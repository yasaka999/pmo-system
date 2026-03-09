# AnkiAudio Platform 项目图谱

> 由 GitNexus 自动生成 | 2026-03-08

## 📊 项目概览

| 指标 | 数值 |
|------|------|
| 文件数 | 19 |
| 代码节点 | 77 |
| 关系边 | 149 |
| 功能模块 | 9 |
| 执行流程 | 8 |

---

## 🏗️ 项目架构

```
anki-audio-platform/
├── backend/
│   ├── main.py              # FastAPI 应用入口
│   ├── db.py                # 数据库初始化
│   ├── api/                 # API 路由层
│   │   ├── card.py          # 卡片相关 API
│   │   ├── export.py        # 导出 API
│   │   └── process.py       # 处理流程 API
│   ├── services/            # 业务服务层
│   │   ├── dictionary.py    # 词典查询服务
│   │   ├── downloader.py    # YouTube 下载服务
│   │   ├── subtitle.py      # 字幕解析服务
│   │   ├── splitter.py      # 音频分割服务
│   │   ├── anki_export.py   # Anki 导出服务
│   │   ├── pipeline.py      # 处理管道
│   │   └── storage.py       # 存储服务
│   └── static/
│       └── index.html        # 前端页面
├── data/                    # 数据目录
├── README.md
└── ROADMAP.md
```

---

## 🔗 核心调用关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer                                 │
├─────────────────────────────────────────────────────────────────┤
│  main.py                                                        │
│  └── lifespan() → init_db()                                     │
│                                                                 │
│  card.py                                                        │
│  ├── get_card() → _render_card_page()                           │
│  │              → get_audio_url()                               │
│  │              → annotate_sentence()                            │
│  └── lookup_word_api() → lookup_word()                          │
│                                                                 │
│  export.py                                                      │
│  └── export_anki() → get_apkg_path()                            │
│                                                                 │
│  process.py                                                      │
│  ├── get_status()                                               │
│  └── list_decks()                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Services Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  dictionary.py (词典服务)                                        │
│  ├── lookup_word() → lookup_word_youdao()                       │
│  │                 → lookup_word_free()                          │
│  ├── lookup_word_youdao()    # 有道词典 API                     │
│  ├── lookup_word_free()       # 免费词典 API                    │
│  ├── extract_difficult_words() # 提取难词                        │
│  └── annotate_sentence() → extract_difficult_words()            │
│                          → lookup_word()                         │
│                                                                 │
│  downloader.py (下载服务)                                        │
│  └── download_audio_and_subtitle() → normalize_youtube_url()    │
│                                                                 │
│  subtitle.py (字幕解析)                                          │
│  ├── parse_subtitle() → parse_srt()                             │
│  │                      → parse_vtt()                            │
│  ├── parse_srt() → _time_to_ms()                                │
│  │               → _clean_text()                                │
│  │               → _merge_short_segments()                      │
│  └── parse_vtt() → _time_to_ms()                                │
│                  → _clean_text()                                │
│                  → _merge_short_segments()                      │
│                                                                 │
│  anki_export.py (Anki 导出)                                      │
│  └── generate_apkg() → _get_model()                             │
│                                                                 │
│  pipeline.py (处理管道)                                          │
│  └── run_pipeline() → _update_deck_status()                     │
│                      → save_apkg()                               │
│                      → get_audio_url()                           │
│                                                                 │
│  storage.py (存储服务)                                            │
│  ├── get_audio_url()                                            │
│  ├── get_apkg_path()                                            │
│  └── cleanup_raw()                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 执行流程 (Processes)

| 流程 | 描述 |
|------|------|
| **Get_card → Lookup_word_youdao** | 获取卡片 → 有道词典查词 |
| **Get_card → Lookup_word_free** | 获取卡片 → 免费词典查词 |
| **Get_card → Extract_difficult_words** | 获取卡片 → 提取难词 |
| **Lookup_word_api → Lookup_word_youdao** | 查词 API → 有道词典 |
| **Lookup_word_api → Lookup_word_free** | 查词 API → 免费词典 |
| **Parse_subtitle → _clean_text** | 字幕解析 → 文本清理 |
| **Parse_subtitle → _merge_short_segments** | 字幕解析 → 合并短片段 |
| **Parse_subtitle → _time_to_ms** | 字幕解析 → 时间转换 |

---

## 📁 文件清单

### API 层 (`backend/api/`)

| 文件 | 函数数 | 说明 |
|------|--------|------|
| `card.py` | 4 | 卡片展示、查词 API |
| `export.py` | 2 | Anki 导出 API |
| `process.py` | 2 | 处理状态 API |

### 服务层 (`backend/services/`)

| 文件 | 函数数 | 说明 |
|------|--------|------|
| `dictionary.py` | 6 | 词典查询服务 |
| `subtitle.py` | 7 | 字幕解析服务 |
| `downloader.py` | 2 | YouTube 下载服务 |
| `anki_export.py` | 2 | Anki .apkg 生成 |
| `pipeline.py` | 2 | 处理管道 |
| `storage.py` | 3 | 文件存储服务 |
| `splitter.py` | - | 音频分割 |

### 核心文件

| 文件 | 说明 |
|------|------|
| `backend/main.py` | FastAPI 应用入口、生命周期管理 |
| `backend/db.py` | SQLite 数据库初始化 |

---

## 🎯 核心功能模块

### 1. 词典服务 (dictionary.py)
- `lookup_word_youdao()` - 有道词典 API 查词
- `lookup_word_free()` - 免费词典 API 查词
- `extract_difficult_words()` - 从句子提取难词
- `annotate_sentence()` - 句子标注（生词高亮）

### 2. 字幕解析 (subtitle.py)
- `parse_srt()` - 解析 SRT 字幕格式
- `parse_vtt()` - 解析 VTT 字幕格式
- `_merge_short_segments()` - 合并短字幕片段
- `_clean_text()` - 清理字幕文本

### 3. Anki 导出 (anki_export.py)
- `generate_apkg()` - 生成 Anki .apkg 卡片包
- `_get_model()` - 获取 Anki 卡片模型

### 4. 下载服务 (downloader.py)
- `download_audio_and_subtitle()` - 下载 YouTube 音频和字幕
- `normalize_youtube_url()` - 标准化 YouTube URL

---

## 📊 统计数据

- **总函数数**: 30+
- **API 端点**: 8+
- **服务模块**: 7
- **调用关系**: 23 条

---

*Generated by GitNexus MCP*