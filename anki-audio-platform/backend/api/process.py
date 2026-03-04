"""
API: POST /process - 提交 YouTube URL 开始处理
     GET /status/{task_id} - 查询任务进度
     GET /decks - 获取所有牌组列表
"""
import uuid
import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl

from backend.db import get_db
from backend.services.pipeline import run_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()


class ProcessRequest(BaseModel):
    youtube_url: str
    lang: str = "en"


@router.post("/process")
async def process_video(req: ProcessRequest, background_tasks: BackgroundTasks):
    """提交 YouTube URL 开始处理"""
    import aiosqlite
    from backend.db import DB_PATH

    deck_id = uuid.uuid4().hex
    task_id = uuid.uuid4().hex

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO deck (id, youtube_url, lang_cd, status) VALUES (?, ?, ?, 'pending')",
            (deck_id, req.youtube_url, req.lang)
        )
        await db.execute(
            "INSERT INTO task (id, deck_id, status) VALUES (?, ?, 'pending')",
            (task_id, deck_id)
        )
        await db.commit()

    background_tasks.add_task(run_pipeline, task_id, deck_id, req.youtube_url, req.lang)

    logger.info(f"已提交任务 task_id={task_id} deck_id={deck_id}")
    return {
        "task_id": task_id,
        "deck_id": deck_id,
        "status_url": f"/status/{task_id}",
    }


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """轮询任务进度"""
    import aiosqlite
    from backend.db import DB_PATH

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT t.id as task_id, t.status as task_status,
                      d.id as deck_id, d.status as deck_status,
                      d.title, d.progress, d.total, d.error_msg
               FROM task t JOIN deck d ON t.deck_id = d.id
               WHERE t.id = ?""",
            (task_id,)
        ) as cursor:
            row = await cursor.fetchone()

    if not row:
        raise HTTPException(404, "任务不存在")

    return {
        "task_id": row["task_id"],
        "deck_id": row["deck_id"],
        "status": row["deck_status"],
        "title": row["title"],
        "progress": row["progress"],
        "total": row["total"],
        "error_msg": row["error_msg"],
        "done": row["deck_status"] == "done",
    }


@router.get("/decks")
async def list_decks():
    """获取所有牌组列表"""
    import aiosqlite
    from backend.db import DB_PATH

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, youtube_url, title, lang_cd, status, progress, total, created_at FROM deck ORDER BY created_at DESC"
        ) as cursor:
            rows = await cursor.fetchall()

    return [dict(r) for r in rows]
