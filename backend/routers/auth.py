from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_db
from models import User
from schemas import UserCreate, User as UserSchema, Token
from auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from config import settings
from security import limiter, sanitize_input

router = APIRouter()

@router.post("/register", response_model=UserSchema)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Sanitize inputs
    username = sanitize_input(user.username)
    email = sanitize_input(user.email)
    
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    username = sanitize_input(form_data.username)
    
    user = authenticate_user(db, username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/refresh")
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

