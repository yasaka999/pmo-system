"""
字幕文件解析：支持 .vtt 和 .srt 格式
返回统一的片段列表：[{start_ms, end_ms, text}, ...]
"""
import re
import logging

logger = logging.getLogger(__name__)


def parse_vtt(vtt_path: str) -> list[dict]:
    """解析 WebVTT 字幕文件"""
    segments = []
    try:
        with open(vtt_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"无法读取字幕文件 {vtt_path}: {e}")
        return []

    # 移除 NOTE、STYLE 等块
    content = re.sub(r'NOTE[^\n]*\n.*?(?=\n\n|\Z)', '', content, flags=re.DOTALL)
    content = re.sub(r'STYLE[^\n]*\n.*?(?=\n\n|\Z)', '', content, flags=re.DOTALL)

    # 解析时间轴行：00:00:01.000 --> 00:00:05.000
    pattern = re.compile(
        r'(\d{1,2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[.,]\d{3})[^\n]*\n(.*?)(?=\n\n|\Z)',
        re.DOTALL
    )

    for match in pattern.finditer(content):
        start_str, end_str, text = match.groups()
        text = _clean_text(text)
        if not text:
            continue
        segments.append({
            "start_ms": _time_to_ms(start_str),
            "end_ms": _time_to_ms(end_str),
            "text": text,
        })

    logger.info(f"VTT 解析完成：{vtt_path}，共 {len(segments)} 段")
    return _merge_short_segments(segments)


def parse_srt(srt_path: str) -> list[dict]:
    """解析 SRT 字幕文件"""
    segments = []
    try:
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"无法读取字幕文件 {srt_path}: {e}")
        return []

    pattern = re.compile(
        r'\d+\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)',
        re.DOTALL
    )
    for match in pattern.finditer(content):
        start_str, end_str, text = match.groups()
        text = _clean_text(text)
        if not text:
            continue
        segments.append({
            "start_ms": _time_to_ms(start_str),
            "end_ms": _time_to_ms(end_str),
            "text": text,
        })

    logger.info(f"SRT 解析完成：{srt_path}，共 {len(segments)} 段")
    return _merge_short_segments(segments)


def parse_subtitle(path: str) -> list[dict]:
    """自动判断字幕格式并解析"""
    if path.endswith(".vtt"):
        return parse_vtt(path)
    elif path.endswith(".srt"):
        return parse_srt(path)
    else:
        logger.warning(f"不支持的字幕格式: {path}")
        return []


def _time_to_ms(time_str: str) -> int:
    """将时间字符串转换为毫秒"""
    time_str = time_str.replace(",", ".")
    parts = time_str.split(":")
    if len(parts) == 3:
        h, m, s = parts
        s, ms = s.split(".") if "." in s else (s, "0")
        return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms[:3].ljust(3, "0"))
    elif len(parts) == 2:
        m, s = parts
        s, ms = s.split(".") if "." in s else (s, "0")
        return (int(m) * 60 + int(s)) * 1000 + int(ms[:3].ljust(3, "0"))
    return 0


def _clean_text(text: str) -> str:
    """清理字幕文本：去除 HTML 标签、位置标记等"""
    text = re.sub(r'<[^>]+>', '', text)           # 去除 HTML 标签
    text = re.sub(r'\{[^}]+\}', '', text)          # 去除 ASS 样式
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'\n+', ' ', text)
    return text.strip()


def _merge_short_segments(segments: list[dict]) -> list[dict]:
    """
    按句子边界合并字幕片段，每个句子一个卡片
    """
    if not segments:
        return []
    
    # 句子结束标点
    sentence_enders = ('.', '!', '?', '。', '！', '？')
    
    merged = []
    current = None
    
    for seg in segments:
        if current is None:
            current = seg.copy()
            continue
        
        text = seg["text"].strip()
        current_text = current["text"].strip()
        
        # 当前片段以句子结束标点结尾 → 结束合并
        if current_text.endswith(sentence_enders):
            merged.append(current)
            current = seg.copy()
        else:
            # 继续合并
            current["end_ms"] = seg["end_ms"]
            current["text"] = current_text + " " + text
    
    # 添加最后一个片段
    if current:
        merged.append(current)
    
    logger.info(f"字幕片段合并：{len(segments)} → {len(merged)} 段")
    return merged
