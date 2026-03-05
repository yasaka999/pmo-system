"""
yt-dlp 封装：下载 YouTube 音频 + 字幕
"""
import os
import re
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

STORAGE_DIR = os.environ.get("STORAGE_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "storage"))

# yt-dlp 和 deno 路径
YTDLP_PATH = os.environ.get("YTDLP_PATH", "/root/anki-audio-platform-app/venv/bin/yt-dlp")
DENO_PATH = os.environ.get("DENO_PATH", "/root/.deno/bin")
FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "/root/.local/bin/ffmpeg")


def normalize_youtube_url(url: str) -> str:
    """
    规范化 YouTube URL，提取并验证视频 ID。
    YouTube 视频 ID 应该是 11 个字符。
    """
    # 提取视频 ID 的正则模式
    patterns = [
        r'(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',  # 标准格式
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',              # 短链接
        r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})',     # 嵌入格式
        r'(?:youtube\.com/v/)([a-zA-Z0-9_-]{11})',         # 旧格式
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}"
    
    # 如果没有匹配到完整的 11 字符 ID，尝试提取部分 ID 并提示
    partial_match = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', url)
    if partial_match:
        video_id = partial_match.group(1)
        if len(video_id) < 11:
            raise ValueError(f"YouTube 视频 ID 不完整: {video_id} (应为 11 字符，实际 {len(video_id)} 字符)。请检查 URL 是否被截断。")
    
    # 尝试直接使用原始 URL
    return url


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
    # 规范化 URL，验证视频 ID
    youtube_url = normalize_youtube_url(youtube_url)
    logger.info(f"[{deck_id}] 规范化 URL: {youtube_url}")
    
    output_dir = os.path.join(STORAGE_DIR, "raw", deck_id)
    os.makedirs(output_dir, exist_ok=True)

    audio_template = os.path.join(output_dir, "audio.%(ext)s")
    subtitle_template = os.path.join(output_dir, "subtitle")

    # 设置环境变量，包含 deno 和 ffmpeg 路径
    env = os.environ.copy()
    env["PATH"] = f"{DENO_PATH}:{os.path.dirname(FFMPEG_PATH)}:{env.get('PATH', '')}"

    # 第一步：获取视频信息（标题）
    info_cmd = [
        YTDLP_PATH,
        "--dump-json",
        "--no-playlist",
        "--remote-components", "ejs:github",
        youtube_url
    ]
    logger.info(f"[{deck_id}] 获取视频信息: {youtube_url}")
    result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=60, env=env)
    title = "Unknown"
    if result.returncode == 0:
        try:
            info = json.loads(result.stdout)
            title = info.get("title", "Unknown")
        except Exception:
            pass

    # 第二步：下载音频（转为 mp3）
    audio_cmd = [
        YTDLP_PATH,
        "-x",                            # 仅提取音频
        "--audio-format", "mp3",
        "--audio-quality", "0",          # 最高质量
        "--no-playlist",
        "--remote-components", "ejs:github",
        "-o", audio_template,
        youtube_url
    ]
    logger.info(f"[{deck_id}] 下载音频...")
    result = subprocess.run(audio_cmd, capture_output=True, text=True, timeout=300, env=env)
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
        YTDLP_PATH,
        "--skip-download",
        "--write-sub",           # 原始字幕
        "--write-auto-sub",      # 自动字幕（fallback）
        "--sub-lang", sub_langs,
        "--sub-format", "vtt",
        "--convert-subs", "vtt",
        "--no-playlist",
        "--remote-components", "ejs:github",
        "-o", subtitle_template,
        youtube_url
    ]
    logger.info(f"[{deck_id}] 下载字幕（语言: {lang}）...")
    result = subprocess.run(sub_cmd, capture_output=True, text=True, timeout=60, env=env)

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
