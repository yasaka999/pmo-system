from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(300), nullable=False, comment="问题标题")
    description = Column(Text, comment="问题描述")
    severity = Column(String(10), default="中", comment="严重等级: 高/中/低")
    source = Column(String(20), default="内部", comment="来源: 客户/内部/第三方")
    assignee = Column(String(100), comment="负责人")
    raised_date = Column(Date, comment="提出日期")
    due_date = Column(Date, comment="期望解决日期")
    resolved_date = Column(Date, comment="实际解决日期")
    status = Column(String(20), default="待处理", comment="待处理/处理中/已关闭")
    resolution = Column(Text, comment="解决措施")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="issues")
