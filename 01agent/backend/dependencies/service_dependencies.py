from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from db.database import get_session
from services.auth_service import AuthService
from services.google_auth_service import GoogleAuthService
from services.token_service import TokenService
from services.email_service import EmailService

def get_auth_service(db: AsyncSession = Depends(get_session)) -> AuthService:
    """Dependency to get AuthService instance."""
    return AuthService(db)

def get_google_auth_service(db: AsyncSession = Depends(get_session)) -> GoogleAuthService:
    """Dependency to get GoogleAuthService instance."""
    return GoogleAuthService(db)

def get_token_service(db: AsyncSession = Depends(get_session)) -> TokenService:
    """Dependency to get TokenService instance."""
    return TokenService(db)

def get_email_service() -> EmailService:
    """Dependency to get EmailService instance."""
    return EmailService()