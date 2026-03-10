"""
操作日志 API
- admin 用户可以查看所有日志
- 普通用户只能查看自己的日志
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_active_user
from app.schemas.schemas import OperationLogOut

router = APIRouter()

@router.get("/", response_model=List[OperationLogOut])
def get_operation_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,  # 仅 admin 可用
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取操作日志
    - admin 用户可以查看所有日志或指定用户的日志
    - 普通用户只能查看自己的日志
    """
    from app.models.operation_log import OperationLog
    
    query = db.query(OperationLog)
    
    # 权限控制
    if current_user.role != "admin":
        # 普通用户只能查看自己的日志
        query = query.filter(OperationLog.user_id == current_user.id)
    elif user_id:
        # admin 可以查看指定用户的日志
        query = query.filter(OperationLog.user_id == user_id)
    
    logs = query.order_by(OperationLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/users", response_model=List[dict])
def get_log_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取有操作日志的用户列表（仅 admin）
    """
    from app.models.operation_log import OperationLog
    from sqlalchemy import distinct
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有权限")
    
    # 查询有日志的用户
    users = db.query(
        distinct(OperationLog.user_id),
        OperationLog.username
    ).filter(
        OperationLog.user_id.isnot(None)
    ).order_by(OperationLog.username).all()
    
    return [{"user_id": u[0], "username": u[1]} for u in users]
