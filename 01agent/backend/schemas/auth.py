from typing import Optional
from pydantic import BaseModel, Field
from db.models import LoginSessionTypes
from .validation import (
    BaseValidationModel, 
    EmailValidationMixin, 
    PasswordValidationMixin, 
    NameValidationMixin
)


class UserBase(BaseValidationModel, NameValidationMixin, EmailValidationMixin):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., max_length=255)


class UserAuth(BaseValidationModel, EmailValidationMixin):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1, max_length=255)
    login_session_type: LoginSessionTypes = LoginSessionTypes.WINDOWS


class UserCreate(UserBase, PasswordValidationMixin):
    password: str = Field(..., min_length=8, max_length=255)
    login_session_type: LoginSessionTypes = LoginSessionTypes.WINDOWS


class UserInfo(UserBase):
    id: str
    image: Optional[str]
    is_email_verified: bool


class Logout(BaseValidationModel):
    access_token: str = Field(..., min_length=10, max_length=2000)


class RefreshToken(BaseValidationModel):
    refresh_token: str = Field(..., min_length=10, max_length=2000)


class LoginWithGoogle(BaseValidationModel):
    code: str = Field(..., min_length=10, max_length=1000)
    code_verifier: str = Field(..., min_length=10, max_length=500)
    login_session_type: LoginSessionTypes = LoginSessionTypes.WINDOWS
