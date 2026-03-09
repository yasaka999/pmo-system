from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class ManDay(Base):
    __tablename__ = "mandays"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    staff_name = Column(String(100), nullable=False, comment="人员姓名")
    role = Column(String(50), comment="角色: 项目经理/实施顾问/技术工程师等")
    work_date = Column(Date, nullable=False, comment="工作日期")
    days = Column(Float, nullable=False, comment="投入人天数")
    work_content = Column(Text, comment="工作内容")
    is_billable = Column(Boolean, default=True, comment="是否计费")
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="mandays")
