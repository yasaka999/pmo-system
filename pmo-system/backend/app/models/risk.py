from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base

# 风险矩阵：概率 x 影响 => 风险等级（英文代码）
# 概率：rp_h=高，rp_m=中，rp_l=低
# 影响：ri_h=高，ri_m=中，ri_l=低
# 等级：rl_h=高，rl_m=中，rl_l=低
RISK_MATRIX = {
    ("rp_h", "ri_h"): "rl_h", ("rp_h", "ri_m"): "rl_h", ("rp_h", "ri_l"): "rl_m",
    ("rp_m", "ri_h"): "rl_h", ("rp_m", "ri_m"): "rl_m", ("rp_m", "ri_l"): "rl_l",
    ("rp_l", "ri_h"): "rl_m", ("rp_l", "ri_m"): "rl_l", ("rp_l", "ri_l"): "rl_l",
}


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(300), nullable=False, comment="风险标题")
    description = Column(Text, comment="风险描述")
    probability = Column(String(10), default="rp_m", comment="概率：rp_h=高/rp_m=中/rp_l=低")
    impact = Column(String(10), default="ri_m", comment="影响：ri_h=高/ri_m=中/ri_l=低")
    level = Column(String(10), comment="风险等级（自动计算）")
    mitigation = Column(Text, comment="应对措施")
    assignee = Column(String(100), comment="负责人")
    status = Column(String(20), default="rs_open", comment="状态：rs_open=开放/rs_mitig=已缓解/rs_closed=已关闭")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="risks")
