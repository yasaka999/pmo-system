from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class WeeklyProgressBase(BaseModel):
    """周报进展基础模型"""
    content: str = Field(..., min_length=1, description="工作内容/进展描述")
    record_date: date = Field(default_factory=date.today, description="记录日期，默认当天")
    progress_percent: Optional[int] = Field(default=0, ge=0, le=100, description="完成进度百分比(0-100)")
    next_plan: Optional[str] = Field(default=None, description="下周计划")
    issues: Optional[str] = Field(default=None, description="遇到的问题")


class WeeklyProgressCreate(WeeklyProgressBase):
    """创建周报进展"""
    project_id: Optional[int] = Field(default=None, description="关联项目ID，可从URL路径获取")


class WeeklyProgressUpdate(BaseModel):
    """更新周报进展"""
    content: Optional[str] = Field(default=None, min_length=1, description="工作内容/进展描述")
    record_date: Optional[date] = Field(default=None, description="记录日期")
    progress_percent: Optional[int] = Field(default=None, ge=0, le=100, description="完成进度百分比")
    next_plan: Optional[str] = Field(default=None, description="下周计划")
    issues: Optional[str] = Field(default=None, description="遇到的问题")


class WeeklyProgressInDB(WeeklyProgressBase):
    """数据库中的周报进展"""
    id: int
    project_id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeeklyProgressResponse(WeeklyProgressInDB):
    """API响应模型"""
    creator_name: Optional[str] = Field(default=None, description="创建者姓名")
