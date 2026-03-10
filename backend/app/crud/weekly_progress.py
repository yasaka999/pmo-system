from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.weekly_progress import WeeklyProgress
from app.schemas.weekly_progress import WeeklyProgressCreate, WeeklyProgressUpdate


def get_by_id(db: Session, progress_id: int) -> Optional[WeeklyProgress]:
    """根据ID获取周报进展"""
    return db.query(WeeklyProgress).filter(WeeklyProgress.id == progress_id).first()


def get_by_project(
    db: Session, 
    project_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[WeeklyProgress]:
    """获取项目的所有周报进展，按日期倒序排列"""
    return (
        db.query(WeeklyProgress)
        .filter(WeeklyProgress.project_id == project_id)
        .order_by(desc(WeeklyProgress.record_date), desc(WeeklyProgress.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(
    db: Session, 
    obj_in: WeeklyProgressCreate, 
    created_by: Optional[int] = None
) -> WeeklyProgress:
    """创建周报进展"""
    db_obj = WeeklyProgress(
        project_id=obj_in.project_id,
        content=obj_in.content,
        record_date=obj_in.record_date,
        progress_percent=obj_in.progress_percent or 0,
        next_plan=obj_in.next_plan,
        issues=obj_in.issues,
        created_by=created_by,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, 
    db_obj: WeeklyProgress, 
    obj_in: WeeklyProgressUpdate
) -> WeeklyProgress:
    """更新周报进展"""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, db_obj: WeeklyProgress) -> None:
    """删除周报进展"""
    db.delete(db_obj)
    db.commit()


def get_latest_by_project(db: Session, project_id: int) -> Optional[WeeklyProgress]:
    """获取项目最新的周报进展"""
    return (
        db.query(WeeklyProgress)
        .filter(WeeklyProgress.project_id == project_id)
        .order_by(desc(WeeklyProgress.record_date))
        .first()
    )
