from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="member")  # admin / pmo / member / viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
