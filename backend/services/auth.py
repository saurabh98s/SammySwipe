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
from typing import Optional  
from starlette.requests import Request          # make sure this import is present

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

from datetime import datetime, timedelta
import os

# ---------------------------------------------------------------------------
# constants – used both here and in matches.py
# ---------------------------------------------------------------------------
SUPERADMIN_MODE   = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"
SUPERADMIN_DB_ID  = os.getenv("SUPERADMIN_DB_ID",  "00000000-0000-0000-0000-000000admin")
SUPERADMIN_EMAIL  = os.getenv("SUPERADMIN_EMAIL", "superadmin@example.com")
SUPERADMIN_UNAME  = os.getenv("SUPERADMIN_USERNAME", "superadmin")

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
) -> UserInDB:

    # ──────────────────────────────────────────────────────────────────────
    # 1. super-admin short-circuit
    # ──────────────────────────────────────────────────────────────────────
    if SUPERADMIN_MODE:
        return UserInDB(
            id=SUPERADMIN_DB_ID,
            email=SUPERADMIN_EMAIL,
            username=SUPERADMIN_UNAME,
            full_name="Super Admin",
            hashed_password="",
            is_active=True,
            is_verified=True,
            birth_date=datetime(1980, 1, 1),
            gender="other",
            interests=["Technology","Food", "Gaming","Cars","Traveling"],
            bio="I keep the lights on 👑",
            location="Nowhere",
            profile_photo="https://example.com/admin.jpg",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    # ──────────────────────────────────────────────────────────────────────
    # 2. no token → return a stub test user (development convenience)
    # ──────────────────────────────────────────────────────────────────────
    if token is None:
        return UserInDB(
            id="test-user-id",
            email="test@sammyswipe.com",
            username="testuser",
            full_name="Test User",
            hashed_password="",
            is_active=True,
            is_verified=True,
            birth_date=datetime.utcnow() - timedelta(days=365 * 25),
            gender="other",
            interests=["testing", "debugging"],
            bio="Test user for development",
            location="Test Location",
            profile_photo="https://example.com/test.jpg",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    # ──────────────────────────────────────────────────────────────────────
    # 3. normal JWT validation path
    # ──────────────────────────────────────────────────────────────────────
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    query = """
    MATCH (u:User {email:$email})
    RETURN u
    """
    result = db.execute_query(query, {"email": token_data.email})
    if not result:
        raise credentials_exception

    return UserInDB(**result[0]["u"])

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 