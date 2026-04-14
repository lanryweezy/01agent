from secure import Secure
import datetime
from fastapi import FastAPI, Request
from utils.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.middleware.cors import CORSMiddleware
from routers.apps.auth import router as userauth_router
from routers.aiagent.generic import router as aiagent_router
from routers.apps.threads import router as threads_router
from routers.aiagent.suggestor import router as suggestor_aiagent_router
from routers.aiagent.background import router as bg_mode_aiagent_router
from routers.apps.skills import router as skills_router
from utils.procedures import CustomError
from utils.error_handlers import (
    validation_exception_handler,
    custom_exception_handler,
    sqlalchemy_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from prometheus_fastapi_instrumentator import Instrumentator
from utils.profiler import ProfilingMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from config.settings import settings
from config.logging import setup_logging
from services.scheduler_service import automation_scheduler

# Setup logging first
logger = setup_logging()

# Conditionally enable docs based on environment
docs_url = "/docs" if settings.is_development else None
redoc_url = "/redoc" if settings.is_development else None
openapi_url = "/openapi.json" if settings.is_development else None

secure_headers = Secure()

app = FastAPI(
    title='01Agent',
    version="1.0.0",
    description="AI Personal Assistant API",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def add_secure_headers(request: Request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response

# Middleware is processed in the reverse order of how it's added.
# So, the last middleware added is the first to process the request.
# We want CORS to be one of the first to run.

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Add profiling middleware (only in development)
if settings.is_development:
    app.add_middleware(ProfilingMiddleware)

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)


# Register exception handlers
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(CustomError, custom_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


app.include_router(userauth_router)
app.include_router(threads_router)
app.include_router(skills_router)
app.include_router(suggestor_aiagent_router)
app.include_router(bg_mode_aiagent_router)
app.include_router(aiagent_router)




@app.on_event("startup")
async def startup_event():
    automation_scheduler.start()

@app.get('/')
async def index():
    return {'message': datetime.datetime.now()}
