from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import schemas
from app.crud import crud_user
from app.core.security import get_current_active_user, get_password_hash
from app.models.user import User
from app.core.logging import record_operation

router = APIRouter()


@router.get("/", response_model=List[schemas.UserOut])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取系统中所有用户（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有权限查看所有用户")
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.UserOut)
def create_user(
    user: schemas.UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """新建用户（仅 admin）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有权限创建用户")
    
    db_user = crud_user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="同名用户已存在")
    
    result = crud_user.create_user(db=db, user=user)
    record_operation("CREATE", "用户管理", f"创建用户：{user.username}", request, current_user)
    return result


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新用户信息（仅 admin）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有权限更新用户")
    
    db_user = crud_user.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    record_operation("UPDATE", "用户管理", f"更新用户：{user_id}", request, current_user)
    return db_user


@router.put("/{user_id}/status", response_model=schemas.UserOut)
def update_user_status(
    user_id: int,
    is_active: bool = Body(..., embed=True),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """启停用账号（仅 admin）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有权限更新用户状态")
    
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="不能停用当前登录账号")
        
    db_user = crud_user.update_user_status(db, user_id=user_id, is_active=is_active)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    action = "启用" if is_active else "停用"
    record_operation("UPDATE", "用户管理", f"{action}用户：{user_id}", request, current_user)
    return db_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除用户（仅 admin）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有权限删除用户")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="不能删除当前登录账号")
    
    success = crud_user.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    record_operation("DELETE", "用户管理", f"删除用户：{user_id}", request, current_user)
    return {"message": "用户已删除"}
