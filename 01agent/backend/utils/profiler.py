import cProfile
import pstats
import io
from functools import wraps
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

def profile_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Print top 20 time-consuming functions
        logger.info(f"Profile for {func.__name__}:\n{s.getvalue()}")
        return result
    return wrapper

class ProfilingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        pr = cProfile.Profile()
        pr.enable()
        response = await call_next(request)
        pr.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Print top 20 time-consuming functions
        
        logger.info(f"Profile for {request.method} {request.url.path}:\n{s.getvalue()}")
        
        return response