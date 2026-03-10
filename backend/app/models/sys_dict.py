from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class SysDict(Base):
    __tablename__ = "sys_dicts"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), index=True)    # 字典类别（如：project_phase, project_status）
    code = Column(String(50), index=True)        # 字典编码（唯一，如：phase_impl）
    label = Column(String(100))                  # 显示名称（如：实施阶段）
    sort_order = Column(Integer, default=0)      # 排序
    color = Column(String(20), nullable=True)    # 前端样式颜色（如：success, #FF0000）
    is_active = Column(Boolean, default=True)    # 是否启用
