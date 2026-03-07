"""
PMO 系统数据规范化迁移脚本
将历史数据中的中文值转换为字典代码

执行方法：
  cd backend && python migrate_to_dict_codes.py

迁移内容：
  - Project.phase: 启动→ph_kickoff, 实施→ph_impl, 验收→ph_accept, 收尾→ph_close, 售前→ph_pre
  - Project.status: 正常→st_normal, 预警→st_warn, 延期→st_delay, 暂停→st_pause, 已完成→st_done
  - Milestone.status: 未开始→ms_notstart, 进行中→ms_inprog, 已完成→ms_done, 延期→ms_delay
  - Task.status: 未开始→ms_notstart, 进行中→ms_inprog, 已完成→ms_done, 延期→ms_delay
  - Issue.severity: 高→isev_h, 中→isev_m, 低→isev_l
  - Issue.source: 客户→src_client, 内部→src_inter, 第三方→src_3rd
  - Issue.status: 待处理→ist_open, 处理中→ist_doing, 已关闭→ist_closed
  - Risk.probability: 高→rp_h, 中→rp_m, 低→rp_l
  - Risk.impact: 高→ri_h, 中→ri_m, 低→ri_l
  - Risk.status: 开放→rs_open, 已缓解→rs_mitig, 已关闭→rs_closed
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.project import Project
from app.models.milestone import Milestone, Task
from app.models.issue import Issue
from app.models.risk import Risk

db = SessionLocal()

# 映射字典
PROJECT_PHASE_MAP = {
    "售前": "ph_pre",
    "启动": "ph_kickoff",
    "实施": "ph_impl",
    "验收": "ph_accept",
    "收尾": "ph_close",
}

PROJECT_STATUS_MAP = {
    "正常": "st_normal",
    "预警": "st_warn",
    "延期": "st_delay",
    "暂停": "st_pause",
    "已完成": "st_done",
}

MILESTONE_STATUS_MAP = {
    "未开始": "ms_notstart",
    "进行中": "ms_inprog",
    "已完成": "ms_done",
    "延期": "ms_delay",
}

ISSUE_SEVERITY_MAP = {
    "高": "isev_h",
    "中": "isev_m",
    "低": "isev_l",
}

ISSUE_SOURCE_MAP = {
    "客户": "src_client",
    "内部": "src_inter",
    "第三方": "src_3rd",
}

ISSUE_STATUS_MAP = {
    "待处理": "ist_open",
    "处理中": "ist_doing",
    "已关闭": "ist_closed",
}

RISK_PROB_MAP = {
    "高": "rp_h",
    "中": "rp_m",
    "低": "rp_l",
}

RISK_IMPACT_MAP = {
    "高": "ri_h",
    "中": "ri_m",
    "低": "ri_l",
}

RISK_STATUS_MAP = {
    "开放": "rs_open",
    "已缓解": "rs_mitig",
    "已关闭": "rs_closed",
}


def migrate_projects():
    """迁移项目表"""
    print("\n=== 迁移 Projects ===")
    projects = db.query(Project).all()
    updated = 0
    
    for p in projects:
        changed = False
        # 迁移 phase
        if p.phase in PROJECT_PHASE_MAP:
            old_val = p.phase
            p.phase = PROJECT_PHASE_MAP[p.phase]
            print(f"  Project {p.code}: phase {old_val} → {p.phase}")
            changed = True
        # 迁移 status
        if p.status in PROJECT_STATUS_MAP:
            old_val = p.status
            p.status = PROJECT_STATUS_MAP[p.status]
            print(f"  Project {p.code}: status {old_val} → {p.status}")
            changed = True
        
        if changed:
            updated += 1
    
    db.commit()
    print(f"✅ 项目表：已迁移 {updated}/{len(projects)} 条")
    return updated


def migrate_milestones():
    """迁移里程碑表"""
    print("\n=== 迁移 Milestones ===")
    milestones = db.query(Milestone).all()
    updated = 0
    
    for m in milestones:
        if m.status in MILESTONE_STATUS_MAP:
            old_val = m.status
            m.status = MILESTONE_STATUS_MAP[m.status]
            print(f"  Milestone {m.id} ({m.name[:20]}): status {old_val} → {m.status}")
            updated += 1
    
    db.commit()
    print(f"✅ 里程碑表：已迁移 {updated}/{len(milestones)} 条")
    return updated


def migrate_tasks():
    """迁移工作任务表"""
    print("\n=== 迁移 Tasks ===")
    tasks = db.query(Task).all()
    updated = 0
    
    for t in tasks:
        if t.status in MILESTONE_STATUS_MAP:
            old_val = t.status
            t.status = MILESTONE_STATUS_MAP[t.status]
            print(f"  Task {t.id} ({t.name[:20]}): status {old_val} → {t.status}")
            updated += 1
    
    db.commit()
    print(f"✅ 工作任务表：已迁移 {updated}/{len(tasks)} 条")
    return updated


def migrate_issues():
    """迁移问题台账表"""
    print("\n=== 迁移 Issues ===")
    issues = db.query(Issue).all()
    updated = 0
    
    for i in issues:
        changed = False
        # 迁移 severity
        if i.severity in ISSUE_SEVERITY_MAP:
            old_val = i.severity
            i.severity = ISSUE_SEVERITY_MAP[i.severity]
            print(f"  Issue {i.id}: severity {old_val} → {i.severity}")
            changed = True
        # 迁移 source
        if i.source in ISSUE_SOURCE_MAP:
            old_val = i.source
            i.source = ISSUE_SOURCE_MAP[i.source]
            print(f"  Issue {i.id}: source {old_val} → {i.source}")
            changed = True
        # 迁移 status
        if i.status in ISSUE_STATUS_MAP:
            old_val = i.status
            i.status = ISSUE_STATUS_MAP[i.status]
            print(f"  Issue {i.id}: status {old_val} → {i.status}")
            changed = True
        
        if changed:
            updated += 1
    
    db.commit()
    print(f"✅ 问题台账表：已迁移 {updated}/{len(issues)} 条")
    return updated


def migrate_risks():
    """迁移风险台账表"""
    print("\n=== 迁移 Risks ===")
    risks = db.query(Risk).all()
    updated = 0
    
    for r in risks:
        changed = False
        # 迁移 probability
        if r.probability in RISK_PROB_MAP:
            old_val = r.probability
            r.probability = RISK_PROB_MAP[r.probability]
            print(f"  Risk {r.id}: probability {old_val} → {r.probability}")
            changed = True
        # 迁移 impact
        if r.impact in RISK_IMPACT_MAP:
            old_val = r.impact
            r.impact = RISK_IMPACT_MAP[r.impact]
            print(f"  Risk {r.id}: impact {old_val} → {r.impact}")
            changed = True
        # 迁移 status
        if r.status in RISK_STATUS_MAP:
            old_val = r.status
            r.status = RISK_STATUS_MAP[r.status]
            print(f"  Risk {r.id}: status {old_val} → {r.status}")
            changed = True
        
        if changed:
            updated += 1
    
    db.commit()
    print(f"✅ 风险台账表：已迁移 {updated}/{len(risks)} 条")
    return updated


if __name__ == "__main__":
    print("=" * 60)
    print("🔄 PMO 系统数据规范化迁移")
    print("   将中文值转换为字典代码")
    print("=" * 60)
    
    total_updated = 0
    total_updated += migrate_projects()
    total_updated += migrate_milestones()
    total_updated += migrate_tasks()
    total_updated += migrate_issues()
    total_updated += migrate_risks()
    
    print("\n" + "=" * 60)
    print(f"🎉 迁移完成！共更新 {total_updated} 条记录")
    print("=" * 60)
    
    db.close()
