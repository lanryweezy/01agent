import pytest
from pydantic import ValidationError
from schemas.auth import UserCreate, UserAuth
from schemas.threads import CreateThread, UpdateThread, SendMessageObj

class TestValidationSchemas:
    """Test validation schemas."""
    
    def test_user_create_valid(self):
        """Test valid user creation data."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "SecurePassword123!"
        }
        user = UserCreate(**data)
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
    
    def test_user_create_invalid_email(self):
        """Test user creation with invalid email."""
        data = {
            "name": "John Doe",
            "email": "invalid-email",
            "password": "SecurePassword123!"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("Invalid email format" in str(error) for error in errors)
    
    def test_user_create_weak_password(self):
        """Test user creation with weak password."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "weak"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("Password must be at least 8 characters long" in str(error) for error in errors)
    
    def test_user_create_password_no_uppercase(self):
        """Test password validation - no uppercase."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "lowercase123!"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("uppercase letter" in str(error) for error in errors)
    
    def test_user_create_password_no_digit(self):
        """Test password validation - no digit."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "NoDigitsHere!"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("digit" in str(error) for error in errors)
    
    def test_user_create_password_no_special_char(self):
        """Test password validation - no special character."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "NoSpecialChar123"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("special character" in str(error) for error in errors)
    
    def test_user_create_empty_name(self):
        """Test user creation with empty name."""
        data = {
            "name": "",
            "email": "john@example.com",
            "password": "SecurePassword123!"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("Name cannot be empty" in str(error) for error in errors)
    
    def test_user_create_name_too_short(self):
        """Test user creation with name too short."""
        data = {
            "name": "A",
            "email": "john@example.com",
            "password": "SecurePassword123!"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("at least 2 characters" in str(error) for error in errors)
    
    def test_user_create_name_invalid_characters(self):
        """Test user creation with invalid characters in name."""
        data = {
            "name": "John123",
            "email": "john@example.com",
            "password": "SecurePassword123!"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("letters, spaces, hyphens, and apostrophes" in str(error) for error in errors)
    
    def test_create_thread_valid(self):
        """Test valid thread creation."""
        data = {
            "task": "This is a valid task description for automation"
        }
        thread = CreateThread(**data)
        assert thread.task == "This is a valid task description for automation"
        assert thread.background_mode is False
        assert thread.extended_thinking_mode is False
    
    def test_create_thread_task_too_short(self):
        """Test thread creation with task too short."""
        data = {
            "task": "Hi"
        }
        with pytest.raises(ValidationError) as exc_info:
            CreateThread(**data)
        
        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(error) for error in errors)
    
    def test_create_thread_task_too_long(self):
        """Test thread creation with task too long."""
        data = {
            "task": "A" * 5001  # Exceeds 5000 character limit
        }
        with pytest.raises(ValidationError) as exc_info:
            CreateThread(**data)
        
        errors = exc_info.value.errors()
        assert any("cannot exceed 5000 characters" in str(error) for error in errors)
    
    def test_create_thread_dangerous_content(self):
        """Test thread creation with potentially dangerous content."""
        data = {
            "task": "Execute this <script>alert('xss')</script> task"
        }
        with pytest.raises(ValidationError) as exc_info:
            CreateThread(**data)
        
        errors = exc_info.value.errors()
        assert any("potentially dangerous content" in str(error) for error in errors)
    
    def test_update_thread_valid(self):
        """Test valid thread update."""
        data = {
            "title": "Updated Thread Title"
        }
        thread_update = UpdateThread(**data)
        assert thread_update.title == "Updated Thread Title"
    
    def test_update_thread_title_too_long(self):
        """Test thread update with title too long."""
        data = {
            "title": "A" * 201  # Exceeds 200 character limit
        }
        with pytest.raises(ValidationError) as exc_info:
            UpdateThread(**data)
        
        errors = exc_info.value.errors()
        assert any("cannot exceed 200 characters" in str(error) for error in errors)
    
    def test_send_message_valid(self):
        """Test valid message sending."""
        data = {
            "text": "This is a valid message for the AI agent"
        }
        message = SendMessageObj(**data)
        assert message.text == "This is a valid message for the AI agent"
        assert message.background_mode is False
        assert message.extended_thinking_mode is False
    
    def test_send_message_empty_text(self):
        """Test message sending with empty text."""
        data = {
            "text": ""
        }
        with pytest.raises(ValidationError) as exc_info:
            SendMessageObj(**data)
        
        errors = exc_info.value.errors()
        assert any("cannot be empty" in str(error) for error in errors)
    
    def test_user_auth_valid(self):
        """Test valid user authentication data."""
        data = {
            "email": "user@example.com",
            "password": "password123"
        }
        auth = UserAuth(**data)
        assert auth.email == "user@example.com"
        assert auth.password == "password123"
    
    def test_user_auth_invalid_email(self):
        """Test user authentication with invalid email."""
        data = {
            "email": "not-an-email",
            "password": "password123"
        }
        with pytest.raises(ValidationError) as exc_info:
            UserAuth(**data)
        
        errors = exc_info.value.errors()
        assert any("Invalid email format" in str(error) for error in errors)