from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.weekly_progress import (
    WeeklyProgressCreate, 
    WeeklyProgressUpdate, 
    WeeklyProgressResponse
)
from app.crud import weekly_progress as crud

router = APIRouter()


@router.get("/projects/{project_id}/weekly-progress", response_model=List[WeeklyProgressResponse])
def list_weekly_progress(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取项目的周报进展列表，按日期倒序排列"""
    progresses = crud.get_by_project(db, project_id=project_id, skip=skip, limit=limit)
    
    # 添加创建者姓名
    result = []
    for p in progresses:
        data = {
            "id": p.id,
            "project_id": p.project_id,
            "content": p.content,
            "record_date": p.record_date,
            "progress_percent": p.progress_percent,
            "next_plan": p.next_plan,
            "issues": p.issues,
            "created_by": p.created_by,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "creator_name": p.creator.full_name if p.creator else None,
        }
        result.append(data)
    
    return result


@router.post("/projects/{project_id}/weekly-progress", response_model=WeeklyProgressResponse, status_code=status.HTTP_201_CREATED)
def create_weekly_progress(
    project_id: int,
    obj_in: WeeklyProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建周报进展记录"""
    # 确保 project_id 一致
    obj_in.project_id = project_id
    
    db_obj = crud.create(db, obj_in=obj_in, created_by=current_user.id if current_user else None)
    
    return {
        "id": db_obj.id,
        "project_id": db_obj.project_id,
        "content": db_obj.content,
        "record_date": db_obj.record_date,
        "progress_percent": db_obj.progress_percent,
        "next_plan": db_obj.next_plan,
        "issues": db_obj.issues,
        "created_by": db_obj.created_by,
        "created_at": db_obj.created_at,
        "updated_at": db_obj.updated_at,
        "creator_name": current_user.full_name if current_user else None,
    }


@router.put("/weekly-progress/{progress_id}", response_model=WeeklyProgressResponse)
def update_weekly_progress(
    progress_id: int,
    obj_in: WeeklyProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新周报进展记录"""
    db_obj = crud.get_by_id(db, progress_id=progress_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="周报进展记录不存在")
    
    db_obj = crud.update(db, db_obj=db_obj, obj_in=obj_in)
    
    return {
        "id": db_obj.id,
        "project_id": db_obj.project_id,
        "content": db_obj.content,
        "record_date": db_obj.record_date,
        "progress_percent": db_obj.progress_percent,
        "next_plan": db_obj.next_plan,
        "issues": db_obj.issues,
        "created_by": db_obj.created_by,
        "created_at": db_obj.created_at,
        "updated_at": db_obj.updated_at,
        "creator_name": db_obj.creator.full_name if db_obj.creator else None,
    }


@router.delete("/weekly-progress/{progress_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weekly_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除周报进展记录"""
    db_obj = crud.get_by_id(db, progress_id=progress_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="周报进展记录不存在")
    
    crud.delete(db, db_obj=db_obj)
    return None
