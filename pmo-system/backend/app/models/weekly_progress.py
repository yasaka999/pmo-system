from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class WeeklyProgress(Base):
    """周报进展记录"""
    __tablename__ = "weekly_progress"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="关联项目ID")
    
    # 核心字段
    content = Column(Text, nullable=False, comment="工作内容/进展描述")
    record_date = Column(Date, nullable=False, comment="记录日期，默认当天")
    
    # 可选扩展字段
    progress_percent = Column(Integer, default=0, comment="完成进度百分比(0-100)")
    next_plan = Column(Text, comment="下周计划")
    issues = Column(Text, comment="遇到的问题")
    
    # 元数据
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者用户ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    project = relationship("Project", back_populates="weekly_progresses")
    creator = relationship("User", foreign_keys=[created_by])
