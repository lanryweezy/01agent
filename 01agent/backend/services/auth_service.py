import datetime
from typing import Optional, Tuple
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import status
from db.models import User, UserType, LoginSession, EmailVerificationEntry
from schemas.auth import UserCreate, UserAuth, UserInfo
from services.email_service import EmailService
from utils.security import verify_password, hash_password
from utils.auth_helper import create_login_session, create_token_from_user
from utils.procedures import CustomError
from utils.datetime_utils import utc_now
from utils import constants
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate, email_service: "EmailService") -> Tuple[str, str, dict]:
        """Create a new user and return tokens and user info."""
        try:
            # Check if user already exists
            existing_user = (await self.db.exec(
                select(User).where(User.email == user_data.email)
            )).first()
            
            if existing_user:
                raise CustomError(
                    status_code=status.HTTP_409_CONFLICT,
                    message='Email already registered'
                )
            
            # Hash password
            hashed_password = hash_password(user_data.password)
            
            # Create user
            new_user = User(
                name=user_data.name,
                email=user_data.email,
                password=hashed_password,
            )
            
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            
            logger.info(f"New user created: {new_user.email}")
            
            # Create email verification entry
            verification_entry = EmailVerificationEntry(
                email=new_user.email,
                expires_at=utc_now() + datetime.timedelta(hours=24)
            )
            self.db.add(verification_entry)
            await self.db.commit()
            await self.db.refresh(verification_entry)

            user_info = {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'image': new_user.image,
                'is_email_verified': new_user.is_email_verified,
            }

            # Send verification email
            await email_service.send_verification_email(UserInfo(**user_info), verification_entry.verification_token)
            
            # Create login session and tokens
            exp = utc_now() + constants.ACCESS_TOKEN_LIFETIME_DELTA
            login_session = await create_login_session(new_user, self.db, exp, user_data.login_session_type)
            token, refresh_token = create_token_from_user(new_user, exp, login_session.id)
            
            return token, refresh_token, user_info
            
        except CustomError:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            await self.db.rollback()
            raise CustomError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Failed to create user'
            )
    
    async def authenticate_user(self, auth_data: UserAuth) -> Tuple[str, str, dict]:
        """Authenticate user and return tokens and user info."""
        try:
            # Find user
            user = (await self.db.exec(
                select(User).where(User.email == auth_data.email)
            )).first()
            
            if not user or not user.password or not verify_password(auth_data.password, user.password):
                raise CustomError(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='Invalid email or password'
                )
            
            if user.user_type != UserType.NORMAL_USER:
                raise CustomError(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    message='Invalid user type'
                )
            
            if user.is_blocked:
                raise CustomError(
                    status_code=status.HTTP_403_FORBIDDEN,
                    message='Account is blocked'
                )
            
            logger.info(f"User authenticated: {user.email}")
            
            # Create login session and tokens
            exp = utc_now() + constants.ACCESS_TOKEN_LIFETIME_DELTA
            login_session = await create_login_session(user, self.db, exp, auth_data.login_session_type)
            token, refresh_token = create_token_from_user(user, exp, login_session.id)
            
            user_info = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'image': user.image,
                'is_email_verified': user.is_email_verified,
            }
            
            return token, refresh_token, user_info
            
        except CustomError:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise CustomError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Authentication failed'
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            return (await self.db.exec(
                select(User).where(User.id == user_id)
            )).first()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def logout_user(self, session_id: int) -> bool:
        """Logout user by marking session as logged out."""
        try:
            login_session = (await self.db.exec(
                select(LoginSession).where(LoginSession.id == session_id)
            )).first()
            
            if login_session:
                login_session.is_logged_out = True
                self.db.add(login_session)
                await self.db.commit()
                logger.info(f"User logged out: session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            await self.db.rollback()
            return False

    async def verify_email(self, token: str) -> bool:
        """Verify user's email with a token."""
        try:
            verification_entry = (await self.db.exec(
                select(EmailVerificationEntry).where(EmailVerificationEntry.verification_token == token)
            )).first()

            if not verification_entry or verification_entry.expires_at < utc_now():
                return False

            user = (await self.db.exec(
                select(User).where(User.email == verification_entry.email)
            )).first()

            if not user:
                return False

            user.is_email_verified = True
            self.db.add(user)
            await self.db.commit()
            logger.info(f"Email verified for user: {user.email}")
            
            # Optionally, delete the verification entry after use
            await self.db.delete(verification_entry)
            await self.db.commit()

            return True

        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            await self.db.rollback()
            return False