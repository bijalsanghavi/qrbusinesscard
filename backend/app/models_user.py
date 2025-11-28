from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from .db import Base
import uuid

def gen_uuid() -> str:
    return uuid.uuid4().hex

class User(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, default=gen_uuid)
    email = Column(String(320), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    picture = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # Monetization
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    sub_active = Column(Boolean, nullable=False, server_default='false')
    sub_ends_at = Column(DateTime(timezone=True), nullable=True)
    plan = Column(String(64), nullable=True)
    stripe_customer_id = Column(String(128), nullable=True)
    stripe_subscription_id = Column(String(128), nullable=True)
