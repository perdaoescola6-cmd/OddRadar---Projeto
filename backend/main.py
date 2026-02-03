from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlmodel import Session, select
from datetime import datetime, timedelta
import os
import logging

from .database import create_db_and_tables, get_session
from .models import User, Subscription, ChatMessage, AuditLog
from .schemas import UserCreate, UserLogin, UserResponse, Token, ChatMessage, ChatResponse, AdminGrantRequest, AdminRevokeRequest, SubscriptionResponse
from .auth import get_current_user, get_admin_user, verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .chatbot import ChatBot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BetStats Trader API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot = ChatBot()

# Environment variables
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
PLUS_URL = os.getenv("PLUS_URL")
PRO_URL = os.getenv("PRO_URL")
ELITE_URL = os.getenv("ELITE_URL")

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

# Utility functions
def check_admin_api_key(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key"
        )
    return True

def check_user_subscription(user: User) -> bool:
    """Check if user has active subscription"""
    session = next(get_session())
    subscription = session.exec(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.status == "active",
            Subscription.expires_at > datetime.utcnow()
        )
    ).first()
    return subscription is not None

# Auth endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, session: Session = Depends(get_session)):
    """Register new user"""
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        created_at=datetime.utcnow()
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Log registration
    audit = AuditLog(
        user_id=user.id,
        action="user_registered",
        details={"email": user.email}
    )
    session.add(audit)
    session.commit()
    
    logger.info(f"User registered: {user.email}")
    return user

@app.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin, session: Session = Depends(get_session)):
    """Login user and return JWT token"""
    user = session.exec(select(User).where(User.email == user_data.email)).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Log login
    audit = AuditLog(
        user_id=user.id,
        action="user_login",
        details={"email": user.email}
    )
    session.add(audit)
    session.commit()
    
    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@app.get("/api/auth/subscription")
async def get_subscription_status(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Get user subscription status"""
    subscription = session.exec(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        ).order_by(Subscription.created_at.desc())
    ).first()
    
    if not subscription:
        return {
            "has_subscription": False,
            "plan": None,
            "expires_at": None,
            "status": "none"
        }
    
    return {
        "has_subscription": True,
        "plan": subscription.plan,
        "expires_at": subscription.expires_at,
        "status": subscription.status
    }

# Chat endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Process chat message"""
    # Check subscription
    if not check_user_subscription(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required to use chat"
        )
    
    # Save user message
    user_message = ChatMessage(
        user_id=current_user.id,
        role="user",
        content=message.content,
        created_at=datetime.utcnow()
    )
    session.add(user_message)
    
    # Process message
    try:
        response = await chatbot.process_message(message.content, current_user)
        
        # Save bot response
        bot_message = ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=response,
            created_at=datetime.utcnow()
        )
        session.add(bot_message)
        session.commit()
        
        logger.info(f"Chat processed for user {current_user.email}")
        
        return ChatResponse(
            response=response,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing message"
        )

@app.get("/api/chat/history")
async def get_chat_history(current_user: User = Depends(get_current_user), session: Session = Depends(get_session), limit: int = 50):
    """Get chat history"""
    messages = session.exec(
        select(ChatMessage).where(
            ChatMessage.user_id == current_user.id
        ).order_by(ChatMessage.created_at.desc()).limit(limit)
    ).all()
    
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at
        }
        for msg in reversed(messages)
    ]

# Plans/Billing endpoints
@app.get("/api/plans")
async def get_plans():
    """Get available subscription plans"""
    return {
        "plans": [
            {
                "id": "plus",
                "name": "Plus",
                "price": "R$30/mês",
                "features": [
                    "Acesso ao chatbot",
                    "Análises de times",
                    "Análises de jogos",
                    "Estatísticas básicas"
                ],
                "url": PLUS_URL
            },
            {
                "id": "pro",
                "name": "Pro", 
                "price": "R$60/mês",
                "features": [
                    "Todos os recursos Plus",
                    "Estatísticas avançadas",
                    "Mais históricos",
                    "Análises detalhadas"
                ],
                "url": PRO_URL
            },
            {
                "id": "elite",
                "name": "Elite",
                "price": "R$100/mês", 
                "features": [
                    "Todos os recursos Pro",
                    "Scanner de odds (em breve)",
                    "Análises premium",
                    "Suporte prioritário"
                ],
                "url": ELITE_URL
            }
        ]
    }

