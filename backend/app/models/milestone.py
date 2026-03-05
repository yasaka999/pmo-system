from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(200), nullable=False, comment="里程碑名称")
    plan_date = Column(Date, comment="计划完成日期")
    actual_date = Column(Date, comment="实际完成日期")
    status = Column(String(20), default="未开始", comment="未开始/进行中/已完成/延期")
    description = Column(Text, comment="描述")
    order_index = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    name = Column(String(200), nullable=False, comment="工作项名称")
    assignee = Column(String(100), comment="负责人")
    plan_start = Column(Date, comment="计划开始")
    plan_end = Column(Date, comment="计划结束")
    actual_start = Column(Date, comment="实际开始")
    actual_end = Column(Date, comment="实际结束")
    progress = Column(Integer, default=0, comment="完成比例 0-100")
    status = Column(String(20), default="未开始", comment="未开始/进行中/已完成/延期")
    notes = Column(Text, comment="备注")
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project")
    milestone = relationship("Milestone", back_populates="tasks")
