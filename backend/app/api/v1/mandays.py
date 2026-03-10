from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.logging import record_operation
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.manday import ManDay
from app.models.project import Project
from app.schemas.schemas import ManDayCreate, ManDayUpdate, ManDayOut
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/projects/{project_id}/mandays", response_model=List[ManDayOut])
def list_mandays(
    project_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(ManDay).filter(ManDay.project_id == project_id)
    if start_date:
        q = q.filter(ManDay.work_date >= start_date)
    if end_date:
        q = q.filter(ManDay.work_date <= end_date)
    return q.order_by(ManDay.work_date.desc()).all()


@router.post("/projects/{project_id}/mandays", response_model=ManDayOut, status_code=201)
def create_manday(project_id: int, md_in: ManDayCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not db.query(Project).filter(Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="项目不存在")
    md = ManDay(**{**md_in.model_dump(), "project_id": project_id})
    db.add(md)
    db.commit()
    db.refresh(md)
    # 记录操作日志
    record_operation("CREATE", "工时管理", f"创建工时记录：{md.staff_name}", request, current_user)
    return md


@router.put("/mandays/{md_id}", response_model=ManDayOut)
def update_manday(md_id: int, md_in: ManDayUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    md = db.query(ManDay).filter(ManDay.id == md_id).first()
    if not md:
        raise HTTPException(status_code=404, detail="记录不存在")
    for k, v in md_in.model_dump(exclude_unset=True).items():
        setattr(md, k, v)
    db.commit()
    db.refresh(md)
    record_operation("UPDATE", "工时管理", f"更新工时记录：{md_id}", request, current_user)
    return md


@router.delete("/mandays/{md_id}", status_code=204)
def delete_manday(md_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    md = db.query(ManDay).filter(ManDay.id == md_id).first()
    if not md:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(md)
    db.commit()
    # 记录操作日志
    record_operation("DELETE", "工时管理", f"删除工时记录：{md_id}", request, current_user)


@router.get("/projects/{project_id}/mandays/stats")
def manday_stats(project_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """按人员汇总人天统计，含总计/计费/非计费分类"""
    total = db.query(func.sum(ManDay.days)).filter(ManDay.project_id == project_id).scalar() or 0
    billable = db.query(func.sum(ManDay.days)).filter(
        ManDay.project_id == project_id, ManDay.is_billable == True
    ).scalar() or 0

    breakdown = (
        db.query(ManDay.staff_name, ManDay.role, func.sum(ManDay.days).label("total"))
        .filter(ManDay.project_id == project_id)
        .group_by(ManDay.staff_name, ManDay.role)
        .all()
    )
    project = db.query(Project).filter(Project.id == project_id).first()
    return {
        "project_id": project_id,
        "project_name": project.name if project else "",
        "budget_mandays": project.budget_mandays if project else 0,
        "total_days": round(total, 1),
        "billable_days": round(billable, 1),
        "non_billable_days": round(total - billable, 1),
        "staff_breakdown": [
            {"staff_name": b.staff_name, "role": b.role, "total": round(b.total, 1)}
            for b in breakdown
        ],
    }
