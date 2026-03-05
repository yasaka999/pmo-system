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

def batch_save_sys_dicts(db: Session, items: list):
    """
    批量保存字典项：删除标记删除的，新增新项，更新已有项
    返回 (created_count, updated_count, deleted_count)
    """
    print(f"=== batch_save received {len(items)} items ===")
    for item in items:
        if item.get('_deleted'):
            print(f"Item marked for deletion: id={item.get('id')}, _deleted={item.get('_deleted')}, category={item.get('category')}, code={item.get('code')}, label={item.get('label')}")
    
    created = 0
    updated = 0
    deleted = 0
    
    for item in items:
        print(f"Processing item: id={item.get('id')}, _deleted={item.get('_deleted')}, category={item.get('category')}, code={item.get('code')}")
        if item.get('_deleted') and item.get('id'):
            # 删除
            db_dict = get_sys_dict(db, item['id'])
            if db_dict:
                db.delete(db_dict)
                deleted += 1
                print(f"Deleted item id={item['id']}")
        elif item.get('_deleted'):
            # 新增但被标记删除，跳过
            print("Skipping: new item marked for deletion")
            continue
        elif not item.get('id'):
            # 新增
            db_dict = SysDict(
                category=item['category'],
                code=item['code'],
                label=item['label'],
                sort_order=item.get('sort_order', 0),
                color=item.get('color'),
                is_active=item.get('is_active', True)
            )
            db.add(db_dict)
            created += 1
            print(f"Created item: {item['code']}")
        else:
            # 更新
            db_dict = get_sys_dict(db, item['id'])
            if db_dict:
                db_dict.category = item['category']
                db_dict.code = item['code']
                db_dict.label = item['label']
                db_dict.sort_order = item.get('sort_order', 0)
                db_dict.color = item.get('color')
                db_dict.is_active = item.get('is_active', True)
                updated += 1
                print(f"Updated item id={item['id']}")
    
    db.commit()
    print(f"=== batch_save result: created={created}, updated={updated}, deleted={deleted} ===")
    return created, updated, deleted
