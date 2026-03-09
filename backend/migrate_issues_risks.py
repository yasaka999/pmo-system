#!/usr/bin/env python3
"""
迁移问题和风险数据到字典代码
"""
import sqlite3
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / "pmo.db"

# 迁移映射
ISSUE_STATUS_MAP = {
    '待处理': 'ist_open',
    '处理中': 'ist_doing',
    '已关闭': 'ist_closed'
}

ISSUE_SEVERITY_MAP = {
    '高': 'isev_h',
    '中': 'isev_m',
    '低': 'isev_l'
}

RISK_STATUS_MAP = {
    '开放': 'rs_open',
    '进行中': 'rs_doing',
    '已缓解': 'rs_mitig',
    '已关闭': 'rs_closed'
}

RISK_LEVEL_MAP = {
    '极高': 'rl_h',
    '高': 'rl_h',
    '中': 'rl_m',
    '低': 'rl_l'
}

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 备份
    backup_path = DB_PATH.parent / f"pmo.db.backup_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M')}"
    with open(backup_path, 'wb') as f:
        for line in conn.iterdump():
            f.write(f"{line}\n".encode())
    print(f"✅ 备份已保存: {backup_path}")
    
    # 迁移 issues 表
    print("\n📋 迁移 issues 表...")
    for old_val, new_val in ISSUE_STATUS_MAP.items():
        cursor.execute("UPDATE issues SET status = ? WHERE status = ?", (new_val, old_val))
        if cursor.rowcount > 0:
            print(f"  status: '{old_val}' → '{new_val}' ({cursor.rowcount} 条)")
    
    for old_val, new_val in ISSUE_SEVERITY_MAP.items():
        cursor.execute("UPDATE issues SET severity = ? WHERE severity = ?", (new_val, old_val))
        if cursor.rowcount > 0:
            print(f"  severity: '{old_val}' → '{new_val}' ({cursor.rowcount} 条)")
    
    # 迁移 risks 表
    print("\n⚠️ 迁移 risks 表...")
    for old_val, new_val in RISK_STATUS_MAP.items():
        cursor.execute("UPDATE risks SET status = ? WHERE status = ?", (new_val, old_val))
        if cursor.rowcount > 0:
            print(f"  status: '{old_val}' → '{new_val}' ({cursor.rowcount} 条)")
    
    for old_val, new_val in RISK_LEVEL_MAP.items():
        cursor.execute("UPDATE risks SET level = ? WHERE level = ?", (new_val, old_val))
        if cursor.rowcount > 0:
            print(f"  level: '{old_val}' → '{new_val}' ({cursor.rowcount} 条)")
    
    conn.commit()
    
    # 验证
    print("\n✅ 迁移完成，验证结果:")
    cursor.execute("SELECT DISTINCT status, severity FROM issues")
    for row in cursor.fetchall():
        print(f"  issues: status={row[0]}, severity={row[1]}")
    
    cursor.execute("SELECT DISTINCT status, level FROM risks")
    for row in cursor.fetchall():
        print(f"  risks: status={row[0]}, level={row[1]}")
    
    conn.close()

if __name__ == "__main__":
    migrate()