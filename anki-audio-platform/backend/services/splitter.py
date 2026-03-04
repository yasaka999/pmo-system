"""
音频切分服务：使用 pydub 按字幕时间轴切割音频
"""
import os
import uuid
import logging

logger = logging.getLogger(__name__)

STORAGE_DIR = os.environ.get("STORAGE_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "storage"))

# pydub 按需导入（需要 ffmpeg）
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub 未安装，音频切分不可用")


def split_audio(audio_path: str, segments: list[dict], deck_id: str, padding_ms: int = 100) -> list[dict]:
    """
    按字幕片段切分音频文件。

    Args:
        audio_path: 原始音频文件路径
        segments: 字幕片段列表 [{start_ms, end_ms, text}, ...]
        deck_id: 牌组ID（用于存储目录）
        padding_ms: 每段前后各增加的毫秒数（让音频更自然）

    Returns:
        [{id, seg_index, audio_path, sentence, start_ms, end_ms}, ...]
    """
    if not PYDUB_AVAILABLE:
        raise RuntimeError("pydub 未安装，请运行: pip install pydub")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_path}")

    output_dir = os.path.join(STORAGE_DIR, "segments", deck_id)
    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"[{deck_id}] 加载音频: {audio_path}")
    audio = AudioSegment.from_file(audio_path)
    audio_duration_ms = len(audio)

    results = []
    for idx, seg in enumerate(segments):
        start = max(0, seg["start_ms"] - padding_ms)
        end = min(audio_duration_ms, seg["end_ms"] + padding_ms)

        if end <= start:
            logger.warning(f"[{deck_id}] 跳过无效片段 {idx}: start={start}, end={end}")
            continue

        clip = audio[start:end]

        seg_id = str(uuid.uuid4()).replace("-", "")
        filename = f"{idx:04d}_{seg_id}.mp3"
        seg_path = os.path.join(output_dir, filename)

        # 导出为 mp3（128kbps 足够听力用途）
        clip.export(seg_path, format="mp3", bitrate="128k")

        results.append({
            "id": seg_id,
            "seg_index": idx,
            "audio_path": seg_path,
            "sentence": seg.get("text", ""),
            "start_ms": seg["start_ms"],
            "end_ms": seg["end_ms"],
        })

        if (idx + 1) % 10 == 0:
            logger.info(f"[{deck_id}] 切分进度: {idx + 1}/{len(segments)}")

    logger.info(f"[{deck_id}] 切分完成，共 {len(results)} 个片段")
    return results
