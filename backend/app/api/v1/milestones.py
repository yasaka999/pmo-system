from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.logging import record_operation
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
def create_milestone(project_id: int, ms_in: MilestoneCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not db.query(Project).filter(Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="项目不存在")
    ms = Milestone(**{**ms_in.model_dump(), "project_id": project_id})
    db.add(ms)
    db.commit()
    db.refresh(ms)
    # 记录操作日志
    record_operation("CREATE", "里程碑管理", f"创建里程碑：{ms.name}", request, current_user)
    return ms


@router.put("/milestones/{ms_id}", response_model=MilestoneOut)
def update_milestone(ms_id: int, ms_in: MilestoneUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ms = db.query(Milestone).filter(Milestone.id == ms_id).first()
    if not ms:
        raise HTTPException(status_code=404, detail="里程碑不存在")
    for k, v in ms_in.model_dump(exclude_unset=True).items():
        setattr(ms, k, v)
    db.commit()
    db.refresh(ms)
    # 记录操作日志
    record_operation("UPDATE", "里程碑管理", f"更新里程碑：{ms_id}", request, current_user)
    return ms


@router.delete("/milestones/{ms_id}", status_code=204)
def delete_milestone(ms_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ms = db.query(Milestone).filter(Milestone.id == ms_id).first()
    if not ms:
        raise HTTPException(status_code=404, detail="里程碑不存在")
    db.delete(ms)
    db.commit()
    # 记录操作日志
    record_operation("DELETE", "里程碑管理", f"删除里程碑：{ms_id}", request, current_user)


# ── 任务 ──────────────────────────────────────────────
@router.get("/milestones/{ms_id}/tasks", response_model=List[TaskOut])
def list_tasks(ms_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Task).filter(Task.milestone_id == ms_id).order_by(Task.order_index).all()


@router.post("/milestones/{ms_id}/tasks", response_model=TaskOut, status_code=201)
def create_task(ms_id: int, task_in: TaskCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not db.query(Milestone).filter(Milestone.id == ms_id).first():
        raise HTTPException(status_code=404, detail="里程碑不存在")
    task = Task(**{**task_in.model_dump(), "milestone_id": ms_id})
    db.add(task)
    db.commit()
    db.refresh(task)
    # 记录操作日志
    record_operation("CREATE", "任务管理", f"创建任务：{task.title}", request, current_user)
    return task


@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_in: TaskUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    for k, v in task_in.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    # 记录操作日志
    record_operation("UPDATE", "任务管理", f"更新任务：{task_id}", request, current_user)
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()
    # 记录操作日志
    record_operation("DELETE", "任务管理", f"删除任务：{task_id}", request, current_user)