# Admin endpoints
@app.post("/api/admin/grant")
async def grant_subscription(
    request: AdminGrantRequest,
    session: Session = Depends(get_session),
    _: bool = Depends(check_admin_api_key)
):
    """Grant subscription to user"""
    # Find user
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create or update subscription
    expires_at = datetime.utcnow() + timedelta(days=request.days)
    
    # Cancel existing subscriptions
    existing = session.exec(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.status == "active"
        )
    ).all()
    
    for sub in existing:
        sub.status = "cancelled"
    
    # Create new subscription
    subscription = Subscription(
        user_id=user.id,
        plan=request.plan,
        status="active",
        expires_at=expires_at,
        updated_at=datetime.utcnow()
    )
    
    session.add(subscription)
    
    # Log action
    audit = AuditLog(
        user_id=user.id,
        action="subscription_granted",
        details={
            "plan": request.plan,
            "days": request.days,
            "expires_at": expires_at.isoformat()
        }
    )
    session.add(audit)
    session.commit()
    
    logger.info(f"Subscription granted to {user.email}: {request.plan}")
    
    return {"message": f"Subscription {request.plan} granted to {user.email}"}

@app.post("/api/admin/revoke")
async def revoke_subscription(
    request: AdminRevokeRequest,
    session: Session = Depends(get_session),
    _: bool = Depends(check_admin_api_key)
):
    """Revoke user subscription"""
    # Find user
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Cancel active subscriptions
    subscriptions = session.exec(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.status == "active"
        )
    ).all()
    
    if not subscriptions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    for sub in subscriptions:
        sub.status = "cancelled"
        sub.updated_at = datetime.utcnow()
    
    # Log action
    audit = AuditLog(
        user_id=user.id,
        action="subscription_revoked",
        details={"email": request.email}
    )
    session.add(audit)
    session.commit()
    
    logger.info(f"Subscription revoked for {user.email}")
    
    return {"message": f"Subscription revoked for {request.email}"}

@app.get("/api/admin/users")
async def list_users(
    search: str = None,
    session: Session = Depends(get_session),
    _: bool = Depends(check_admin_api_key)
):
    """List users with optional search"""
    query = select(User)
    if search:
        query = query.where(User.email.contains(search))
    
    users = session.exec(query.order_by(User.created_at.desc())).all()
    
    result = []
    for user in users:
        subscription = session.exec(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.status == "active"
            ).order_by(Subscription.created_at.desc())
        ).first()
        
        result.append({
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
            "is_active": user.is_active,
            "subscription": {
                "plan": subscription.plan,
                "expires_at": subscription.expires_at,
                "status": subscription.status
            } if subscription else None
        })
    
    return result

@app.get("/api/admin/user/{email}")
async def get_user_details(
    email: str,
    session: Session = Depends(get_session),
    _: bool = Depends(check_admin_api_key)
):
    """Get detailed user information"""
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    subscriptions = session.exec(
        select(Subscription).where(
            Subscription.user_id == user.id
        ).order_by(Subscription.created_at.desc())
    ).all()
    
    chat_messages = session.exec(
        select(ChatMessage).where(
            ChatMessage.user_id == user.id
        ).order_by(ChatMessage.created_at.desc()).limit(20)
    ).all()
    
    audit_logs = session.exec(
        select(AuditLog).where(
            AuditLog.user_id == user.id
        ).order_by(AuditLog.created_at.desc()).limit(10)
    ).all()
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
            "is_active": user.is_active
        },
        "subscriptions": [
            {
                "id": sub.id,
                "plan": sub.plan,
                "status": sub.status,
                "expires_at": sub.expires_at,
                "created_at": sub.created_at
            }
            for sub in subscriptions
        ],
        "recent_chats": [
            {
                "role": msg.role,
                "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                "created_at": msg.created_at
            }
            for msg in chat_messages
        ],
        "audit_logs": [
            {
                "action": log.action,
                "details": log.details,
                "created_at": log.created_at
            }
            for log in audit_logs
        ]
    }

# Health check
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
