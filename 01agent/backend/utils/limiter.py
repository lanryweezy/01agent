from slowapi import Limiter
from slowapi.util import get_remote_address
from config.settings import settings
from db.database import redis_client

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_connection,
    storage_options={"client": redis_client} if redis_client else {},
    default_limits=["100/minute"]
)
