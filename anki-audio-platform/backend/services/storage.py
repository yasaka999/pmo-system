"""
存储服务：MVP 阶段使用本地文件存储
提供统一接口，后续可替换为 OSS
"""
import os
import shutil
import logging

logger = logging.getLogger(__name__)

STORAGE_DIR = os.environ.get("STORAGE_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "storage"))

# 服务器基础 URL（用于生成可访问的音频 URL）
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def get_audio_url(segment_id: str, audio_path: str) -> str:
    """
    生成音频文件的可访问 URL。
    MVP 阶段直接返回本地服务的静态文件 URL。
    后续可替换为 OSS 签名 URL。
    """
    # 计算相对于 STORAGE_DIR 的相对路径
    try:
        rel_path = os.path.relpath(audio_path, STORAGE_DIR)
    except ValueError:
        rel_path = os.path.basename(audio_path)

    return f"{BASE_URL}/storage/{rel_path}"


def save_apkg(deck_id: str, apkg_data: bytes) -> str:
    """
    保存生成的 .apkg 文件，返回本地路径。
    """
    apkg_dir = os.path.join(STORAGE_DIR, "apkg")
    os.makedirs(apkg_dir, exist_ok=True)
    apkg_path = os.path.join(apkg_dir, f"{deck_id}.apkg")
    with open(apkg_path, "wb") as f:
        f.write(apkg_data)
    logger.info(f"apkg 已保存: {apkg_path}")
    return apkg_path


def get_apkg_path(deck_id: str) -> str | None:
    """获取已生成的 apkg 文件路径"""
    path = os.path.join(STORAGE_DIR, "apkg", f"{deck_id}.apkg")
    return path if os.path.exists(path) else None


def cleanup_raw(deck_id: str):
    """清理原始下载文件（处理完成后可释放空间）"""
    raw_dir = os.path.join(STORAGE_DIR, "raw", deck_id)
    if os.path.exists(raw_dir):
        shutil.rmtree(raw_dir)
        logger.info(f"已清理原始文件: {raw_dir}")
