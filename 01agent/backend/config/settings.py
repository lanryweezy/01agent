import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import secrets

class Settings(BaseSettings):
    # Environment
    environment: str = "production"
    
    # Database
    db_host: str
    db_port: int = 5432
    db_database: str
    db_username: str
    db_password: str
    db_connection_string: Optional[str] = None
    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    
    # Security
    jwt_iss: str = "01AgentBackend"
    jwt_secret: str
    session_secret: Optional[str] = None
    allowed_hosts: str = "localhost,127.0.0.1"
    cors_origins: str = "http://localhost:6763,http://127.0.0.1:6763,file://"
    
    # Redis
    redis_connection: Optional[str] = None
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Google OAuth
    google_login_client_id: Optional[str] = None
    google_login_client_secret: Optional[str] = None
    google_login_desktop_redirect_uri: str = "http://127.0.0.1:36478"
    
    # AWS
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    bedrock_region: str = "us-west-2"
    
    # Azure
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    openai_api_version: str = "2024-12-01-preview"
    
    # Ollama
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model_name: str = "claude-3-7-sonnet-latest"

    # Agent-specific LLM configurations
    planner_agent_model_type: str = "openai"
    planner_agent_model_id: str = "gpt-4o"

    suggestor_agent_model_type: str = "openai"
    suggestor_agent_model_id: str = "gpt-4o-mini"

    computer_use_agent_model_type: str = "anthropic"
    computer_use_agent_model_id: str = "claude-3-7-sonnet-latest" # Multimodal model

    classifier_agent_model_type: str = "openai"
    classifier_agent_model_id: str = "gpt-4o-mini"

    title_agent_model_type: str = "openai"
    title_agent_model_id: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @validator('jwt_secret')
    def validate_jwt_secret(cls, v):
        if not v:
            raise ValueError('JWT_SECRET is required')
        if len(v) < 32:
            raise ValueError('JWT_SECRET must be at least 32 characters long')
        return v
    
    @validator('session_secret', pre=True, always=True)
    def validate_session_secret(cls, v):
        if not v:
            return secrets.token_urlsafe(32)
        if len(v) < 32:
            raise ValueError('SESSION_SECRET must be at least 32 characters long')
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('ENVIRONMENT must be one of: development, staging, production')
        return v
    
    @property
    def database_url(self) -> str:
        if self.db_connection_string:
            return self.db_connection_string
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_database}"
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.allowed_hosts.split(',')]

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(',')]
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

# Global settings instance
settings = Settings()