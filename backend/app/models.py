from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy import JSON
from sqlalchemy.sql import func
from .db import Base
import uuid

def gen_uuid() -> str:
    return uuid.uuid4().hex

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(32), primary_key=True, default=gen_uuid)
    user_id = Column(String(32), nullable=True)
    slug = Column(String(64), unique=True, nullable=False, index=True)

    # Core fields
    full_name = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    org = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)

    url = Column(String(1024), nullable=True)
    note = Column(String(2048), nullable=True)
    photo_url = Column(String(2048), nullable=True)

    # Structured fields stored as JSON
    phones = Column(JSON, nullable=False, default=list)
    emails = Column(JSON, nullable=False, default=list)
    address = Column(JSON, nullable=False, default=dict)
    social = Column(JSON, nullable=False, default=dict)

    active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
