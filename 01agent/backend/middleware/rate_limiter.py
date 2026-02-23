import time
import asyncio
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, str]]:
        async with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Clean old requests
            while self.requests[identifier] and self.requests[identifier][0] < window_start:
                self.requests[identifier].popleft()
            
            # Check if limit exceeded
            current_requests = len(self.requests[identifier])
            if current_requests >= self.max_requests:
                retry_after = str(int(self.requests[identifier][0] + self.window_seconds - now))
                headers = {
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(self.requests[identifier][0] + self.window_seconds)),
                    "Retry-After": retry_after
                }
                return False, headers
            
            # Add current request
            self.requests[identifier].append(now)
            
            headers = {
                "X-RateLimit-Limit": str(self.max_requests),
                "X-RateLimit-Remaining": str(self.max_requests - current_requests - 1),
                "X-RateLimit-Reset": str(int(now + self.window_seconds))
            }
            return True, headers

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.rate_limiter = RateLimiter(max_requests=calls_per_minute, window_seconds=60)
        
        # Different limits for different endpoints
        self.endpoint_limits = {
            "/apps/auth/login": RateLimiter(max_requests=5, window_seconds=60),
            "/apps/auth/signup": RateLimiter(max_requests=3, window_seconds=60),
            "/apps/auth/refresh_token": RateLimiter(max_requests=10, window_seconds=60),
        }
    
    def get_client_identifier(self, request: Request) -> str:
        # Use IP address as identifier, could be enhanced with user ID for authenticated requests
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next):
        client_id = self.get_client_identifier(request)
        path = request.url.path
        
        # Choose appropriate rate limiter
        limiter = self.endpoint_limits.get(path, self.rate_limiter)
        
        # Check rate limit
        allowed, headers = await limiter.is_allowed(client_id)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_id} on {path}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers=headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        for key, value in headers.items():
            response.headers[key] = value
        
        return response