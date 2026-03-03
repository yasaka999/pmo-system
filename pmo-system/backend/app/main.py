from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router
from app.db.session import engine
from app.db.base import Base

# 导入所有模型，确保建表时能发现
from app.models import user, project, milestone, issue, risk, manday, sys_dict  # noqa

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="PMO实施项目管理系统 API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境替换为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    """应用启动时自动建表"""
    Base.metadata.create_all(bind=engine)
    _seed_admin()


def _seed_admin():
    """初始化默认管理员账号（仅首次）"""
    from app.db.session import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                full_name="系统管理员",
                email="admin@pmo.local",
                hashed_password=get_password_hash("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("✅ 默认管理员已创建: admin / admin123")
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
