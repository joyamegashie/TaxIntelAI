from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
import uvicorn

from config import settings
from database import engine, get_db
from models import Base
from security import limiter, add_security_headers
from routers import auth, businesses, tax_opportunities, geofiscal, policy_simulation

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="TaxIntel AI",
    description="AI-Powered Informal Economy Tax Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    return add_security_headers(response)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(businesses.router, prefix="/api/v1/businesses", tags=["Informal Businesses"])
app.include_router(tax_opportunities.router, prefix="/api/v1/tax-opportunities", tags=["Tax Opportunities"])
app.include_router(geofiscal.router, prefix="/api/v1/geofiscal", tags=["GeoFiscal Intelligence"])
app.include_router(policy_simulation.router, prefix="/api/v1/policy", tags=["Policy Simulation"])

# Health check endpoint
@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    return {"status": "healthy", "message": "TaxIntel AI is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to TaxIntel AI",
        "description": "AI-Powered Informal Economy Tax Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile=None,
        ssl_certfile=None
    )

