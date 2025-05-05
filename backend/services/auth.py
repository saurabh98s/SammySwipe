from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..core.config import get_settings
from ..models.user import TokenData, UserInDB
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from ..db.database import db
import os

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), request: Request = None) -> UserInDB:
    # Check if we're in development/superadmin mode
    superadmin_mode = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"
    
    if superadmin_mode:
        # Return a superadmin user with all privileges
        return UserInDB(
            id="superadmin-id",
            email="superadmin@sammyswipe.com",
            username="superadmin",
            full_name="Super Admin",
            hashed_password="",
            is_active=True,
            is_verified=True,
            birth_date=datetime.now() - timedelta(days=365*30),
            gender="other",
            interests=["admin", "debugging"],
            bio="System administrator",
            location="Server",
            profile_photo="https://example.com/admin.jpg",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    if token is None:
        # For development or testing, create a default test user
        return UserInDB(
            id="test-user-id",
            email="test@sammyswipe.com",
            username="testuser",
            full_name="Test User",
            hashed_password="",
            is_active=True,
            is_verified=True,
            birth_date=datetime.now() - timedelta(days=365*25),
            gender="other",
            interests=["testing", "debugging"],
            bio="Test user for development",
            location="Test Location",
            profile_photo="https://example.com/test.jpg",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    query = """
    MATCH (u:User {email: $email})
    RETURN u
    """
    result = db.execute_query(query, {"email": token_data.email})
    
    if not result:
        raise credentials_exception
        
    user_data = result[0]["u"]
    return UserInDB(**user_data)

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 