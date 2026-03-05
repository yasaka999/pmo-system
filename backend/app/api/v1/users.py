from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import schemas
from app.crud import crud_user
from app.core.security import get_current_active_user, get_password_hash
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[schemas.UserOut])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取系统中所有用户（仅管管理员可见，简单起见前端控制或者这里直接校验权限）
    """
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="没有权限查看所有用户")
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=schemas.UserOut)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    新建用户（仅admin）
    """
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="没有权限创建用户")
    
    db_user = crud_user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="同名用户已存在")
    
    return crud_user.create_user(db=db, user=user)

@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新用户信息（仅admin）
    """
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="没有权限更新用户")
    
    db_user = crud_user.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.put("/{user_id}/status", response_model=schemas.UserOut)
def update_user_status(
    user_id: int,
    is_active: bool = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    启停用账号（仅admin）
    """
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="没有权限更新用户状态")
    
    if current_user.id == user_id:
         raise HTTPException(status_code=400, detail="不能停用当前登录账号")
         
    db_user = crud_user.update_user_status(db, user_id=user_id, is_active=is_active)
    if db_user is None:
         raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除用户（仅admin）
    """
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="没有权限删除用户")
    if current_user.id == user_id:
         raise HTTPException(status_code=400, detail="不能删除当前登录账号")
         
    success = crud_user.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "删除成功"}

@router.put("/me/password")
def change_my_password(
    old_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    用户自行修改密码
    """
    from app.core.security import verify_password
    
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="旧密码不正确")
        
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "密码修改成功"}
