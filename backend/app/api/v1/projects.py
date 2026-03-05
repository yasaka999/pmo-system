from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.project import Project
from app.models.milestone import Milestone
from app.models.issue import Issue
from app.models.risk import Risk
from app.models.manday import ManDay
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectOut, ProjectSummary
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


def _can_manage(project: Project, current_user: User) -> bool:
    """判断当前用户是否有权限管理该项目（编辑/删除）"""
    if current_user.role in ("admin", "pmo"):
        return True
    # member/viewer 只能管理自己创建的项目
    return project.created_by == current_user.id


def _build_summary(p: Project, db: Session) -> ProjectSummary:
    used = db.query(func.sum(ManDay.days)).filter(ManDay.project_id == p.id).scalar() or 0
    open_issues = db.query(func.count(Issue.id)).filter(
        Issue.project_id == p.id, Issue.status != "已关闭"
    ).scalar() or 0
    open_risks = db.query(func.count(Risk.id)).filter(
        Risk.project_id == p.id, Risk.status == "开放"
    ).scalar() or 0
    ms_count = db.query(func.count(Milestone.id)).filter(Milestone.project_id == p.id).scalar() or 0
    return ProjectSummary(
        id=p.id, code=p.code, name=p.name, client=p.client, manager=p.manager,
        phase=p.phase, status=p.status, plan_end=p.plan_end,
        milestone_count=ms_count, open_issue_count=open_issues,
        open_risk_count=open_risks, used_mandays=used,
        budget_mandays=p.budget_mandays or 0,
        created_by=p.created_by,
        plan_delivery_date=p.plan_delivery_date,
        actual_delivery_date=p.actual_delivery_date,
        plan_final_acceptance_date=p.plan_final_acceptance_date,
        actual_final_acceptance_date=p.actual_final_acceptance_date,
    )


@router.get("/", response_model=List[ProjectSummary])
def list_projects(
    status: Optional[str] = None,       # 单值兼容（废弃，保留向后兼容）
    statuses: Optional[str] = None,     # 逗号分隔多选状态，如 "正常,预警"
    phases: Optional[str] = None,       # 逗号分隔多选阶段
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Project)

    # 角色权限过滤：member 只能看自己的
    if current_user.role not in ("admin", "pmo"):
        query = query.filter(
            (Project.created_by == current_user.id) | (Project.created_by.is_(None))
        )

    # 多选状态筛选（优先用 statuses，兼容旧 status）
    status_list = []
    if statuses:
        status_list = [s.strip() for s in statuses.split(",") if s.strip()]
    elif status:
        status_list = [status]
    if status_list:
        query = query.filter(Project.status.in_(status_list))

    # 多选阶段筛选
    if phases:
        phase_list = [p.strip() for p in phases.split(",") if p.strip()]
        if phase_list:
            query = query.filter(Project.phase.in_(phase_list))

    projects = query.all()
    return [_build_summary(p, db) for p in projects]


@router.post("/", response_model=ProjectOut, status_code=201)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if db.query(Project).filter(Project.code == project_in.code).first():
        raise HTTPException(status_code=400, detail="项目编号已存在")
    project = Project(**project_in.model_dump(), created_by=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    # member 只能看自己的或 created_by 为空的
    if current_user.role not in ("admin", "pmo"):
        if project.created_by is not None and project.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问该项目")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    if not _can_manage(project, current_user):
        raise HTTPException(status_code=403, detail="无权编辑该项目，仅项目创建者或管理员可编辑")
    for field, value in project_in.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    if not _can_manage(project, current_user):
        raise HTTPException(status_code=403, detail="无权删除该项目，仅项目创建者或管理员可删除")
    db.delete(project)
    db.commit()
