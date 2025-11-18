"""
Custom Middleware

Provides logging, request tracking, rate limiting, and other cross-cutting concerns.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.api.config import settings


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Adds unique request ID to each request for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = getattr(request.state, "request_id", "unknown")
        start_time = time.time()

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exc_info=True,
                extra={"request_id": request_id},
            )
            raise

        # Calculate duration
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 2)

        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {duration_ms}ms",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        response.headers["X-Process-Time"] = str(duration_ms)

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting (use Redis in production)."""

    def __init__(self, app: ASGIApp, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics", "/", f"{settings.API_PREFIX}/ping"]:
            return await call_next(request)

        # Get client identifier
        client_id = request.client.host if request.client else "unknown"

        # Get current time
        current_time = time.time()

        # Initialize or clean up request history for this client
        if client_id not in self.request_counts:
            self.request_counts[client_id] = []

        # Remove old requests outside the window
        self.request_counts[client_id] = [
            req_time
            for req_time in self.request_counts[client_id]
            if current_time - req_time < self.window_seconds
        ]

        # Check if rate limit exceeded
        if len(self.request_counts[client_id]) >= self.max_requests:
            logger.warning(
                f"Rate limit exceeded for client {client_id}",
                extra={"client": client_id, "requests": len(self.request_counts[client_id])},
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": self.window_seconds,
                },
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + self.window_seconds)),
                },
            )

        # Add current request
        self.request_counts[client_id].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = self.max_requests - len(self.request_counts[client_id])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))

        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Adds cache control headers to responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add cache headers for GET requests
        if request.method == "GET":
            # Static/public endpoints can be cached
            if any(
                path in request.url.path
                for path in ["/docs", "/redoc", "/openapi.json", "/static"]
            ):
                response.headers["Cache-Control"] = "public, max-age=3600"
            else:
                # API responses should not be cached by default
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"

        return response
