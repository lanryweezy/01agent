from fastapi import APIRouter, Depends, status, Request
from utils.limiter import limiter
from sqlmodel import Session
from db.models import User
from schemas.auth import UserInfo, UserCreate, UserAuth, Logout, RefreshToken, LoginWithGoogle
from db.database import get_session
from services.auth_service import AuthService
from dependencies.service_dependencies import get_auth_service, get_google_auth_service, get_token_service, get_email_service
from services.google_auth_service import GoogleAuthService
from services.token_service import TokenService
from utils.procedures import CustomError
from dependencies.auth_dependencies import get_current_user_dependency


router = APIRouter(prefix='/apps/auth', tags=['auth'])


@router.post('/login')
@limiter.limit("5/minute")
async def login_with_email(
    request: Request,
    user_auth: UserAuth, 
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user with email and password."""
    token, refresh_token, user_data = await auth_service.authenticate_user(user_auth)
    
    return {
        'token': token,
        'refresh_token': refresh_token,
        'user': user_data,
    }


@router.post('/login_google_desktop')
async def login_with_google_desktop(
    login_google_obj: LoginWithGoogle,
    google_auth_service: GoogleAuthService = Depends(get_google_auth_service)
):
    """Authenticate user with Google OAuth."""
    token, refresh_token, user_data = await google_auth_service.authenticate_with_google(login_google_obj)
    
    return {
        'token': token,
        'refresh_token': refresh_token,
        'user': user_data,
    }


from sqlmodel.ext.asyncio.session import AsyncSession

@router.get('/user_info')
async def user_info(db: AsyncSession = Depends(get_session), user: User = Depends(get_current_user_dependency)):
    user_data = UserInfo(
        id=user.id,
        name=user.name,
        email=user.email,
        image=user.image,
        is_email_verified=user.is_email_verified,
    )

    return user_data


from services.email_service import EmailService

@router.post('/signup')
@limiter.limit("3/minute")
async def signup(
    request: Request,
    user_create: UserCreate, 
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service)
):
    """Create a new user account."""
    token, refresh_token, user_data = await auth_service.create_user(user_create, email_service)
    
    return {
        'token': token,
        'refresh_token': refresh_token,
        'user': user_data,
    }


@router.post('/logout')
async def logout(
    logout_obj: Logout, 
    token_service: TokenService = Depends(get_token_service)
):
    """Logout user by invalidating session."""
    success = await token_service.logout_user(logout_obj.access_token)
    
    if not success:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            message='Logout failed'
        )
    
    return {'message': 'Successfully logged out'}


@router.post('/refresh_token')
@limiter.limit("10/minute")
async def refresh_current_token(
    request: Request,
    refresh_obj: RefreshToken, 
    token_service: TokenService = Depends(get_token_service)
):
    """Refresh access token using refresh token."""
    new_token, new_refresh = await token_service.refresh_token(refresh_obj.refresh_token)
    
    return {
        'new_token': new_token,
        'new_refresh': new_refresh
    }

@router.get('/verify_email')
async def verify_email(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify user's email."""
    success = await auth_service.verify_email(token)
    if not success:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            message='Invalid or expired verification token'
        )
    return {'message': 'Email verified successfully'}
