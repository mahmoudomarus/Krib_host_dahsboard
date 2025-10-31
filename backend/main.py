"""
RentalAI FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import redis_client
from app.core.monitoring import init_sentry, metrics_middleware, metrics_endpoint, health_check_with_metrics
from app.core.rate_limiter import limiter, custom_rate_limit_handler
from app.api.routes import auth, properties, bookings, analytics, upload, financials, users, locations, external, webhooks, notifications, sse, stripe_connect, payments, payouts, stripe_webhooks, external_payments
from app.core.supabase_client import supabase_client
from slowapi.errors import RateLimitExceeded

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Krib AI Backend...")
    
    # Initialize Sentry error tracking
    init_sentry()
    print("✅ Sentry error tracking initialized")
    
    await init_db()
    print("✅ Database initialized")
    
    # Initialize Redis
    await redis_client.connect()
    if redis_client.is_connected:
        print("✅ Redis cache connected")
    else:
        print("⚠️ Redis cache unavailable - running without cache")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Krib AI Backend...")
    
    # Cancel all SSE connections gracefully
    try:
        from app.api.routes.sse import sse_manager
        await sse_manager.shutdown_all_connections()
        print("✅ SSE connections closed")
    except Exception as e:
        print(f"⚠️ Error closing SSE connections: {e}")
    
    await redis_client.disconnect()
    print("✅ Redis connection closed")

app = FastAPI(
    title="Krib AI API",
    description="Krib AI - AI-Powered Property Rental Management Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware Configuration

# Simple HTTPS redirect fix for Render
@app.middleware("http")
async def https_fix_middleware(request, call_next):
    """Simple fix for HTTPS behind proxy"""
    response = await call_next(request)
    
    # Fix any HTTP redirects to HTTPS
    if "location" in response.headers:
        location = response.headers["location"]
        if "onrender.com" in location and location.startswith("http://"):
            response.headers["location"] = location.replace("http://", "https://")
    
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173", 
        "https://krib-host-dahsboard.vercel.app",
        "https://krib.ai",
        "https://*.krib.ai",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics and monitoring
app.middleware("http")(metrics_middleware)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])
app.include_router(properties.router, prefix="/api/properties", tags=["properties"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(financials.router, prefix="/api/financials", tags=["financials"])

# External API for third-party integrations (AI platforms)
app.include_router(external.router, prefix="/api", tags=["external-api"])

# Webhook management endpoints
app.include_router(webhooks.router, prefix="/api", tags=["webhooks"])

# Host notification endpoints
app.include_router(notifications.router, prefix="/api", tags=["notifications"])

# Server-Sent Events for real-time updates
app.include_router(sse.router, prefix="/api", tags=["sse"])

# Stripe Connect and payment endpoints
app.include_router(stripe_connect.router, prefix="/api/v1/stripe", tags=["stripe-connect"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(payouts.router, prefix="/api/v1/payouts", tags=["payouts"])
app.include_router(stripe_webhooks.router, prefix="/api/v1/stripe", tags=["stripe-webhooks"])
app.include_router(external_payments.router, prefix="/api/external", tags=["external-payments"])

@app.get("/")
async def root():
    return {
        "message": "RentalAI API is running! 🏠✨",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
@app.head("/health")
async def health_check():
    """Enhanced health check with monitoring"""
    try:
        return await health_check_with_metrics()
    except Exception as e:
        # Fallback health check if monitoring fails
        return {"status": "ok", "message": "Service is running", "timestamp": datetime.utcnow().isoformat()}

@app.get("/healthz")
@app.head("/healthz")
async def simple_health():
    """Simple health check for container orchestrators"""
    return {"status": "ok"}

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return await metrics_endpoint()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
