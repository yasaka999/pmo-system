"""
FastAPI 应用入口
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.db import init_db
from backend.api.process import router as process_router
from backend.api.card import router as card_router
from backend.api.export import router as export_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

STORAGE_DIR = os.environ.get(
    "STORAGE_DIR",
    os.path.join(os.path.dirname(__file__), "..", "storage")
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AnkiAudio Platform 启动中...")
    await init_db()
    logger.info("✅ 数据库初始化完成")
    yield
    logger.info("👋 服务关闭")


app = FastAPI(
    title="AnkiAudio Platform",
    description="个人云端音频 Anki 服务",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS（允许 Anki iframe 跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(process_router, tags=["处理流程"])
app.include_router(card_router, tags=["卡片渲染"])
app.include_router(export_router, tags=["导出与偏好"])

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}

# 静态文件（音频文件服务）
os.makedirs(STORAGE_DIR, exist_ok=True)
app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")

# 管理 Web 页面静态文件（必须最后挂载，避免覆盖其他路由）
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
