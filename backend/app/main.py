import secrets
from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from uvicorn import run
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html

from app.logger import logger
from app.core.config import settings
from app.middleware.log_middleware import log_request_middleware
from app.common.exception_handler import (
    request_validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.db.mongodb import get_client
from app.db.redis import get_redis, close_redis
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")

    # ---- MongoDB ----
    mongo_client = get_client()
    await mongo_client.admin.command("ping")
    logger.info("MongoDB connected")

    # ---- Redis ----
    redis_client = get_redis()
    await redis_client.ping()
    logger.info("Redis connected")

    yield  # App runs here

    # ---- Shutdown ----
    await close_redis()

    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")

    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

security = HTTPBasic()

# Add SessionMiddleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

app.middleware("http")(log_request_middleware)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Includ all routers
app.include_router(api_router, prefix=settings.API_V1_STR)

def get_current_username(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> str:
    correct_username = secrets.compare_digest(credentials.username.encode(), settings.DOC_ROOT_USERNAME.encode())
    correct_password = secrets.compare_digest(credentials.password.encode(), settings.DOC_ROOT_PASSWORD.encode())
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_schema(username: str = Depends(get_current_username)):
    return get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.PROJECT_DESCRIPTION,
        routes=app.routes,
    )


# Add Authentication to Swagger Docs and Redoc
@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.PROJECT_NAME} - API Documentation",
    )


@app.get("/api/health", summary="Health Check", tags=["System"])
async def health_check():
    mongo_client = get_client()
    redis_client = get_redis()

    mongo_status = await mongo_client.admin.command("ping")
    redis_status = await redis_client.ping()

    response= {
        "status": "operational",
        "services": {
            "postgres": "ready (async pool)",
            "mongodb": "online" if mongo_status else "offline",
            "redis": "connected" if redis_status else "error",
        },
        "version": settings.VERSION,
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)



if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, log_config=None)