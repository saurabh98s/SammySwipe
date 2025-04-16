from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..core.config import get_settings
from ..models.user import UserCreate, Token, UserResponse
from ..services.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from ..services.ml_integration import ml_service
from ..db.database import db
from typing import Any

settings = get_settings()
router = APIRouter()

@router.post("/auth/register", response_model=UserResponse)
async def register(user_in: UserCreate) -> Any:
    # Check if user exists
    query = """
    MATCH (u:User {email: $email}) RETURN u
    """
    result = db.execute_query(query, {"email": user_in.email})
    if result:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # Check for potential fraud
    user_data = user_in.dict()
    if ml_service.check_fraud(user_data):
        raise HTTPException(
            status_code=400,
            detail="Registration blocked due to suspicious activity"
        )
    
    # Create user
    hashed_password = get_password_hash(user_in.password)
    query = """
    CREATE (u:User {
        email: $email,
        username: $username,
        full_name: $full_name,
        hashed_password: $hashed_password,
        gender: $gender,
        birth_date: $birth_date,
        bio: $bio,
        interests: $interests,
        location: $location,
        profile_photo: $profile_photo,
        created_at: datetime(),
        updated_at: datetime(),
        is_active: true,
        is_verified: false,
        login_frequency: 0,
        profile_updates: 0,
        reported_count: 0,
        suspicious_login_count: 0
    })
    RETURN u
    """
    
    user_data = user_in.dict()
    user_data["hashed_password"] = hashed_password
    
    result = db.execute_query(query, user_data)
    
    # Analyze user metadata
    metadata = ml_service.analyze_user(user_data)
    
    # Update user with metadata
    if metadata:
        update_query = """
        MATCH (u:User {email: $email})
        SET u.metadata = $metadata
        """
        db.execute_query(
            update_query,
            {
                "email": user_data["email"],
                "metadata": metadata
            }
        )
    
    return UserResponse(**result[0]["u"])

@router.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    query = """
    MATCH (u:User {email: $email})
    RETURN u
    """
    result = db.execute_query(query, {"email": form_data.username})
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = result[0]["u"]
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Update login frequency
    update_query = """
    MATCH (u:User {email: $email})
    SET u.login_frequency = coalesce(u.login_frequency, 0) + 1,
        u.last_login = datetime()
    """
    db.execute_query(update_query, {"email": user["email"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    } 