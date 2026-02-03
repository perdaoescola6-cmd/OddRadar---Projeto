"""Script para conceder plano Elite"""
import sys
sys.path.insert(0, '.')

from sqlmodel import Session, select
from database import engine
from models import User, Subscription
from datetime import datetime, timedelta

def grant_elite(email: str):
    with Session(engine) as session:
        # Find user
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            print(f"Usuário {email} não encontrado!")
            return
        
        # Cancel existing subscriptions
        existing = session.exec(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.status == "active"
            )
        ).all()
        
        for sub in existing:
            sub.status = "cancelled"
        
        # Create Elite subscription (30 days)
        subscription = Subscription(
            user_id=user.id,
            plan="elite",
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=30),
            updated_at=datetime.utcnow()
        )
        
        session.add(subscription)
        session.commit()
        
        print(f"✅ Plano ELITE concedido para {email}")
        print(f"   Válido até: {subscription.expires_at}")

if __name__ == "__main__":
    email = "perdaoescola6@gmail.com"
    grant_elite(email)
