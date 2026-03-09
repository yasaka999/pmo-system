from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.milestone import Milestone, Task
from app.models.project import Project
from app.schemas.schemas import (
    MilestoneCreate, MilestoneUpdate, MilestoneOut,
    TaskCreate, TaskUpdate, TaskOut,
)
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


# ── 里程碑 ──────────────────────────────────────────────
@router.get("/projects/{project_id}/milestones", response_model=List[MilestoneOut])
def list_milestones(project_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Milestone).filter(Milestone.project_id == project_id).order_by(Milestone.order_index).all()


@router.post("/projects/{project_id}/milestones", response_model=MilestoneOut, status_code=201)
def create_milestone(project_id: int, ms_in: MilestoneCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    if not db.query(Project).filter(Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="项目不存在")
    ms = Milestone(**{**ms_in.model_dump(), "project_id": project_id})
    db.add(ms)
    db.commit()
    db.refresh(ms)
    return ms


@router.put("/milestones/{ms_id}", response_model=MilestoneOut)
def update_milestone(ms_id: int, ms_in: MilestoneUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    ms = db.query(Milestone).filter(Milestone.id == ms_id).first()
    if not ms:
        raise HTTPException(status_code=404, detail="里程碑不存在")
    for k, v in ms_in.model_dump(exclude_unset=True).items():
        setattr(ms, k, v)
    db.commit()
    db.refresh(ms)
    return ms


@router.delete("/milestones/{ms_id}", status_code=204)
def delete_milestone(ms_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    ms = db.query(Milestone).filter(Milestone.id == ms_id).first()
    if not ms:
        raise HTTPException(status_code=404, detail="里程碑不存在")
    db.delete(ms)
    db.commit()


# ── 工作任务 ────────────────────────────────────────────
@router.get("/projects/{project_id}/tasks", response_model=List[TaskOut])
def list_tasks(project_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Task).filter(Task.project_id == project_id).all()


@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=201)
def create_task(project_id: int, task_in: TaskCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    if not db.query(Project).filter(Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="项目不存在")
    task = Task(**{**task_in.model_dump(), "project_id": project_id})
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    for k, v in task_in.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()
