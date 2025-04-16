from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    
class UserCreate(UserBase):
    password: str
    gender: Gender
    birth_date: datetime
    bio: Optional[str] = None
    interests: List[str] = []
    location: Optional[str] = None
    profile_photo: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    interests: Optional[List[str]] = None
    location: Optional[str] = None
    profile_photo: Optional[str] = None

class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    is_verified: bool = False

class UserResponse(UserBase):
    id: str
    gender: Gender
    birth_date: datetime
    bio: Optional[str] = None
    interests: List[str] = []
    location: Optional[str] = None
    profile_photo: Optional[str] = None
    match_score: Optional[float] = None

class UserPreferences(BaseModel):
    min_age: int = Field(ge=18, le=100)
    max_age: int = Field(ge=18, le=100)
    preferred_gender: Optional[List[Gender]] = None
    max_distance: Optional[int] = Field(None, ge=1, le=1000)
    interests_weight: float = Field(default=0.5, ge=0, le=1)
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None 