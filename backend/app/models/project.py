from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False, comment="项目编号")
    name = Column(String(200), nullable=False, comment="项目名称")
    client = Column(String(200), comment="客户/甲方")
    manager = Column(String(100), comment="项目经理")
    phase = Column(String(20), default="ph_kickoff", comment="项目阶段：ph_pre=售前/ph_kickoff=启动/ph_impl=实施/ph_accept=验收/ph_close=收尾")
    status = Column(String(20), default="st_normal", comment="项目状态：st_normal=正常/st_warn=预警/st_delay=延期/st_pause=暂停/st_done=已完成")
    plan_start = Column(Date, comment="计划开始日期")
    plan_end = Column(Date, comment="计划结束日期")
    actual_start = Column(Date, comment="实际开始日期")
    actual_end = Column(Date, comment="实际结束日期")
    budget_mandays = Column(Float, default=0, comment="预算人天")
    description = Column(Text, comment="项目描述")
    contract_no = Column(String(100), comment="合同编号")
    region = Column(String(100), comment="区域")
    plan_delivery_date = Column(Date, comment="计划交付日期")
    actual_delivery_date = Column(Date, comment="实际交付日期")
    plan_initial_acceptance_date = Column(Date, comment="计划初验日期")
    actual_initial_acceptance_date = Column(Date, comment="实际初验日期")
    plan_final_acceptance_date = Column(Date, comment="计划终验日期")
    actual_final_acceptance_date = Column(Date, comment="实际终验日期")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者用户 ID")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    mandays = relationship("ManDay", back_populates="project", cascade="all, delete-orphan")
    weekly_progresses = relationship("WeeklyProgress", back_populates="project", cascade="all, delete-orphan", order_by="desc(WeeklyProgress.record_date)")
    creator = relationship("User", foreign_keys=[created_by])

