import hashlib
import secrets
from cryptography.fernet import Fernet
from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config import settings
import time
from typing import Dict

# Rate limiting
limiter = Limiter(key_func=get_remote_address)


# Encryption utilities
def generate_encryption_key() -> str:
    """Generate a new encryption key"""
    return Fernet.generate_key().decode()


def encrypt_data(data: str, key: str = None) -> str:
    """Encrypt sensitive data"""
    if key is None:
        key = settings.encryption_key

    if isinstance(key, str):
        key = key.encode()

    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data.decode()


def decrypt_data(encrypted_data: str, key: str = None) -> str:
    """Decrypt sensitive data"""
    if key is None:
        key = settings.encryption_key

    if isinstance(key, str):
        key = key.encode()

    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data.encode())
    return decrypted_data.decode()


def hash_api_key(api_key: str) -> str:
    """Hash API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


# Security headers middleware
def add_security_headers(response):
    """Add security headers to response"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


# Input validation and sanitization
def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not isinstance(input_string, str):
        raise HTTPException(status_code=400, detail="Invalid input type")

    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", "&", '"', "'", "/", "\\"]
    for char in dangerous_chars:
        input_string = input_string.replace(char, "")

    return input_string.strip()


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate geographic coordinates"""
    if not (-90 <= latitude <= 90):
        return False
    if not (-180 <= longitude <= 180):
        return False
    return True


# API key validation
class APIKeyValidator:
    def __init__(self):
        self.valid_keys: Dict[str, Dict] = {}
        self.rate_limits: Dict[str, Dict] = {}

    def add_api_key(self, key: str, permissions: list, rate_limit: int = 1000):
        """Add a valid API key with permissions"""
        hashed_key = hash_api_key(key)
        self.valid_keys[hashed_key] = {
            "permissions": permissions,
            "rate_limit": rate_limit,
            "created_at": time.time(),
        }

    def validate_key(self, key: str) -> bool:
        """Validate an API key"""
        hashed_key = hash_api_key(key)
        return hashed_key in self.valid_keys

    def check_rate_limit(self, key: str) -> bool:
        """Check if API key has exceeded rate limit"""
        hashed_key = hash_api_key(key)
        current_time = time.time()

        if hashed_key not in self.rate_limits:
            self.rate_limits[hashed_key] = {"requests": 1, "window_start": current_time}
            return True

        # Reset window if more than 1 minute has passed
        if current_time - self.rate_limits[hashed_key]["window_start"] > 60:
            self.rate_limits[hashed_key] = {"requests": 1, "window_start": current_time}
            return True

        # Check if within rate limit
        key_info = self.valid_keys.get(hashed_key, {})
        rate_limit = key_info.get("rate_limit", 1000)

        if self.rate_limits[hashed_key]["requests"] >= rate_limit:
            return False

        self.rate_limits[hashed_key]["requests"] += 1
        return True


# Initialize API key validator
api_key_validator = APIKeyValidator()
