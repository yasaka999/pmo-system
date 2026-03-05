from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import schemas
from app.crud import crud_sys_dict
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[schemas.SysDictOut])
def read_sys_dicts(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取数据字典列表。
    如果提供了 category 参数，则只返回该类别下的字典。
    """
    if category:
        sys_dicts = crud_sys_dict.get_sys_dicts_by_category(db, category)
    else:
        sys_dicts = crud_sys_dict.get_sys_dicts(db, skip=skip, limit=limit)
    return sys_dicts

@router.post("/", response_model=schemas.SysDictOut)
def create_sys_dict(
    sys_dict: schemas.SysDictCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建数据字典项（仅限管理员，此处简单起见暂未硬性校验 admin 角色，后续可通过依赖注入完善）。
    """
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="没有权限执行此操作")
    return crud_sys_dict.create_sys_dict(db=db, sys_dict=sys_dict)

@router.put("/{dict_id}", response_model=schemas.SysDictOut)
def update_sys_dict(
    dict_id: int,
    sys_dict: schemas.SysDictUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新数据字典项
    """
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="没有权限执行此操作")
    
    db_dict = crud_sys_dict.update_sys_dict(db=db, dict_id=dict_id, sys_dict=sys_dict)
    if db_dict is None:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return db_dict

@router.delete("/{dict_id}")
def delete_sys_dict(
    dict_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除数据字典项
    """
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="没有权限执行此操作")
         
    success = crud_sys_dict.delete_sys_dict(db=db, dict_id=dict_id)
    if not success:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return {"message": "删除成功"}
