"""SQLite 数据库连接与初始化"""
import aiosqlite
import os

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "ankitube.db"))

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS deck (
    id          TEXT PRIMARY KEY,
    youtube_url TEXT NOT NULL,
    title       TEXT,
    thumbnail   TEXT,
    lang_cd     TEXT DEFAULT 'en',
    status      TEXT DEFAULT 'pending',
    progress    INTEGER DEFAULT 0,
    total       INTEGER DEFAULT 0,
    error_msg   TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS segment (
    id          TEXT PRIMARY KEY,
    deck_id     TEXT NOT NULL REFERENCES deck(id),
    seg_index   INTEGER NOT NULL,
    audio_path  TEXT NOT NULL,
    sentence    TEXT,
    words       TEXT,
    start_ms    INTEGER,
    end_ms      INTEGER,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task (
    id          TEXT PRIMARY KEY,
    deck_id     TEXT NOT NULL REFERENCES deck(id),
    status      TEXT DEFAULT 'pending',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

MIGRATE_SQL = """
ALTER TABLE deck ADD COLUMN thumbnail TEXT;
ALTER TABLE segment ADD COLUMN words TEXT;
"""


async def get_db():
    """获取数据库连接（依赖注入用）"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db():
    """初始化数据库表（应用启动时调用）"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_SQL)
        await db.commit()
        
        # 尝试添加 thumbnail 列（如果不存在）
        try:
            await db.execute("ALTER TABLE deck ADD COLUMN thumbnail TEXT")
            await db.commit()
        except:
            pass  # 列已存在
        
        # 尝试添加 words 列（如果不存在）
        try:
            await db.execute("ALTER TABLE segment ADD COLUMN words TEXT")
            await db.commit()
        except:
            pass  # 列已存在
