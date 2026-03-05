"""
API: GET /card/{card_id}?side=0|1
服务端渲染卡片页面（被 Anki iframe 加载）
"""
import os
import logging
import json
import aiosqlite
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

from backend.db import DB_PATH
from backend.services.storage import get_audio_url
from backend.services.dictionary import annotate_sentence, lookup_word

logger = logging.getLogger(__name__)
router = APIRouter()

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

# 默认缩略图 (base64 编码的简单音符图标)
DEFAULT_THUMBNAIL = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMjgiIGhlaWdodD0iMTI4IiB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9IiM0YTkwZTIiPjxwYXRoIGQ9Ik0xMiAzdjEwLjU1Yy0uNTktLjM0LTEuMjctLjU1LTItLjU1LTIuMjEgMC00IDEuNzktNCA0czEuNzkgNCA0IDQgNC0xLjc5IDQtNGMwLS4zNi0uMDUtLjcxLS4xNC0xLjA1TDE1IDE1LjlWMTJsMy0xVjdsLTMgMXYtNXoiLz48L3N2Zz4="


def _render_card_page(sentence: str, audio_url: str, side: int, title: str = None, 
                       thumbnail_url: str = None, words_data: list = None) -> str:
    """渲染 Anki iframe 加载的 HTML 页面 - 播放器样式"""
    
    show_sentence = side == 1
    is_looping = "true" if side == 0 else "false"  # 正面循环播放，背面不循环
    
    # 缩略图URL
    thumb = thumbnail_url or DEFAULT_THUMBNAIL
    
    # 标题（显示在播放器上）
    display_title = title or "AnkiAudio"
    
    # 处理单词标注
    annotated_sentence = sentence
    words_json = "[]"
    if words_data:
        words_json = json.dumps(words_data, ensure_ascii=False)

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
    background: #f5f5f7;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 16px;
    transition: background 0.3s;
  }}
  body.dark {{ background: #1a1a1a; }}

  .player-card {{
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    padding: 20px;
    width: 100%;
    max-width: 360px;
    transition: background 0.3s, box-shadow 0.3s;
  }}
  body.dark .player-card {{ background: #2a2a2a; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}

  .player-top {{
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;
  }}

  .thumbnail-wrap {{
    position: relative;
    width: 64px;
    height: 64px;
    flex-shrink: 0;
    border-radius: 50%;
    overflow: hidden;
  }}

  .thumbnail {{
    width: 64px;
    height: 64px;
    border-radius: 50%;
    object-fit: cover;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }}

  .thumbnail.spinning {{
    animation: spin 3s linear infinite;
  }}

  @keyframes spin {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
  }}

  .play-overlay {{
    position: absolute;
    top: 0;
    left: 0;
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.2s;
  }}
  .play-overlay:hover {{ background: rgba(0,0,0,0.4); }}
  .play-overlay svg {{
    width: 28px;
    height: 28px;
    fill: #fff;
    transition: transform 0.15s;
  }}
  .play-overlay:active svg {{ transform: scale(0.9); }}

  .info-section {{
    flex: 1;
    min-width: 0;
  }}

  .card-title {{
    font-size: 13px;
    color: #888;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 4px;
  }}
  body.dark .card-title {{ color: #aaa; }}

  .time-display {{
    font-size: 28px;
    font-weight: 600;
    color: #333;
    font-variant-numeric: tabular-nums;
  }}
  body.dark .time-display {{ color: #f0f0f0; }}

  .duration-display {{
    font-size: 13px;
    color: #888;
    margin-top: 2px;
  }}
  body.dark .duration-display {{ color: #aaa; }}

  .progress-section {{
    margin-bottom: 12px;
  }}

  .progress-bar {{
    width: 100%;
    height: 6px;
    background: #e0e0e0;
    border-radius: 3px;
    overflow: hidden;
    cursor: pointer;
    position: relative;
  }}
  body.dark .progress-bar {{ background: #404040; }}

  .progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, #4a90e2, #667eea);
    width: 0%;
    transition: width 0.1s linear;
    border-radius: 3px;
  }}

  .progress-thumb {{
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 14px;
    height: 14px;
    background: #fff;
    border: 2px solid #4a90e2;
    border-radius: 50%;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    opacity: 0;
    transition: opacity 0.2s;
  }}
  .progress-bar:hover .progress-thumb {{ opacity: 1; }}

  .controls {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
  }}

  .speed-btn {{
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border: 1px solid #ddd;
    border-radius: 20px;
    background: #fff;
    color: #666;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
  }}
  body.dark .speed-btn {{ background: #333; border-color: #555; color: #aaa; }}
  .speed-btn:hover {{ border-color: #4a90e2; color: #4a90e2; }}

  .speed-menu {{
    position: absolute;
    bottom: 100%;
    left: 0;
    margin-bottom: 8px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    padding: 8px 0;
    display: none;
    z-index: 10;
    min-width: 100px;
  }}
  body.dark .speed-menu {{ background: #333; }}
  .speed-menu.show {{ display: block; }}

  .speed-option {{
    padding: 8px 16px;
    cursor: pointer;
    font-size: 14px;
    color: #333;
    transition: background 0.15s;
  }}
  body.dark .speed-option {{ color: #ddd; }}
  .speed-option:hover {{ background: #f5f5f5; }}
  body.dark .speed-option:hover {{ background: #404040; }}
  .speed-option.active {{
    background: #4a90e2;
    color: #fff;
  }}

  .main-controls {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .ctrl-btn {{
    width: 40px;
    height: 40px;
    border: none;
    border-radius: 50%;
    background: transparent;
    color: #666;
    font-size: 18px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
  }}
  body.dark .ctrl-btn {{ color: #aaa; }}
  .ctrl-btn:hover {{ background: #f0f0f0; color: #4a90e2; }}
  body.dark .ctrl-btn:hover {{ background: #404040; }}

  .play-btn {{
    width: 52px;
    height: 52px;
    background: linear-gradient(135deg, #4a90e2 0%, #667eea 100%);
    color: #fff;
    box-shadow: 0 4px 15px rgba(74,144,226,0.4);
  }}
  .play-btn:hover {{
    transform: scale(1.05);
    background: linear-gradient(135deg, #5a9ff2 0%, #7688f0 100%);
    box-shadow: 0 6px 20px rgba(74,144,226,0.5);
  }}
  .play-btn:active {{ transform: scale(0.95); }}

  .sentence-block {{
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #eee;
    animation: fadeIn 0.4s ease;
  }}
  body.dark .sentence-block {{ border-color: #404040; }}

  .sentence-text {{
    font-size: 15px;
    line-height: 1.7;
    color: #333;
    text-align: center;
  }}
  body.dark .sentence-text {{ color: #f0f0f0; }}

  /* 单词标注样式 */
  .word-tip {{
    text-decoration: underline;
    text-decoration-color: #4a90e2;
    text-decoration-style: dotted;
    text-underline-offset: 3px;
    cursor: pointer;
    color: #4a90e2;
    transition: all 0.2s;
  }}
  .word-tip:hover {{
    background: rgba(74, 144, 226, 0.1);
  }}

  /* 单词解释弹窗 */
  .word-popup {{
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    padding: 16px 20px;
    max-width: 320px;
    width: 90%;
    z-index: 100;
    display: none;
    animation: slideUp 0.3s ease;
  }}
  body.dark .word-popup {{ background: #2a2a2a; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
  .word-popup.show {{ display: block; }}

  @keyframes slideUp {{
    from {{ opacity: 0; transform: translateX(-50%) translateY(20px); }}
    to {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
  }}

  .popup-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }}

  .popup-word {{
    font-size: 20px;
    font-weight: 600;
    color: #333;
  }}
  body.dark .popup-word {{ color: #f0f0f0; }}

  .popup-phonetic {{
    font-size: 14px;
    color: #888;
    margin-left: 8px;
  }}
  body.dark .popup-phonetic {{ color: #aaa; }}

  .popup-close {{
    background: none;
    border: none;
    font-size: 20px;
    color: #888;
    cursor: pointer;
    padding: 4px;
    line-height: 1;
  }}
  .popup-close:hover {{ color: #333; }}
  body.dark .popup-close:hover {{ color: #f0f0f0; }}

  .popup-pos {{
    display: inline-block;
    background: #e8f0fe;
    color: #4a90e2;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 10px;
    margin-bottom: 8px;
  }}
  body.dark .popup-pos {{ background: #3a4a5a; }}

  .popup-definition {{
    font-size: 14px;
    color: #333;
    line-height: 1.5;
    margin-bottom: 8px;
  }}
  body.dark .popup-definition {{ color: #ddd; }}

  .popup-example {{
    font-size: 13px;
    color: #666;
    font-style: italic;
    padding-left: 12px;
    border-left: 2px solid #ddd;
  }}
  body.dark .popup-example {{ color: #aaa; border-color: #555; }}

  @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
</style>
</head>
<body id="body">
<div class="player-card">
  <div class="player-top">
    <div class="thumbnail-wrap">
      <img class="thumbnail" id="thumbnail" src="{thumb}" alt="cover">
      <div class="play-overlay" onclick="togglePlay()">
        <svg id="playIcon" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
      </div>
    </div>
    <div class="info-section">
      <div class="card-title">{display_title}</div>
      <div class="time-display" id="timeDisplay">0:00</div>
      <div class="duration-display" id="durationDisplay">/ 0:00</div>
    </div>
  </div>

  <div class="progress-section">
    <div class="progress-bar" id="progressBar" onclick="seek(event)">
      <div class="progress-fill" id="progress"></div>
      <div class="progress-thumb" id="progressThumb"></div>
    </div>
  </div>

  <div class="controls">
    <div style="position: relative;">
      <button class="speed-btn" id="speedBtn" onclick="toggleSpeedMenu()">
        <span id="speedLabel">1x</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M7 10l5 5 5-5z"/></svg>
      </button>
      <div class="speed-menu" id="speedMenu">
        <div class="speed-option" data-speed="0.5" onclick="setSpeed(0.5)">0.5x</div>
        <div class="speed-option" data-speed="0.75" onclick="setSpeed(0.75)">0.75x</div>
        <div class="speed-option active" data-speed="1" onclick="setSpeed(1)">1x</div>
        <div class="speed-option" data-speed="1.25" onclick="setSpeed(1.25)">1.25x</div>
        <div class="speed-option" data-speed="2" onclick="setSpeed(2)">2x</div>
      </div>
    </div>

    <div class="main-controls">
      <button class="ctrl-btn" onclick="skipBack()" title="后退5秒">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>
      </button>
      <button class="ctrl-btn play-btn" id="playBtn" onclick="togglePlay()" title="播放">
        <svg id="btnIcon" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
      </button>
      <button class="ctrl-btn" onclick="skipForward()" title="前进5秒">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 5V1l5 5-5 5V7c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6h2c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8z"/></svg>
      </button>
    </div>

    <div style="width: 70px;"></div>
  </div>

  <div class="sentence-block" id="sentenceBlock" style="display: {'block' if show_sentence else 'none'};">
    <p class="sentence-text" id="sentenceText">{sentence}</p>
  </div>
</div>

<!-- 单词解释弹窗 -->
<div class="word-popup" id="wordPopup">
  <div class="popup-header">
    <div>
      <span class="popup-word" id="popupWord">word</span>
      <span class="popup-phonetic" id="popupPhonetic"></span>
    </div>
    <button class="popup-close" onclick="closePopup()">×</button>
  </div>
  <div class="popup-pos" id="popupPos"></div>
  <div class="popup-definition" id="popupDefinition"></div>
  <div class="popup-example" id="popupExample"></div>
</div>

<audio id="audio" src="{audio_url}" preload="auto"></audio>

<script>
const audio = document.getElementById('audio');
const progress = document.getElementById('progress');
const progressThumb = document.getElementById('progressThumb');
const timeDisplay = document.getElementById('timeDisplay');
const durationDisplay = document.getElementById('durationDisplay');
const playBtn = document.getElementById('playBtn');
const playIcon = document.getElementById('playIcon');
const btnIcon = document.getElementById('btnIcon');
const thumbnail = document.getElementById('thumbnail');
const speedMenu = document.getElementById('speedMenu');
const speedLabel = document.getElementById('speedLabel');
var isLooping = {is_looping};
var currentSpeed = 1;

function formatTime(seconds) {{
  if (!seconds || isNaN(seconds)) return '0:00';
  var mins = Math.floor(seconds / 60);
  var secs = Math.floor(seconds % 60);
  return mins + ':' + (secs < 10 ? '0' : '') + secs;
}}

audio.addEventListener('loadedmetadata', function() {{
  durationDisplay.textContent = '/ ' + formatTime(audio.duration);
}});

audio.addEventListener('timeupdate', function() {{
  if (audio.duration) {{
    var pct = (audio.currentTime / audio.duration * 100);
    progress.style.width = pct + '%';
    progressThumb.style.left = pct + '%';
    timeDisplay.textContent = formatTime(audio.currentTime);
  }}
}});

audio.addEventListener('play', function() {{
  playIcon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';
  btnIcon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';
  thumbnail.classList.add('spinning');
}});

audio.addEventListener('pause', function() {{
  playIcon.innerHTML = '<path d="M8 5v14l11-7z"/>';
  btnIcon.innerHTML = '<path d="M8 5v14l11-7z"/>';
  thumbnail.classList.remove('spinning');
}});

audio.addEventListener('ended', function() {{
  if (isLooping) {{
    audio.currentTime = 0;
    audio.play();
  }} else {{
    playIcon.innerHTML = '<path d="M8 5v14l11-7z"/>';
    btnIcon.innerHTML = '<path d="M8 5v14l11-7z"/>';
    thumbnail.classList.remove('spinning');
    progress.style.width = '0%';
    timeDisplay.textContent = '0:00';
  }}
}});

function togglePlay() {{
  if (audio.paused) {{
    audio.play();
  }} else {{
    audio.pause();
  }}
}}

function seek(e) {{
  var rect = e.currentTarget.getBoundingClientRect();
  var pct = (e.clientX - rect.left) / rect.width;
  audio.currentTime = pct * audio.duration;
}}

function skipBack() {{
  audio.currentTime = Math.max(0, audio.currentTime - 5);
}}

function skipForward() {{
  audio.currentTime = Math.min(audio.duration, audio.currentTime + 5);
}}

function toggleSpeedMenu() {{
  speedMenu.classList.toggle('show');
}}

function setSpeed(speed) {{
  currentSpeed = speed;
  audio.playbackRate = speed;
  speedLabel.textContent = speed + 'x';
  speedMenu.classList.remove('show');
  
  // 更新选中状态
  document.querySelectorAll('.speed-option').forEach(function(opt) {{
    opt.classList.remove('active');
    if (parseFloat(opt.dataset.speed) === speed) {{
      opt.classList.add('active');
    }}
  }});
}}

// 点击其他地方关闭菜单
document.addEventListener('click', function(e) {{
  if (!e.target.closest('.speed-btn') && !e.target.closest('.speed-menu')) {{
    speedMenu.classList.remove('show');
  }}
}});

// 单词标注数据
var wordsData = {words_json};

// 初始化单词标注
function initWordTips() {{
  if (!wordsData || wordsData.length === 0) return;
  
  var sentenceEl = document.getElementById('sentenceText');
  var sentence = sentenceEl.textContent;
  var html = sentence;
  
  // 按位置排序，从后往前替换
  var sorted = wordsData.slice().sort(function(a, b) {{ return b.start - a.start; }});
  
  sorted.forEach(function(w) {{
    var original = sentence.substring(w.start, w.end);
    var tipData = encodeURIComponent(JSON.stringify(w.data));
    var span = '<span class="word-tip" data-word="' + tipData + '">' + original + '</span>';
    html = html.substring(0, w.start) + span + html.substring(w.end);
  }});
  
  sentenceEl.innerHTML = html;
  
  // 绑定点击事件
  document.querySelectorAll('.word-tip').forEach(function(el) {{
    el.addEventListener('click', function(e) {{
      e.stopPropagation();
      showWordPopup(this);
    }});
  }});
}}

function showWordPopup(el) {{
  var data = JSON.parse(decodeURIComponent(el.dataset.word));
  
  document.getElementById('popupWord').textContent = data.word || '';
  document.getElementById('popupPhonetic').textContent = data.phonetic || '';
  document.getElementById('popupPos').textContent = data.pos || '';
  
  // 优先中文释义，其次英文
  var definition = data.definition_cn || data.definition_en || '';
  document.getElementById('popupDefinition').textContent = definition;
  
  document.getElementById('popupExample').textContent = data.example || '';
  
  document.getElementById('wordPopup').classList.add('show');
}}

function closePopup() {{
  document.getElementById('wordPopup').classList.remove('show');
}}

// 点击其他地方关闭弹窗
document.addEventListener('click', function(e) {{
  if (!e.target.closest('.word-tip') && !e.target.closest('.word-popup')) {{
    closePopup();
  }}
}});

// 自动播放
window.addEventListener('load', function() {{
  audio.play().catch(function() {{
    // 自动播放被浏览器限制
  }});
  applyDarkMode();
  initWordTips();
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
        # 获取卡片信息和牌组缩略图、标题、单词数据
        async with db.execute(
            """SELECT s.id, s.audio_path, s.sentence, s.words, d.thumbnail, d.title, d.lang_cd
               FROM segment s 
               JOIN deck d ON s.deck_id = d.id 
               WHERE s.id=?""", 
            (card_id,)
        ) as cursor:
            seg = await cursor.fetchone()

    if not seg:
        raise HTTPException(404, "卡片不存在")

    audio_url = get_audio_url(seg["id"], seg["audio_path"])
    sentence = seg["sentence"] or ""
    thumbnail = seg["thumbnail"]
    title = seg["title"]
    lang = seg["lang_cd"] or "en"
    
    # 解析单词数据
    words_data = None
    if seg["words"]:
        try:
            words_data = json.loads(seg["words"])
        except:
            pass
    
    # 如果没有预存的单词数据，实时查询（仅背面）
    if not words_data and side == 1 and sentence:
        try:
            annotated = await annotate_sentence(sentence, lang)
            words_data = annotated.get("words", [])
        except Exception as e:
            logger.warning(f"单词标注失败: {e}")
    
    # 如果有缩略图，构建URL
    thumbnail_url = None
    if thumbnail:
        thumbnail_url = f"{BASE_URL}/card/thumbnail/{seg['id']}"
    
    html = _render_card_page(sentence, audio_url, side, title, thumbnail_url, words_data)
    return HTMLResponse(content=html)


@router.get("/word/{word}")
async def lookup_word_api(word: str, lang: str = "en"):
    """查询单词解释API"""
    result = await lookup_word(word, lang)
    if not result:
        raise HTTPException(404, f"未找到单词: {word}")
    return JSONResponse(content=result)


@router.get("/card/thumbnail/{card_id}")
async def get_thumbnail(card_id: str):
    """获取卡片对应的牌组缩略图"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT d.thumbnail FROM segment s 
               JOIN deck d ON s.deck_id = d.id 
               WHERE s.id=?""", 
            (card_id,)
        ) as cursor:
            row = await cursor.fetchone()
    
    if not row or not row["thumbnail"]:
        raise HTTPException(404, "缩略图不存在")
    
    thumbnail_path = row["thumbnail"]
    if not os.path.exists(thumbnail_path):
        raise HTTPException(404, "缩略图文件不存在")
    
    return FileResponse(thumbnail_path, media_type="image/jpeg")