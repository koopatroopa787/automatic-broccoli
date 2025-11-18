"""
Enterprise Data Analytics Platform - Main API Entry Point

This module initializes the FastAPI application with all routers, middleware,
and configuration for the analytics platform.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from loguru import logger

from backend.api.config import settings
from backend.api.routers import (
    analytics,
    auth,
    dashboards,
    data_quality,
    data_sources,
    etl,
    ml_models,
    queries,
    reports,
)
from backend.api.database import engine, init_db
from backend.api.middleware import (
    LoggingMiddleware,
    RequestIDMiddleware,
    RateLimitMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan context manager.

    Handles startup and shutdown events for the application.
    """
    # Startup
    logger.info("Starting Enterprise Data Analytics Platform...")

    # Initialize database
    await init_db()
    logger.info("Database initialized successfully")

    # Additional startup tasks
    logger.info(f"API Version: {settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    yield

    # Shutdown
    logger.info("Shutting down Enterprise Data Analytics Platform...")
    await engine.dispose()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Enterprise-grade Data Analytics & Business Intelligence Platform. "
        "Provides comprehensive APIs for data ingestion, processing, analysis, "
        "and visualization."
    ),
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add custom middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(
    data_sources.router, prefix=f"{settings.API_PREFIX}/data-sources", tags=["Data Sources"]
)
app.include_router(etl.router, prefix=f"{settings.API_PREFIX}/etl", tags=["ETL Pipelines"])
app.include_router(queries.router, prefix=f"{settings.API_PREFIX}/queries", tags=["Queries"])
app.include_router(
    analytics.router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"]
)
app.include_router(
    ml_models.router, prefix=f"{settings.API_PREFIX}/ml-models", tags=["ML Models"]
)
app.include_router(
    dashboards.router, prefix=f"{settings.API_PREFIX}/dashboards", tags=["Dashboards"]
)
app.include_router(reports.router, prefix=f"{settings.API_PREFIX}/reports", tags=["Reports"])
app.include_router(
    data_quality.router, prefix=f"{settings.API_PREFIX}/data-quality", tags=["Data Quality"]
)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "docs": f"{settings.API_PREFIX}/docs",
        "metrics": "/metrics",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get(f"{settings.API_PREFIX}/ping", tags=["Health"])
async def ping() -> dict:
    """Simple ping endpoint."""
    return {"message": "pong"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
