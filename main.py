# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from contextlib import asynccontextmanager
from core.database import initialize_database
from core import constants
from core.exceptions import CustomException
from api.auth.router import auth_router 


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    initialize_database()
    logging.info("🚀 Application startup complete")
    
    yield
    
    # Shutdown
    logging.info("🛑 Application shutdown")


# Initialize FastAPI app
app = FastAPI(
    title= "Agent 2.0",
    description="A full-fledged FastAPI backend application",
    version= "0.1",
    docs_url="/api/docs" if constants.ENV == "development" else None,
    redoc_url="/api/redoc" if constants.ENV == "development" else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[constants.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "localhost:8000",
        "127.0.0.1",
        "127.0.0.1:8000",
        constants.FRONTEND_URL
    ]
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log requests and responses"""
    start_time = time.time()
    
    # Log request
    logging.info(f"📥 {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logging.info(f"📤 {request.method} {request.url} - {response.status_code} - {process_time:.4f}s")
    
    return response


# Exception handler
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    logging.error(f"❌ Custom exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": exc.detail}
    )


# Include API router
app.include_router(auth_router, prefix="/api")