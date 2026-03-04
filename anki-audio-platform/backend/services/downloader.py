"""
yt-dlp 封装：下载 YouTube 音频 + 字幕
"""
import os
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

STORAGE_DIR = os.environ.get("STORAGE_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "storage"))


def download_audio_and_subtitle(youtube_url: str, deck_id: str, lang: str = "en") -> dict:
    """
    下载 YouTube 音频和字幕。

    Returns:
        {
            "audio_path": "/path/to/audio.mp3",
            "subtitle_path": "/path/to/subtitle.vtt",  # 可能为 None
            "title": "视频标题",
            "lang": "en"
        }
    """
    output_dir = os.path.join(STORAGE_DIR, "raw", deck_id)
    os.makedirs(output_dir, exist_ok=True)

    audio_template = os.path.join(output_dir, "audio.%(ext)s")
    subtitle_template = os.path.join(output_dir, "subtitle")

    # 第一步：获取视频信息（标题）
    info_cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-playlist",
        youtube_url
    ]
    logger.info(f"[{deck_id}] 获取视频信息: {youtube_url}")
    result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=60)
    title = "Unknown"
    if result.returncode == 0:
        try:
            info = json.loads(result.stdout)
            title = info.get("title", "Unknown")
        except Exception:
            pass

    # 第二步：下载音频（转为 mp3）
    audio_cmd = [
        "yt-dlp",
        "-x",                            # 仅提取音频
        "--audio-format", "mp3",
        "--audio-quality", "0",          # 最高质量
        "--no-playlist",
        "-o", audio_template,
        youtube_url
    ]
    logger.info(f"[{deck_id}] 下载音频...")
    result = subprocess.run(audio_cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"音频下载失败: {result.stderr[:500]}")

    audio_path = os.path.join(output_dir, "audio.mp3")
    if not os.path.exists(audio_path):
        # 找一下其他可能的音频文件
        for f in os.listdir(output_dir):
            if f.startswith("audio."):
                audio_path = os.path.join(output_dir, f)
                break

    # 第三步：下载字幕（优先原始字幕，fallback 到自动字幕）
    subtitle_path = None
    sub_langs = f"{lang},{lang}-*,en,en-*"

    sub_cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-sub",           # 原始字幕
        "--write-auto-sub",      # 自动字幕（fallback）
        "--sub-lang", sub_langs,
        "--sub-format", "vtt",
        "--convert-subs", "vtt",
        "--no-playlist",
        "-o", subtitle_template,
        youtube_url
    ]
    logger.info(f"[{deck_id}] 下载字幕（语言: {lang}）...")
    result = subprocess.run(sub_cmd, capture_output=True, text=True, timeout=60)

    # 找字幕文件
    for f in os.listdir(output_dir):
        if f.startswith("subtitle") and f.endswith(".vtt"):
            subtitle_path = os.path.join(output_dir, f)
            break

    if subtitle_path is None:
        logger.warning(f"[{deck_id}] 未找到字幕文件，将无法切分片段")

    logger.info(f"[{deck_id}] 下载完成 | 音频: {audio_path} | 字幕: {subtitle_path}")

    return {
        "audio_path": audio_path,
        "subtitle_path": subtitle_path,
        "title": title,
        "lang": lang,
    }
