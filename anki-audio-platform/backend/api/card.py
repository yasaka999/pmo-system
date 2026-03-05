"""
API: GET /card/{card_id}?side=0|1
服务端渲染卡片页面（被 Anki iframe 加载）
"""
import os
import logging
import aiosqlite
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from backend.db import DB_PATH
from backend.services.storage import get_audio_url

logger = logging.getLogger(__name__)
router = APIRouter()

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def _render_card_page(sentence: str, audio_url: str, side: int) -> str:
    """渲染 Anki iframe 加载的 HTML 页面"""
    
    show_sentence = side == 1
    is_looping = "true" if side == 0 else "false"  # 正面循环播放，背面不循环
    sentence_block = f"""
    <div class="sentence-block">
      <p class="sentence-text">{sentence}</p>
    </div>
""" if show_sentence else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AnkiAudio Card</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 20px;
    transition: background 0.3s;
  }}
  body.dark {{ background: #303030; color: #ffffff; }}

  .player-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    width: 100%;
    max-width: 500px;
  }}

  .play-btn {{
    width: 80px; height: 80px;
    border-radius: 50%;
    border: none;
    background: #4a90e2;
    color: white;
    font-size: 32px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 12px rgba(74,144,226,0.4);
    transition: transform 0.15s, box-shadow 0.15s;
  }}
  .play-btn:active {{ transform: scale(0.93); }}
  .play-btn.playing {{ background: #e25f4a; }}

  .progress-bar {{
    width: 100%;
    height: 4px;
    background: #e0e0e0;
    border-radius: 2px;
    overflow: hidden;
  }}
  .progress-fill {{
    height: 100%;
    background: #4a90e2;
    width: 0%;
    transition: width 0.1s linear;
  }}

  .sentence-block {{
    margin-top: 24px;
    padding: 16px 20px;
    border-top: 2px solid #e0e0e0;
    width: 100%;
    max-width: 500px;
    animation: fadeIn 0.4s ease;
  }}
  .sentence-text {{
    font-size: 1.2em;
    line-height: 1.7;
    color: #333;
    text-align: center;
  }}
  body.dark .sentence-text {{ color: #f0f0f0; }}
  body.dark .sentence-block {{ border-color: #555; }}

  @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
</style>
</head>
<body id="body">
<div class="player-wrap">
  <button class="play-btn" id="playBtn" onclick="togglePlay()" title="播放">▶</button>
  <div class="progress-bar">
    <div class="progress-fill" id="progress"></div>
  </div>
</div>
{sentence_block}

<audio id="audio" src="{audio_url}" preload="auto"></audio>

<script>
const audio = document.getElementById('audio');
const btn = document.getElementById('playBtn');
const prog = document.getElementById('progress');
var isLooping = {is_looping};

audio.addEventListener('timeupdate', function() {{
  if (audio.duration) {{
    prog.style.width = (audio.currentTime / audio.duration * 100) + '%';
  }}
}});
audio.addEventListener('ended', function() {{
  if (isLooping) {{
    audio.currentTime = 0;
    audio.play();
  }} else {{
    btn.textContent = '▶';
    btn.classList.remove('playing');
    prog.style.width = '0%';
  }}
}});

function togglePlay() {{
  if (audio.paused) {{
    audio.play();
    btn.textContent = '⏸';
    btn.classList.add('playing');
  }} else {{
    audio.pause();
    btn.textContent = '▶';
    btn.classList.remove('playing');
  }}
}}

// 自动播放
window.addEventListener('load', function() {{
  audio.play().then(function() {{
    btn.textContent = '⏸'; btn.classList.add('playing');
  }}).catch(function() {{
    // 自动播放被浏览器限制，等待用户点击
  }});
  applyDarkMode();
}});

function applyDarkMode() {{
  try {{
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '{BASE_URL}/deck/prefer/default/', false);
    xhr.send();
    if (xhr.status === 200) {{
      let pref = JSON.parse(xhr.responseText);
      if (pref.dark_mode) document.getElementById('body').classList.add('dark');
    }}
  }} catch(e) {{}}
}}
</script>
</body>
</html>"""


@router.get("/card/{card_id}", response_class=HTMLResponse)
async def get_card(card_id: str, side: int = Query(0, ge=0, le=1)):
    """渲染卡片页面（side=0 正面，side=1 背面）"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, audio_path, sentence FROM segment WHERE id=?", (card_id,)
        ) as cursor:
            seg = await cursor.fetchone()

    if not seg:
        raise HTTPException(404, "卡片不存在")

    audio_url = get_audio_url(seg["id"], seg["audio_path"])
    sentence = seg["sentence"] or ""
    html = _render_card_page(sentence, audio_url, side)
    return HTMLResponse(content=html)
