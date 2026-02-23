from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from redis import Redis
from functools import wraps
import json
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

# Redis configuration
redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True
) if settings.redis_connection else None

def cache_decorator(prefix: str, ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not redis_client:
                # No Redis available, execute function directly
                return await func(*args, **kwargs)
            
            try:
                # Generate cache key
                key = f"{prefix}:{json.dumps(args)}:{json.dumps(kwargs)}"
                
                # Try to get from cache
                cached = redis_client.get(key)
                if cached:
                    return json.loads(cached)
                
                # Get from function
                result = await func(*args, **kwargs)
                
                # Store in cache
                redis_client.setex(key, ttl, json.dumps(result))
                
                return result
            except Exception as e:
                logger.warning(f"Cache operation failed: {e}")
                # Fallback to direct function execution
                return await func(*args, **kwargs)
        return wrapper
    return decorator

from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from redis import Redis
from functools import wraps
import json
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

# Redis configuration
redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True
) if settings.redis_connection else None

def cache_decorator(prefix: str, ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not redis_client:
                # No Redis available, execute function directly
                return await func(*args, **kwargs)
            
            try:
                # Generate cache key
                key = f"{prefix}:{json.dumps(args)}:{json.dumps(kwargs)}"
                
                # Try to get from cache
                cached = redis_client.get(key)
                if cached:
                    return json.loads(cached)
                
                # Get from function
                result = await func(*args, **kwargs)
                
                # Store in cache
                redis_client.setex(key, ttl, json.dumps(result))
                
                return result
            except Exception as e:
                logger.warning(f"Cache operation failed: {e}")
                # Fallback to direct function execution
                return await func(*args, **kwargs)
        return wrapper
    return decorator

engine = AsyncEngine(create_engine(
    settings.database_url,
    echo=settings.is_development,  # Enable SQL logging only in development
    poolclass=QueuePool,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,
    pool_reset_on_return='commit',
    connect_args={
        "options": "-c timezone=utc"  # Ensure UTC timezone
    }
))

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
