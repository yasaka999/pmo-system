"""
管理员专用 API
仅 admin 和 pmo 角色可访问
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("/admin/project-owners")
def get_all_projects_with_owners(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有项目及其负责人（仅 admin/pmo）
    """
    if current_user.role not in ("admin", "pmo"):
        raise HTTPException(status_code=403, detail="没有权限，仅管理员和 PMO 可访问")
    
    projects = db.query(Project).offset(skip).limit(limit).all()
    result = []
    for p in projects:
        result.append({
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "created_by": p.created_by,
            "owner_name": p.creator.username if p.creator else None,
            "owner_full_name": p.creator.full_name if p.creator else None,
        })
    return result


@router.get("/admin/users")
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有用户列表（仅 admin/pmo）
    用于选择新负责人
    """
    if current_user.role not in ("admin", "pmo"):
        raise HTTPException(status_code=403, detail="没有权限")
    
    users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
        }
        for u in users
    ]


@router.put("/admin/project/{project_id}/owner")
def reassign_project_owner(
    project_id: int,
    new_owner_id: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    重新分配项目负责人（仅 admin/pmo）
    """
    if current_user.role not in ("admin", "pmo"):
        raise HTTPException(status_code=403, detail="没有权限，仅管理员和 PMO 可访问")
    
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查新负责人是否存在
    new_owner = db.query(User).filter(User.id == new_owner_id).first()
    if not new_owner:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 保存旧负责人信息（用于日志）
    old_owner_id = project.created_by
    old_owner_name = project.creator.username if project.creator else None
    
    # 更新 created_by
    project.created_by = new_owner_id
    db.commit()
    db.refresh(project)
    
    return {
        "message": "负责人已更新",
        "project_id": project_id,
        "project_name": project.name,
        "old_owner_id": old_owner_id,
        "old_owner_name": old_owner_name,
        "new_owner_id": new_owner_id,
        "new_owner_name": new_owner.username,
    }
