# AnkiAudio Platform

个人云端音频 Anki 服务，自动从 YouTube 视频提取音频和字幕，生成可导入 Anki 的听力卡片牌组。

## 快速开始

### 1. 安装依赖

```bash
# 系统依赖（macOS）
brew install ffmpeg yt-dlp

# Python 依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，修改 BASE_URL 为你的服务器地址
```

### 3. 启动服务

```bash
# 从项目根目录运行
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问管理页面

打开浏览器访问 `http://localhost:8000`，粘贴 YouTube 链接开始制作牌组。

## 项目结构

```
anki-audio-platform/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── db.py                # SQLite 数据库
│   ├── api/
│   │   ├── process.py       # POST /process, GET /status/{id}, GET /decks
│   │   ├── card.py          # GET /card/{id}?side=0/1  (Anki iframe 加载)
│   │   └── export.py        # GET /export/{deck_id}/anki, GET /deck/prefer/
│   ├── services/
│   │   ├── downloader.py    # yt-dlp 下载音频+字幕
│   │   ├── subtitle.py      # VTT/SRT 字幕解析
│   │   ├── splitter.py      # pydub 音频切分
│   │   ├── storage.py       # 本地文件存储
│   │   ├── anki_export.py   # genanki 生成 .apkg
│   │   └── pipeline.py      # 整体流水线协调
│   └── static/
│       └── index.html       # 管理 Web 页面
├── storage/                 # 音频文件存储目录
├── data/                    # SQLite 数据库文件
├── requirements.txt
└── .env.example
```

## Anki 卡片工作原理

1. 生成的 `.apkg` 中每张卡片只有一个字段 `page`，值为 `{BASE_URL}/card/{id}?type=ting&seg_index={n}`
2. 卡片正面：iframe 加载 `{page}&side=0` → 服务端渲染音频播放器（听音辨意）
3. 卡片背面：iframe 加载 `{page}&side=1` → 服务端渲染播放器 + 字幕答案

## 云服务器部署

```bash
# 修改 .env 中的 BASE_URL 为公网 IP 或域名
BASE_URL=https://your-domain.com

# 使用 nginx 反向代理 8000 端口（建议配置 HTTPS）
```
