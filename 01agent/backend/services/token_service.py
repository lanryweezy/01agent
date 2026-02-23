import datetime
from typing import Tuple, Optional
from sqlmodel import Session, select
from fastapi import status
from db.models import User, LoginSession
from utils.auth_helper import decode_token, is_session_valid, create_token_from_user
from utils.datetime_utils import utc_now
from utils import constants
from utils.procedures import CustomError
import logging

logger = logging.getLogger(__name__)

class TokenService:
    def __init__(self, db: Session):
        self.db = db
    
    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh access token using refresh token."""
        try:
            # Decode refresh token
            payload = decode_token(refresh_token)
            
            if payload.get('token_type') != 'refresh':
                raise CustomError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message='Invalid token type'
                )
            
            session_id = payload.get('session_id')
            if not is_session_valid(session_id, self.db):
                raise CustomError(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='Invalid or expired session'
                )
            
            # Get user and session
            user = self.db.exec(
                select(User).where(User.id == payload.get('user_id'))
            ).first()
            
            if not user:
                raise CustomError(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='User not found'
                )
            
            login_session = self.db.exec(
                select(LoginSession).where(LoginSession.id == session_id)
            ).first()
            
            if not login_session:
                raise CustomError(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='Session not found'
                )
            
            # Check if refresh token is close to expiry
            exp = payload.get('exp')
            time_until_expiry = datetime.datetime.fromtimestamp(exp) - datetime.datetime.now()
            should_refresh_refresh_token = time_until_expiry <= datetime.timedelta(hours=1)
            
            # Generate new tokens
            new_exp = utc_now() + constants.ACCESS_TOKEN_LIFETIME_DELTA
            new_token, new_refresh = create_token_from_user(
                user, 
                new_exp, 
                login_session.id, 
                should_refresh_refresh_token
            )
            
            # Update session expiry
            login_session.expires_at = new_exp
            if should_refresh_refresh_token:
                login_session.refresh_expires_at = utc_now() + constants.REFRESH_TOKEN_LIFETIME_DELTA
            
            self.db.add(login_session)
            self.db.commit()
            self.db.refresh(login_session)
            
            logger.info(f"Token refreshed for user: {user.email}")
            
            return new_token, new_refresh
            
        except CustomError:
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise CustomError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Token refresh failed'
            )
    
    async def logout_user(self, access_token: str) -> bool:
        """Logout user by invalidating session."""
        try:
            # Decode access token
            payload = decode_token(access_token)
            
            if payload.get('token_type') != 'access':
                raise CustomError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message='Invalid token type'
                )
            
            session_id = payload.get('session_id')
            if not is_session_valid(session_id, self.db):
                raise CustomError(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='Invalid or expired session'
                )
            
            # Mark session as logged out
            login_session = self.db.exec(
                select(LoginSession).where(LoginSession.id == session_id)
            ).first()
            
            if login_session:
                login_session.is_logged_out = True
                self.db.add(login_session)
                self.db.commit()
                logger.info(f"User logged out: session {session_id}")
                return True
            
            return False
            
        except CustomError:
            raise
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            self.db.rollback()
            raise CustomError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Logout failed'
            )
    
    async def validate_token(self, token: str) -> Optional[dict]:
        """Validate token and return payload if valid."""
        try:
            payload = decode_token(token)
            session_id = payload.get('session_id')
            
            if not is_session_valid(session_id, self.db):
                return None
            
            return payload
            
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            return None