# AnkiAudio Platform 🎧

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

个人云端音频 Anki 服务，自动从 YouTube 视频提取音频和字幕，生成可导入 Anki 的听力卡片牌组。

## ✨ 功能特性

- 🎬 **YouTube 视频处理** - 自动下载音频和字幕
- 🎵 **智能音频切分** - 按句子自动分割音频片段
- 📚 **Anki 牌组生成** - 一键导出 `.apkg` 文件
- 🔄 **循环播放** - 卡片正面自动循环播放音频
- ⚡ **变速播放** - 支持 0.5x ~ 2x 播放速度
- 📖 **生词标注** - 点击单词查看中英双语释义
- 🎨 **精美界面** - 圆形旋转缩略图，沉浸式学习体验

## 📸 截图

| 管理页面 | 卡片正面 | 卡片背面 |
|---------|---------|---------|
| ![管理页面](docs/screenshot-home.png) | ![卡片正面](docs/screenshot-front.png) | ![卡片背面](docs/screenshot-back.png) |

## 🚀 快速开始

### 系统要求

- Python 3.10+
- FFmpeg
- yt-dlp

### 安装

```bash
# 克隆仓库
git clone https://github.com/yasaka999/python/tree/master/anki-audio-platform.git
cd anki-audio-platform

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt

# 安装系统依赖
# macOS:
brew install ffmpeg yt-dlp
# Ubuntu/Debian:
sudo apt install ffmpeg yt-dlp
```

### 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
BASE_URL=http://your-server:8000  # 服务器公网地址
STORAGE_DIR=./storage             # 音频存储目录
DB_PATH=./data/ankitube.db        # 数据库路径
FFMPEG_PATH=/usr/bin/ffmpeg      # FFmpeg 路径（可选）
```

### 启动

```bash
# 开发模式
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000` 开始使用。

## 📖 使用指南

### 1. 创建牌组

1. 打开管理页面，粘贴 YouTube 视频链接
2. 选择字幕语言（如 en, zh-CN, ja）
3. 点击"开始处理"，等待处理完成
4. 点击"下载 Anki 牌组"获取 `.apkg` 文件

### 2. 导入 Anki

1. 打开 Anki → 文件 → 导入
2. 选择下载的 `.apkg` 文件
3. 开始学习！

### 3. 卡片学习

- **正面**：自动循环播放音频，尝试理解内容
- **背面**：显示字幕文本，点击生词查看释义
- **播放控制**：调整播放速度，反复练习

## 🏗️ 项目结构

```
anki-audio-platform/
├── backend/
│   ├── main.py              # FastAPI 应用入口
│   ├── db.py                # SQLite 数据库操作
│   ├── api/
│   │   ├── process.py       # 视频处理 API
│   │   ├── card.py          # 卡片渲染 API
│   │   └── export.py        # Anki 导出 API
│   ├── services/
│   │   ├── downloader.py    # yt-dlp 下载器
│   │   ├── subtitle.py      # VTT/SRT 字幕解析
│   │   ├── splitter.py      # pydub 音频切分
│   │   ├── storage.py       # 文件存储服务
│   │   ├── anki_export.py   # genanki 牌组生成
│   │   ├── dictionary.py    # 词典查询服务
│   │   └── pipeline.py      # 处理流水线
│   └── static/
│       └── index.html       # Web 管理界面
├── storage/                 # 音频文件存储
├── data/                    # SQLite 数据库
├── requirements.txt
└── .env.example
```

## 🔌 API 文档

### 处理视频

```http
POST /process
Content-Type: application/json

{
  "url": "https://youtube.com/watch?v=xxx",
  "lang": "en"
}
```

### 查询状态

```http
GET /status/{deck_id}
```

### 获取牌组列表

```http
GET /decks
```

### 导出 Anki 牌组

```http
GET /export/{deck_id}/anki
```

### 渲染卡片

```http
GET /card/{card_id}?side=0|1
```

### 查询单词释义

```http
GET /word/{word}
```

## 🌐 云服务器部署

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用 Systemd 服务

```ini
# /etc/systemd/system/ankiaudio.service
[Unit]
Description=AnkiAudio Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/anki-audio-platform
Environment="PATH=/opt/anki-audio-platform/venv/bin"
ExecStart=/opt/anki-audio-platform/venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ankiaudio
sudo systemctl start ankiaudio
```

## 🛠️ 技术栈

| 组件 | 技术 |
|-----|------|
| 后端框架 | FastAPI |
| 数据库 | SQLite (aiosqlite) |
| 视频下载 | yt-dlp |
| 音频处理 | pydub + FFmpeg |
| Anki 生成 | genanki |
| 字幕解析 | webvtt-py, srt |
| HTTP 客户端 | aiohttp |

## 📝 开发路线

详见 [ROADMAP.md](ROADMAP.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License