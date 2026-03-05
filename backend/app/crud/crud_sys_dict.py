from sqlalchemy.orm import Session
from app.models.sys_dict import SysDict
from app.schemas.schemas import SysDictCreate, SysDictUpdate

def get_sys_dict(db: Session, dict_id: int):
    return db.query(SysDict).filter(SysDict.id == dict_id).first()

def get_sys_dicts_by_category(db: Session, category: str):
    return db.query(SysDict).filter(SysDict.category == category).order_by(SysDict.sort_order).all()

def get_sys_dicts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SysDict).order_by(SysDict.category, SysDict.sort_order).offset(skip).limit(limit).all()

def create_sys_dict(db: Session, sys_dict: SysDictCreate):
    db_dict = SysDict(**sys_dict.model_dump())
    db.add(db_dict)
    db.commit()
    db.refresh(db_dict)
    return db_dict

def update_sys_dict(db: Session, dict_id: int, sys_dict: SysDictUpdate):
    db_dict = get_sys_dict(db, dict_id)
    if db_dict:
        update_data = sys_dict.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_dict, key, value)
        db.commit()
        db.refresh(db_dict)
    return db_dict

def delete_sys_dict(db: Session, dict_id: int):
    db_dict = get_sys_dict(db, dict_id)
    if db_dict:
        db.delete(db_dict)
        db.commit()
        return True
    return False
