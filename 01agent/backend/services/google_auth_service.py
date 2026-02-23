import aiohttp
from typing import Tuple, Dict, Any
from fastapi import status
from sqlmodel import Session, select
from db.models import User
from schemas.auth import LoginWithGoogle
from utils.auth_helper import create_login_session, create_token_from_user
from utils.datetime_utils import utc_now
from utils import constants
from utils.procedures import CustomError
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class GoogleAuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def authenticate_with_google(self, login_data: LoginWithGoogle) -> Tuple[str, str, dict]:
        """Authenticate user with Google OAuth."""
        try:
            # Exchange authorization code for access token
            access_token = await self._exchange_code_for_token(login_data)
            
            # Get user info from Google
            google_user = await self._get_google_user_info(access_token)
            
            # Find or create user
            user = await self._find_or_create_user(google_user, access_token)
            
            # Create login session and tokens
            exp = utc_now() + constants.ACCESS_TOKEN_LIFETIME_DELTA
            login_session = create_login_session(user, self.db, exp, login_data.login_session_type)
            token, refresh_token = create_token_from_user(user, exp, login_session.id)
            
            user_info = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'image': user.image,
                'is_email_verified': user.is_email_verified,
            }
            
            logger.info(f"Google authentication successful for user: {user.email}")
            return token, refresh_token, user_info
            
        except CustomError:
            raise
        except Exception as e:
            logger.error(f"Google authentication error: {e}")
            raise CustomError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Google authentication failed'
            )
    
    async def _exchange_code_for_token(self, login_data: LoginWithGoogle) -> str:
        """Exchange authorization code for access token."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": login_data.code,
                        "client_id": settings.google_login_client_id,
                        "client_secret": settings.google_login_client_secret,
                        "redirect_uri": settings.google_login_desktop_redirect_uri,
                        "grant_type": "authorization_code",
                        "code_verifier": login_data.code_verifier,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token exchange failed: {response.status} - {error_text}")
                        raise CustomError(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            message="Failed to exchange authorization code"
                        )
                    
                    tokens = await response.json()
                    return tokens["access_token"]
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error during token exchange: {e}")
            raise CustomError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Network error during Google authentication"
            )
    
    async def _get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    headers={'Authorization': f'Bearer {access_token}'},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Google user info request failed: {response.status} - {error_text}")
                        raise CustomError(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            message="Invalid Google token"
                        )
                    
                    return await response.json()
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error getting Google user info: {e}")
            raise CustomError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Network error during Google authentication"
            )
    
    async def _find_or_create_user(self, google_user: Dict[str, Any], access_token: str) -> User:
        """Find existing user or create new one from Google user data."""
        try:
            sub = google_user['sub']
            name = google_user['name']
            email = google_user['email']
            
            # Try to find user by Google ID first
            user = self.db.exec(
                select(User).where(User.google_user_id == sub)
            ).first()
            
            if not user:
                # Try to find user by email
                user = self.db.exec(
                    select(User).where(User.email == email)
                ).first()
                
                if user:
                    # Link existing user to Google account
                    user.google_user_id = sub
                    user.google_token = access_token
                    user.is_email_verified = True
                    
                    self.db.add(user)
                    self.db.commit()
                    self.db.refresh(user)
                    logger.info(f"Linked existing user to Google: {email}")
                else:
                    # Create new user
                    user = User(
                        name=name,
                        email=email,
                        google_user_id=sub,
                        google_token=access_token,
                        is_email_verified=True
                    )
                    self.db.add(user)
                    self.db.commit()
                    self.db.refresh(user)
                    logger.info(f"Created new user from Google: {email}")
            else:
                # Update existing Google user's token
                user.google_token = access_token
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
            
            return user
            
        except Exception as e:
            logger.error(f"Error finding/creating user: {e}")
            self.db.rollback()
            raise CustomError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to process user account"
            )