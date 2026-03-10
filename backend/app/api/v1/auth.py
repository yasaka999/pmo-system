from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.schemas import UserCreate, UserOut, Token
from app.core.logging import record_operation
from app.core.security import (
    verify_password, get_password_hash, create_access_token, get_current_user
)

router = APIRouter()


@router.post("/login", response_model=Token)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已禁用")
    
    # 记录登录日志
    from app.models.operation_log import OperationLog
    from app.db.session import SessionLocal
    import threading
    log_entry = OperationLog(
        user_id=user.id,
        username=user.username,
        action="LOGIN",
        module="登录认证",
        description=f"用户登录：{user.username}",
        request_method="POST",
        request_url=str(request.url),
        ip_address=request.client.host if request.client else "",
        user_agent=request.headers.get("user-agent", "")
    )
    def save_log():
        try:
            db_log = SessionLocal()
            db_log.add(log_entry)
            db_log.commit()
            db_log.close()
        except Exception as e:
            print(f"Login log save error: {e}")
    threading.Thread(target=save_log).start()
    
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=user_in.username,
        full_name=user_in.full_name,
        email=user_in.email,
        role=user_in.role,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
