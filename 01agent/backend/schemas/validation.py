import re
from typing import Optional
from pydantic import BaseModel, validator, Field
from email_validator import validate_email, EmailNotValidError

class BaseValidationModel(BaseModel):
    """Base model with common validation utilities."""
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True

class EmailValidationMixin:
    """Mixin for email validation."""
    
    @validator('email')
    def validate_email_format(cls, v):
        try:
            validate_email(v)
            return v.lower()
        except EmailNotValidError:
            raise ValueError('Invalid email format')

class PasswordValidationMixin:
    """Mixin for password validation."""
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v

class NameValidationMixin:
    """Mixin for name validation."""
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        
        if len(v.strip()) > 100:
            raise ValueError('Name cannot exceed 100 characters')
        
        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", v.strip()):
            raise ValueError('Name can only contain letters, spaces, hyphens, and apostrophes')
        
        return v.strip()

class TaskValidationMixin:
    """Mixin for task text validation."""
    
    @validator('task', 'text', allow_reuse=True)
    def validate_task_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Task description cannot be empty')
        
        if len(v.strip()) < 3:
            raise ValueError('Task description must be at least 3 characters long')
        
        if len(v.strip()) > 5000:
            raise ValueError('Task description cannot exceed 5000 characters')
        
        # Basic XSS prevention
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE | re.DOTALL):
                raise ValueError('Task description contains potentially dangerous content')
        
        return v.strip()

class ThreadValidationMixin:
    """Mixin for thread validation."""
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        
        if len(v.strip()) < 1:
            raise ValueError('Title must be at least 1 character long')
        
        if len(v.strip()) > 200:
            raise ValueError('Title cannot exceed 200 characters')
        
        return v.strip()

class UUIDValidationMixin:
    """Mixin for UUID validation."""
    
    @validator('tid', 'thread_id', 'user_id', allow_reuse=True)
    def validate_uuid_format(cls, v):
        if not v:
            raise ValueError('ID cannot be empty')
        
        # Basic alphanumeric check for custom IDs
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid ID format')
        
        if len(v) < 10 or len(v) > 50:
            raise ValueError('ID must be between 10 and 50 characters')
        
        return v