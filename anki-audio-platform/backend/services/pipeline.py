"""
处理任务：协调整个 YouTube → 音频片段 → 数据库 → apkg 流程
"""
import asyncio
import uuid
import logging
import aiosqlite
import os

from backend.services.downloader import download_audio_and_subtitle
from backend.services.subtitle import parse_subtitle
from backend.services.splitter import split_audio
from backend.services.storage import save_apkg, get_audio_url
from backend.services.anki_export import generate_apkg
from backend.db import DB_PATH

logger = logging.getLogger(__name__)


async def _update_deck_status(deck_id: str, status: str, progress: int = 0,
                               total: int = 0, error_msg: str = None, title: str = None, thumbnail: str = None):
    """更新牌组状态（写DB）"""
    async with aiosqlite.connect(DB_PATH) as db:
        if title and thumbnail:
            await db.execute(
                "UPDATE deck SET status=?, progress=?, total=?, error_msg=?, title=?, thumbnail=? WHERE id=?",
                (status, progress, total, error_msg, title, thumbnail, deck_id)
            )
        elif title:
            await db.execute(
                "UPDATE deck SET status=?, progress=?, total=?, error_msg=?, title=? WHERE id=?",
                (status, progress, total, error_msg, title, deck_id)
            )
        elif thumbnail:
            await db.execute(
                "UPDATE deck SET status=?, progress=?, total=?, error_msg=?, thumbnail=? WHERE id=?",
                (status, progress, total, error_msg, thumbnail, deck_id)
            )
        else:
            await db.execute(
                "UPDATE deck SET status=?, progress=?, total=?, error_msg=? WHERE id=?",
                (status, progress, total, error_msg, deck_id)
            )
        await db.commit()


async def run_pipeline(task_id: str, deck_id: str, youtube_url: str, lang: str):
    """
    完整处理流水线（在后台线程池里运行）
    1. 下载音频+字幕
    2. 解析字幕
    3. 切分音频
    4. 写入数据库
    5. 生成 .apkg
    """
    try:
        # 更新任务状态
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE task SET status='processing' WHERE id=?", (task_id,))
            await db.commit()

        await _update_deck_status(deck_id, "downloading", 0, 0)

        # --- 步骤1：下载 ---
        logger.info(f"[{deck_id}] Step1: 下载")
        loop = asyncio.get_event_loop()
        download_result = await loop.run_in_executor(
            None,
            download_audio_and_subtitle,
            youtube_url, deck_id, lang
        )

        title = download_result["title"]
        audio_path = download_result["audio_path"]
        subtitle_path = download_result["subtitle_path"]
        thumbnail_path = download_result.get("thumbnail_path")

        await _update_deck_status(deck_id, "processing", 0, 0, title=title, thumbnail=thumbnail_path)

        # --- 步骤2：解析字幕 ---
        logger.info(f"[{deck_id}] Step2: 解析字幕")
        if subtitle_path:
            sub_segments = await loop.run_in_executor(None, parse_subtitle, subtitle_path)
        else:
            logger.warning(f"[{deck_id}] 无字幕，跳过切分")
            await _update_deck_status(deck_id, "error", error_msg="未找到字幕文件，无法切分音频")
            return

        if not sub_segments:
            await _update_deck_status(deck_id, "error", error_msg="字幕解析结果为空")
            return

        total = len(sub_segments)
        await _update_deck_status(deck_id, "splitting", 0, total, title=title)

        # --- 步骤3：切分音频 ---
        logger.info(f"[{deck_id}] Step3: 切分音频（{total} 段）")
        seg_results = await loop.run_in_executor(
            None, split_audio, audio_path, sub_segments, deck_id
        )

        # --- 步骤4：写入数据库 ---
        logger.info(f"[{deck_id}] Step4: 写入数据库")
        async with aiosqlite.connect(DB_PATH) as db:
            for i, seg in enumerate(seg_results):
                audio_url = get_audio_url(seg["id"], seg["audio_path"])
                await db.execute(
                    """INSERT OR REPLACE INTO segment
                       (id, deck_id, seg_index, audio_path, sentence, start_ms, end_ms)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (seg["id"], deck_id, seg["seg_index"],
                     seg["audio_path"], seg["sentence"],
                     seg["start_ms"], seg["end_ms"])
                )
                if (i + 1) % 20 == 0:
                    await db.commit()
                    await _update_deck_status(deck_id, "splitting", i + 1, total, title=title)
            await db.commit()

        await _update_deck_status(deck_id, "exporting", total, total, title=title)

        # --- 步骤5：生成 .apkg ---
        logger.info(f"[{deck_id}] Step5: 生成 .apkg")
        apkg_bytes = await loop.run_in_executor(
            None, generate_apkg, deck_id, title, seg_results
        )
        save_apkg(deck_id, apkg_bytes)

        # 完成
        await _update_deck_status(deck_id, "done", total, total, title=title)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE task SET status='done' WHERE id=?", (task_id,))
            await db.commit()

        logger.info(f"[{deck_id}] ✅ 处理完成！共 {total} 张卡片")

    except Exception as e:
        logger.exception(f"[{deck_id}] 流水线出错: {e}")
        await _update_deck_status(deck_id, "error", error_msg=str(e)[:200])
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE task SET status='error' WHERE id=?", (task_id,))
            await db.commit()
