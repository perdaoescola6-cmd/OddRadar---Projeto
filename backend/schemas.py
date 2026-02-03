from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatMessageRequest(BaseModel):
    content: str
    extra_data: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime

class SubscriptionCreate(BaseModel):
    user_id: int
    plan: str
    days: int

class AdminGrantRequest(BaseModel):
    email: EmailStr
    plan: str
    days: int

class AdminRevokeRequest(BaseModel):
    email: EmailStr

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan: str
    status: str
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
