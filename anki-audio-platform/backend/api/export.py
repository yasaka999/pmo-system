"""
API: GET /export/{deck_id}/anki - 下载 .apkg 文件
     GET /deck/prefer/{username}/  - 用户偏好（夜间模式）
"""
import logging
import aiosqlite
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from backend.db import DB_PATH
from backend.services.storage import get_apkg_path

logger = logging.getLogger(__name__)
router = APIRouter()

# 简单的偏好存储（MVP 阶段用内存，重启后重置）
_preferences: dict = {}


@router.get("/export/{deck_id}/anki")
async def export_anki(deck_id: str):
    """下载已生成的 .apkg 文件"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, title, status FROM deck WHERE id=?", (deck_id,)
        ) as cursor:
            deck = await cursor.fetchone()

    if not deck:
        raise HTTPException(404, "牌组不存在")

    if deck["status"] != "done":
        raise HTTPException(400, f"牌组尚未处理完成，当前状态: {deck['status']}")

    apkg_path = get_apkg_path(deck_id)
    if not apkg_path:
        raise HTTPException(404, "apkg 文件不存在")

    safe_title = (deck["title"] or deck_id)[:50].replace("/", "_").replace("\\", "_")
    filename = f"{safe_title}.apkg"

    return FileResponse(
        apkg_path,
        media_type="application/octet-stream",
        filename=filename,
    )


@router.get("/deck/prefer/{username}/")
async def get_prefer(username: str):
    """获取用户偏好（供 Anki 卡片模板调用）"""
    pref = _preferences.get(username, {"dark_mode": False})
    return JSONResponse(pref)


@router.post("/deck/prefer/{username}/")
async def set_prefer(username: str, dark_mode: bool = False):
    """设置用户偏好"""
    _preferences[username] = {"dark_mode": dark_mode}
    return {"ok": True}
