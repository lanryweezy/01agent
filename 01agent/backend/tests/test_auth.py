import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import Session
from db.models import User
from services.auth_service import AuthService
from utils.security import hash_password

class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_signup_success(self, client: TestClient, sample_user_data):
        """Test successful user signup."""
        response = client.post("/apps/auth/signup", json=sample_user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == sample_user_data["email"]
        assert data["user"]["name"] == sample_user_data["name"]
        assert data["user"]["is_email_verified"] is False
    
    def test_signup_duplicate_email(self, client: TestClient, sample_user_data):
        """Test signup with duplicate email."""
        # First signup
        client.post("/apps/auth/signup", json=sample_user_data)
        
        # Second signup with same email
        response = client.post("/apps/auth/signup", json=sample_user_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "Email already registered" in data["message"]
    
    def test_signup_invalid_email(self, client: TestClient, sample_user_data):
        """Test signup with invalid email."""
        sample_user_data["email"] = "invalid-email"
        response = client.post("/apps/auth/signup", json=sample_user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_signup_weak_password(self, client: TestClient, sample_user_data):
        """Test signup with weak password."""
        sample_user_data["password"] = "weak"
        response = client.post("/apps/auth/signup", json=sample_user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client: TestClient, sample_user_data, sample_login_data):
        """Test successful login."""
        # First create user
        client.post("/apps/auth/signup", json=sample_user_data)
        
        # Then login
        response = client.post("/apps/auth/login", json=sample_login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == sample_login_data["email"]
    
    def test_login_invalid_credentials(self, client: TestClient, sample_login_data):
        """Test login with invalid credentials."""
        response = client.post("/apps/auth/login", json=sample_login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid email or password" in data["message"]
    
    def test_login_wrong_password(self, client: TestClient, sample_user_data, sample_login_data):
        """Test login with wrong password."""
        # Create user
        client.post("/apps/auth/signup", json=sample_user_data)
        
        # Login with wrong password
        sample_login_data["password"] = "WrongPassword123!"
        response = client.post("/apps/auth/login", json=sample_login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_user_info_authenticated(self, client: TestClient, sample_user_data):
        """Test getting user info when authenticated."""
        # Create user and get token
        signup_response = client.post("/apps/auth/signup", json=sample_user_data)
        token = signup_response.json()["token"]
        
        # Get user info
        response = client.get(
            "/apps/auth/user_info",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["name"] == sample_user_data["name"]
    
    def test_user_info_unauthenticated(self, client: TestClient):
        """Test getting user info when not authenticated."""
        response = client.get("/apps/auth/user_info")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_success(self, client: TestClient, sample_user_data):
        """Test successful logout."""
        # Create user and get token
        signup_response = client.post("/apps/auth/signup", json=sample_user_data)
        token = signup_response.json()["token"]
        
        # Logout
        response = client.post(
            "/apps/auth/logout",
            json={"access_token": token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Successfully logged out" in data["message"]
    
    def test_refresh_token_success(self, client: TestClient, sample_user_data):
        """Test successful token refresh."""
        # Create user and get tokens
        signup_response = client.post("/apps/auth/signup", json=sample_user_data)
        refresh_token = signup_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/apps/auth/refresh_token",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "new_token" in data
        assert "new_refresh" in data

class TestAuthService:
    """Test AuthService class."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, test_session: Session, sample_user_data):
        """Test successful user creation."""
        auth_service = AuthService(test_session)
        
        from schemas.auth import UserCreate
        user_data = UserCreate(**sample_user_data)
        
        token, refresh_token, user_info = await auth_service.create_user(user_data)
        
        assert token is not None
        assert refresh_token is not None
        assert user_info["email"] == sample_user_data["email"]
        assert user_info["name"] == sample_user_data["name"]
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, test_session: Session, sample_user_data):
        """Test successful user authentication."""
        # Create user first
        user = User(
            name=sample_user_data["name"],
            email=sample_user_data["email"],
            password=hash_password(sample_user_data["password"])
        )
        test_session.add(user)
        test_session.commit()
        
        # Authenticate
        auth_service = AuthService(test_session)
        from schemas.auth import UserAuth
        auth_data = UserAuth(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        token, refresh_token, user_info = await auth_service.authenticate_user(auth_data)
        
        assert token is not None
        assert refresh_token is not None
        assert user_info["email"] == sample_user_data["email"]
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, test_session: Session, sample_user_data):
        """Test getting user by ID."""
        # Create user
        user = User(
            name=sample_user_data["name"],
            email=sample_user_data["email"],
            password=hash_password(sample_user_data["password"])
        )
        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)
        
        # Get user by ID
        auth_service = AuthService(test_session)
        retrieved_user = await auth_service.get_user_by_id(user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.email == sample_user_data["email"]
        assert retrieved_user.name == sample_user_data["name"]