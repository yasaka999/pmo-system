from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base

# 风险矩阵：概率 x 影响 => 风险等级
RISK_MATRIX = {
    ("高", "高"): "极高", ("高", "中"): "高", ("高", "低"): "中",
    ("中", "高"): "高",  ("中", "中"): "中", ("中", "低"): "低",
    ("低", "高"): "中",  ("低", "中"): "低", ("低", "低"): "极低",
}


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(300), nullable=False, comment="风险标题")
    description = Column(Text, comment="风险描述")
    probability = Column(String(10), default="中", comment="概率: 高/中/低")
    impact = Column(String(10), default="中", comment="影响: 高/中/低")
    level = Column(String(10), comment="风险等级（自动）")
    mitigation = Column(Text, comment="应对措施")
    assignee = Column(String(100), comment="负责人")
    status = Column(String(20), default="开放", comment="开放/已缓解/已关闭")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="risks")
