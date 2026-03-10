from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(100), index=True)
    action = Column(String(50), nullable=False, index=True)  # CREATE/UPDATE/DELETE/LOGIN/LOGOUT
    module = Column(String(50))  # 用户管理/项目管理/系统配置
    description = Column(Text)  # 操作描述
    request_method = Column(String(10))  # POST/PUT/DELETE
    request_url = Column(String(200))
    ip_address = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
