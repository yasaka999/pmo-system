"""
PMO 系统初始化脚本 —— 仅创建必要的基础数据
=============================================
执行方法：
  cd backend
  source venv/bin/activate       # Windows: venv\\Scripts\\activate
  python init_data.py

效果：
  1. 建表（如果表不存在）
  2. 创建 admin 初始用户（默认密码 admin123，已存在则跳过）
  3. 写入所有系统配置字典（项目状态/阶段/里程碑状态/问题/风险等枚举值）
     已存在的字典项会跳过，不会重复插入

说明：
  - 本脚本不会清空任何已有数据，可安全重复执行
  - 如需写入测试数据（测试项目/问题/风险等），请执行 seed_data.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.base import Base
from app.db import session as db_session

# 导入所有模型（触发 CREATE TABLE IF NOT EXISTS）
from app.models.project import Project       # noqa
from app.models.milestone import Milestone, Task  # noqa
from app.models.issue import Issue           # noqa
from app.models.risk import Risk             # noqa
from app.models.manday import ManDay         # noqa
from app.models.user import User
from app.models.sys_dict import SysDict
from app.core.security import get_password_hash

db = SessionLocal()

# ──────────────────────────────────────────────
# 1. 系统字典（所有选择类字段的枚举值）
# ──────────────────────────────────────────────
DICT_DATA = [
    # ── 项目状态 ──────────────────────────────
    {"category": "project_status", "code": "st_normal",  "label": "正常",   "color": "success", "sort_order": 1},
    {"category": "project_status", "code": "st_warn",    "label": "预警",   "color": "warning", "sort_order": 2},
    {"category": "project_status", "code": "st_delay",   "label": "延期",   "color": "danger",  "sort_order": 3},
    {"category": "project_status", "code": "st_pause",   "label": "暂停",   "color": "info",    "sort_order": 4},
    {"category": "project_status", "code": "st_done",    "label": "已完成", "color": "",        "sort_order": 5},

    # ── 项目阶段 ──────────────────────────────
    {"category": "project_phase", "code": "ph_pre",     "label": "售前", "color": "info",    "sort_order": 1},
    {"category": "project_phase", "code": "ph_kickoff", "label": "启动", "color": "primary", "sort_order": 2},
    {"category": "project_phase", "code": "ph_impl",    "label": "实施", "color": "primary", "sort_order": 3},
    {"category": "project_phase", "code": "ph_accept",  "label": "验收", "color": "warning", "sort_order": 4},
    {"category": "project_phase", "code": "ph_close",   "label": "收尾", "color": "success", "sort_order": 5},

    # ── 里程碑状态 ────────────────────────────
    {"category": "milestone_status", "code": "ms_notstart", "label": "未开始", "color": "info",    "sort_order": 1},
    {"category": "milestone_status", "code": "ms_inprog",   "label": "进行中", "color": "primary", "sort_order": 2},
    {"category": "milestone_status", "code": "ms_done",     "label": "已完成", "color": "success", "sort_order": 3},
    {"category": "milestone_status", "code": "ms_delay",    "label": "延期",   "color": "danger",  "sort_order": 4},

    # ── 任务状态 ──────────────────────────────
    {"category": "task_status", "code": "ts_planned",   "label": "计划",     "color": "info",    "sort_order": 1},
    {"category": "task_status", "code": "ts_inprog",    "label": "进行中",   "color": "primary", "sort_order": 2},
    {"category": "task_status", "code": "ts_completed", "label": "已完成",   "color": "success", "sort_order": 3},
    {"category": "task_status", "code": "ts_delayed",   "label": "延期",     "color": "danger",  "sort_order": 4},

    # ── 问题严重等级 ──────────────────────────
    {"category": "issue_severity", "code": "isev_h", "label": "高", "color": "danger",  "sort_order": 1},
    {"category": "issue_severity", "code": "isev_m", "label": "中", "color": "warning", "sort_order": 2},
    {"category": "issue_severity", "code": "isev_l", "label": "低", "color": "success", "sort_order": 3},

    # ── 问题状态 ──────────────────────────────
    {"category": "issue_status", "code": "ist_open",   "label": "待处理", "color": "danger",  "sort_order": 1},
    {"category": "issue_status", "code": "ist_doing",  "label": "处理中", "color": "warning", "sort_order": 2},
    {"category": "issue_status", "code": "ist_closed", "label": "已关闭", "color": "success", "sort_order": 3},

    # ── 问题来源 ──────────────────────────────
    {"category": "issue_source", "code": "src_client", "label": "客户",   "color": "", "sort_order": 1},
    {"category": "issue_source", "code": "src_inter",  "label": "内部",   "color": "", "sort_order": 2},
    {"category": "issue_source", "code": "src_3rd",    "label": "第三方", "color": "", "sort_order": 3},

    # ── 风险概率 ──────────────────────────────
    {"category": "risk_prob", "code": "rp_h", "label": "高", "color": "danger",  "sort_order": 1},
    {"category": "risk_prob", "code": "rp_m", "label": "中", "color": "warning", "sort_order": 2},
    {"category": "risk_prob", "code": "rp_l", "label": "低", "color": "success", "sort_order": 3},

    # ── 风险影响 ──────────────────────────────
    {"category": "risk_impact", "code": "ri_h", "label": "高", "color": "danger",  "sort_order": 1},
    {"category": "risk_impact", "code": "ri_m", "label": "中", "color": "warning", "sort_order": 2},
    {"category": "risk_impact", "code": "ri_l", "label": "低", "color": "success", "sort_order": 3},

    # ── 风险状态 ──────────────────────────────
    {"category": "risk_status", "code": "rs_open",   "label": "开放",   "color": "danger",  "sort_order": 1},
    {"category": "risk_status", "code": "rs_mitig",  "label": "已缓解", "color": "warning", "sort_order": 2},
    {"category": "risk_status", "code": "rs_closed", "label": "已关闭", "color": "success", "sort_order": 3},

    # ── 风险等级（根据概率和影响自动计算）───────
    {"category": "risk_level", "code": "rl_h", "label": "高", "color": "danger",  "sort_order": 1},
    {"category": "risk_level", "code": "rl_m", "label": "中", "color": "warning", "sort_order": 2},
    {"category": "risk_level", "code": "rl_l", "label": "低", "color": "success", "sort_order": 3},

    # ── 看板卡片配置 ─────────────────────────
    # is_active 控制显示/隐藏，sort_order 控制排列顺序
    # label/color 字段不使用，仅 code 和 sort_order、is_active 有意义
    {"category": "dashboard_widget", "code": "total",              "label": "项目总数",   "color": "", "sort_order": 1},
    {"category": "dashboard_widget", "code": "in_progress",        "label": "进行中",     "color": "", "sort_order": 2},
    {"category": "dashboard_widget", "code": "done",               "label": "已完成",     "color": "", "sort_order": 3},
    {"category": "dashboard_widget", "code": "open_issues",        "label": "未关闭问题", "color": "", "sort_order": 4},
    {"category": "dashboard_widget", "code": "open_risks",         "label": "开放风险",   "color": "", "sort_order": 5},
    {"category": "dashboard_widget", "code": "pending_delivery",   "label": "待交付",     "color": "", "sort_order": 6},
    {"category": "dashboard_widget", "code": "delivered",          "label": "已交付",     "color": "", "sort_order": 7},
    {"category": "dashboard_widget", "code": "pending_acceptance", "label": "待验收",     "color": "", "sort_order": 8},
    {"category": "dashboard_widget", "code": "accepted",           "label": "已验收",     "color": "", "sort_order": 9},
    # 按项目状态细分的卡片
    {"category": "dashboard_widget", "code": "status_normal",  "label": "正常",   "color": "", "sort_order": 10},
    {"category": "dashboard_widget", "code": "status_warning", "label": "预警",   "color": "", "sort_order": 11},
    {"category": "dashboard_widget", "code": "status_delayed", "label": "延期",   "color": "", "sort_order": 12},
    {"category": "dashboard_widget", "code": "status_paused",  "label": "暂停",   "color": "", "sort_order": 13},
    {"category": "dashboard_widget", "code": "status_done",    "label": "已完成", "color": "", "sort_order": 14},
]

def init_dicts():
    inserted = 0
    skipped = 0
    for d in DICT_DATA:
        existing = db.query(SysDict).filter(
            SysDict.category == d["category"],
            SysDict.code == d["code"]
        ).first()
        if existing:
            skipped += 1
        else:
            db.add(SysDict(**d, is_active=True))
            inserted += 1
    db.commit()
    print(f"✅ 系统字典：新增 {inserted} 条，跳过（已存在）{skipped} 条，共 {len(DICT_DATA)} 条配置项")


def init_admin():
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("✅ admin 用户：已存在，跳过")
    else:
        db.add(User(
            username="admin",
            full_name="系统管理员",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True,
        ))
        db.commit()
        print("✅ admin 用户：已创建（用户名: admin，密码: admin123）")


if __name__ == "__main__":
    print("=" * 55)
    print("  PMO 系统初始化（基础数据）")
    print("=" * 55)

    # 创建所有表
    print("📦 创建数据库表...")
    Base.metadata.create_all(bind=db.get_bind())
    
    init_admin()
    init_dicts()

    print()
    print("🎉 初始化完成！")
    print()
    print("  登录账号：admin / admin123")
    print()
    print("  提示：如需插入测试数据（示例项目/问题/风险），")
    print("        请执行 python seed_data.py")
    print("=" * 55)

    db.close()
