"""
PMO 系统测试数据初始化脚本
执行方法：
  cd backend && source venv/bin/activate && python seed_data.py

包含：
  - 系统字典（项目状态/阶段/问题/风险等全分类）
  - 用户（admin + 3 个不同角色用户）
  - 3 个项目（正常/预警/延期各一个）
  - 每个项目的里程碑（3～4 个）+ 工作任务（2～4 个）
  - 每个项目的问题台账（2～4 条）
  - 每个项目的风险台账（2～3 条）
  - 每个项目的人天记录（多条，涵盖计费/非计费）
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from app.db.session import SessionLocal
from app.db.base import Base
from app.db import session as db_session
from sqlalchemy import create_engine, inspect

# 导入所有模型（触发建表）
from app.models.project import Project
from app.models.milestone import Milestone, Task
from app.models.issue import Issue
from app.models.risk import Risk
from app.models.manday import ManDay
from app.models.user import User
from app.models.sys_dict import SysDict
from app.core.security import get_password_hash

db = SessionLocal()

def clear_all():
    """清空已有数据（保留结构）"""
    for model in [Task, ManDay, Issue, Risk, Milestone, Project, SysDict]:
        db.query(model).delete()
    # 只清空非 admin 用户
    db.query(User).filter(User.username != 'admin').delete()
    db.commit()
    print("✅ 已清空旧数据（admin 用户保留）")

def seed_dicts():
    """系统字典配置：覆盖所有选择类字段"""
    dicts = [
        # 项目状态
        dict(category="project_status", code="st_normal",   label="正常",  color="success", sort_order=1),
        dict(category="project_status", code="st_warn",     label="预警",  color="warning", sort_order=2),
        dict(category="project_status", code="st_delay",    label="延期",  color="danger",  sort_order=3),
        dict(category="project_status", code="st_pause",    label="暂停",  color="info",    sort_order=4),
        dict(category="project_status", code="st_done",     label="已完成",color="",        sort_order=5),
        # 项目阶段
        dict(category="project_phase",  code="ph_pre",      label="售前",  color="info",    sort_order=1),
        dict(category="project_phase",  code="ph_kickoff",  label="启动",  color="primary", sort_order=2),
        dict(category="project_phase",  code="ph_impl",     label="实施",  color="primary", sort_order=3),
        dict(category="project_phase",  code="ph_accept",   label="验收",  color="warning", sort_order=4),
        dict(category="project_phase",  code="ph_close",    label="收尾",  color="success", sort_order=5),
        # 里程碑状态
        dict(category="milestone_status", code="ms_notstart", label="未开始", color="info",    sort_order=1),
        dict(category="milestone_status", code="ms_inprog",   label="进行中", color="primary", sort_order=2),
        dict(category="milestone_status", code="ms_done",     label="已完成", color="success", sort_order=3),
        dict(category="milestone_status", code="ms_delay",    label="延期",   color="danger",  sort_order=4),
        # 问题严重等级
        dict(category="issue_severity", code="isev_h", label="高", color="danger",  sort_order=1),
        dict(category="issue_severity", code="isev_m", label="中", color="warning", sort_order=2),
        dict(category="issue_severity", code="isev_l", label="低", color="success", sort_order=3),
        # 问题状态
        dict(category="issue_status", code="ist_open",   label="待处理", color="danger",  sort_order=1),
        dict(category="issue_status", code="ist_doing",  label="处理中", color="warning", sort_order=2),
        dict(category="issue_status", code="ist_closed", label="已关闭", color="success", sort_order=3),
        # 问题来源
        dict(category="issue_source", code="src_client", label="客户",  color="", sort_order=1),
        dict(category="issue_source", code="src_inter",  label="内部",  color="", sort_order=2),
        dict(category="issue_source", code="src_3rd",    label="第三方",color="", sort_order=3),
        # 风险概率
        dict(category="risk_prob", code="rp_h", label="高", color="danger",  sort_order=1),
        dict(category="risk_prob", code="rp_m", label="中", color="warning", sort_order=2),
        dict(category="risk_prob", code="rp_l", label="低", color="success", sort_order=3),
        # 风险影响
        dict(category="risk_impact", code="ri_h", label="高", color="danger",  sort_order=1),
        dict(category="risk_impact", code="ri_m", label="中", color="warning", sort_order=2),
        dict(category="risk_impact", code="ri_l", label="低", color="success", sort_order=3),
        # 风险状态
        dict(category="risk_status", code="rs_open",    label="开放",   color="danger",  sort_order=1),
        dict(category="risk_status", code="rs_mitig",   label="已缓解", color="warning", sort_order=2),
        dict(category="risk_status", code="rs_closed",  label="已关闭", color="success", sort_order=3),
        # 风险等级（根据概率和影响自动计算）
        dict(category="risk_level", code="rl_h", label="高", color="danger",  sort_order=1),
        dict(category="risk_level", code="rl_m", label="中", color="warning", sort_order=2),
        dict(category="risk_level", code="rl_l", label="低", color="success", sort_order=3),
    ]
    for d in dicts:
        db.add(SysDict(**d, is_active=True))
    db.commit()
    print(f"✅ 字典配置：已插入 {len(dicts)} 条")

def seed_users():
    """新增 3 个测试用户（保留已有 admin）"""
    users = [
        dict(username="pmo_zhang", full_name="张敏（PMO）",  role="pmo",    password="pmo123"),
        dict(username="pm_li",     full_name="李强（PM）",    role="member", password="pm123"),
        dict(username="viewer1",   full_name="陈阅（只读）",  role="viewer", password="view123"),
    ]
    for u in users:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if not existing:
            db.add(User(
                username=u["username"],
                full_name=u["full_name"],
                hashed_password=get_password_hash(u["password"]),
                role=u["role"],
                is_active=True,
            ))
    db.commit()
    print(f"✅ 用户：已插入 {len(users)} 个测试用户")

def seed_projects_and_children():
    today = date.today()

    # ─────────────── 项目 1：某银行信贷系统上线（正常） ───────────────
    p1 = Project(
        code="PMO-2024-001",
        name="某银行信贷系统实施项目",
        client="某商业银行",
        manager="李强",
        phase="ph_impl",      # 实施
        status="st_normal",   # 正常
        description="为某商业银行实施新一代信贷系统，包含授信、放贷、还款模块。",
        plan_start=today - timedelta(days=120),
        plan_end=today + timedelta(days=60),
        budget_mandays=180,
    )
    db.add(p1)
    db.flush()

    ms1_1 = Milestone(project_id=p1.id, name="需求调研完成", plan_date=today - timedelta(days=90),
                      actual_date=today - timedelta(days=88), status="ms_done", order_index=1)
    ms1_2 = Milestone(project_id=p1.id, name="系统开发完成", plan_date=today - timedelta(days=30),
                      actual_date=today - timedelta(days=28), status="ms_done", order_index=2)
    ms1_3 = Milestone(project_id=p1.id, name="UAT 测试完成", plan_date=today + timedelta(days=15),
                      status="ms_inprog", order_index=3)
    ms1_4 = Milestone(project_id=p1.id, name="生产上线", plan_date=today + timedelta(days=45),
                      status="ms_notstart", order_index=4)
    db.add_all([ms1_1, ms1_2, ms1_3, ms1_4])
    db.flush()

    db.add_all([
        Task(project_id=p1.id, milestone_id=ms1_3.id, name="授信模块测试用例编写",
             assignee="张敏", plan_start=today - timedelta(days=10), plan_end=today,
             status="ms_inprog", progress=70),
        Task(project_id=p1.id, milestone_id=ms1_3.id, name="放贷模块 UAT 执行",
             assignee="李强", plan_start=today, plan_end=today + timedelta(days=10),
             status="ms_notstart", progress=0),
        Task(project_id=p1.id, milestone_id=ms1_4.id, name="生产环境部署方案编写",
             assignee="王技术", plan_start=today + timedelta(days=10), plan_end=today + timedelta(days=20),
             status="ms_notstart", progress=0),
        Task(project_id=p1.id, milestone_id=ms1_4.id, name="数据迁移脚本验证",
             assignee="张敏", plan_start=today + timedelta(days=20), plan_end=today + timedelta(days=35),
             status="ms_notstart", progress=0),
    ])

    db.add_all([
        Issue(project_id=p1.id, title="授信规则引擎计算结果与预期不符",
              description="规则引擎在部分边界场景下的利率计算结果不正确，影响验收测试通过",
              severity="isev_h", source="src_client", assignee="李强",
              raised_date=today - timedelta(days=5), due_date=today + timedelta(days=3),
              status="ist_doing", resolution="正在排查参数配置问题"),
        Issue(project_id=p1.id, title="UAT 测试环境数据库连接超时",
              description="高并发情况下测试环境 MySQL 连接池满，造成超时",
              severity="isev_m", source="src_inter", assignee="王技术",
              raised_date=today - timedelta(days=3), due_date=today + timedelta(days=7),
              status="ist_open"),
        Issue(project_id=p1.id, title="文档版本不一致",
              description="接口文档与实际开发版本存在差异",
              severity="isev_l", source="src_inter", assignee="张敏",
              raised_date=today - timedelta(days=15),
              resolved_date=today - timedelta(days=10),
              status="ist_closed", resolution="已统一更新文档至 v2.3"),
    ])

    db.add_all([
        Risk(project_id=p1.id, title="客户 IT 部门配合度不足",
             description="客户 IT 人员参与度低，测试数据准备缓慢",
             probability="rp_m", impact="ri_h", level="rl_h",
             assignee="李强", mitigation="升级至客户分管副行长，制定配合计划", status="rs_open"),
        Risk(project_id=p1.id, title="生产数据量超出预期",
             description="历史数据量超过估算 2 倍，迁移耗时存在风险",
             probability="rp_l", impact="ri_m", level="rl_m",
             assignee="王技术", mitigation="提前进行性能测试，准备增量迁移方案", status="rs_mitig"),
    ])

    db.add_all([
        ManDay(project_id=p1.id, staff_name="李强",  role="项目经理",   work_date=today - timedelta(days=i*7),
               days=5, is_billable=True, work_content="项目管理、客户汇报") for i in range(1, 5)
    ])
    db.add_all([
        ManDay(project_id=p1.id, staff_name="张敏",  role="实施顾问",   work_date=today - timedelta(days=i*7),
               days=4.5, is_billable=True, work_content="需求分析、测试设计") for i in range(1, 5)
    ])
    db.add_all([
        ManDay(project_id=p1.id, staff_name="王技术", role="技术工程师", work_date=today - timedelta(days=i*7),
               days=5, is_billable=False, work_content="环境搭建、脚本开发") for i in range(1, 3)
    ])

    # ─────────────── 项目 2：某政务平台改造（预警） ───────────────
    p2 = Project(
        code="PMO-2024-002",
        name="某市政务服务平台改造项目",
        client="某市行政审批局",
        manager="张敏",
        phase="ph_accept",   # 验收
        status="st_warn",    # 预警
        description="对现有政务服务平台进行功能升级和性能优化，支持更多事项在线办理。",
        plan_start=today - timedelta(days=180),
        plan_end=today + timedelta(days=15),
        budget_mandays=220,
    )
    db.add(p2)
    db.flush()

    ms2_1 = Milestone(project_id=p2.id, name="旧系统调研与分析", plan_date=today - timedelta(days=150),
                      actual_date=today - timedelta(days=145), status="ms_done", order_index=1)
    ms2_2 = Milestone(project_id=p2.id, name="平台功能开发完成", plan_date=today - timedelta(days=60),
                      actual_date=today - timedelta(days=55), status="ms_done", order_index=2)
    ms2_3 = Milestone(project_id=p2.id, name="性能压测验收", plan_date=today - timedelta(days=7),
                      status="ms_delay", order_index=3,
                      description="原计划上周完成，因压测场景设计问题延期")
    ms2_4 = Milestone(project_id=p2.id, name="系统正式投产", plan_date=today + timedelta(days=14),
                      status="ms_notstart", order_index=4)
    db.add_all([ms2_1, ms2_2, ms2_3, ms2_4])
    db.flush()

    db.add_all([
        Task(project_id=p2.id, milestone_id=ms2_3.id, name="高并发场景压测脚本编写",
             assignee="王技术", plan_start=today - timedelta(days=14), plan_end=today - timedelta(days=7),
             status="ms_inprog", progress=60),
        Task(project_id=p2.id, milestone_id=ms2_3.id, name="压测环境准备与调优",
             assignee="王技术", plan_start=today - timedelta(days=7), plan_end=today + timedelta(days=3),
             status="ms_inprog", progress=40),
        Task(project_id=p2.id, milestone_id=ms2_4.id, name="投产方案评审",
             assignee="张敏", plan_start=today + timedelta(days=5), plan_end=today + timedelta(days=8),
             status="ms_notstart", progress=0),
    ])

    db.add_all([
        Issue(project_id=p2.id, title="压测 QPS 未达标，仅为目标值 70%",
              description="在 2000 并发下系统响应时间超过 5 秒，QPS 仅 1400，要求 2000",
              severity="isev_h", source="src_inter", assignee="王技术",
              raised_date=today - timedelta(days=8), due_date=today + timedelta(days=5),
              status="ist_doing", resolution="已定位到数据库慢查询，正在优化索引"),
        Issue(project_id=p2.id, title="部分事项表单数据丢失",
              description="提交某类事项后偶现表单数据未完整保存",
              severity="isev_h", source="src_client", assignee="李强",
              raised_date=today - timedelta(days=5), due_date=today + timedelta(days=2),
              status="ist_open"),
        Issue(project_id=p2.id, title="页面存在部分按钮样式错位",
              description="IE11 兼容性问题，部分按钮显示异常",
              severity="isev_l", source="src_client", assignee="张敏",
              raised_date=today - timedelta(days=20),
              resolved_date=today - timedelta(days=18),
              status="ist_closed", resolution="已针对 IE11 增加样式兼容"),
    ])

    db.add_all([
        Risk(project_id=p2.id, title="性能问题导致验收推迟上线",
             description="当前性能压测未通过，若无法在计划日期前解决将推迟投产",
             probability="rp_h", impact="ri_h", level="rl_h",
             assignee="张敏", mitigation="每日召开技术攻关会议，同时启动分布式方案可行性研究", status="rs_open"),
        Risk(project_id=p2.id, title="客户验收人员调岗",
             description="对接负责人已通知调岗，新负责人尚未完成交接",
             probability="rp_m", impact="ri_m", level="rl_m",
             assignee="张敏", mitigation="加快完成交接文档，安排新对接人快速了解项目", status="rs_open"),
        Risk(project_id=p2.id, title="服务器采购延迟",
             description="生产服务器采购流程较长，存在到货晚于投产计划的风险",
             probability="rp_l", impact="ri_h", level="rl_h",
             assignee="王技术", mitigation="已申请绿色通道加急采购", status="rs_mitig"),
    ])

    for i in range(1, 6):
        db.add(ManDay(project_id=p2.id, staff_name="张敏",  role="项目经理",
                      work_date=today - timedelta(days=i*7), days=5, is_billable=True, work_content="项目协调、客户汇报"))
        db.add(ManDay(project_id=p2.id, staff_name="王技术", role="技术负责人",
                      work_date=today - timedelta(days=i*7), days=5, is_billable=True, work_content="性能调优、架构优化"))
        db.add(ManDay(project_id=p2.id, staff_name="刘测试", role="测试工程师",
                      work_date=today - timedelta(days=i*7), days=4, is_billable=True, work_content="压测脚本开发与执行"))

    # ─────────────── 项目 3：某集团 ERP 系统实施（延期） ───────────────
    p3 = Project(
        code="PMO-2025-001",
        name="某制造集团 ERP 系统实施",
        client="某制造集团有限公司",
        manager="刘总",
        phase="ph_impl",    # 实施
        status="st_delay",  # 延期
        description="为某制造集团实施 SAP ERP 系统，覆盖财务、采购、生产、销售四个模块。",
        plan_start=today - timedelta(days=240),
        plan_end=today - timedelta(days=30),   # 计划已过期，项目延期
        budget_mandays=500,
    )
    db.add(p3)
    db.flush()

    ms3_1 = Milestone(project_id=p3.id, name="蓝图设计完成", plan_date=today - timedelta(days=200),
                      actual_date=today - timedelta(days=195), status="ms_done", order_index=1)
    ms3_2 = Milestone(project_id=p3.id, name="财务模块上线", plan_date=today - timedelta(days=120),
                      actual_date=today - timedelta(days=100), status="ms_done", order_index=2,
                      description="较计划延期 20 天，因科目体系设计变更")
    ms3_3 = Milestone(project_id=p3.id, name="采购 + 生产模块上线", plan_date=today - timedelta(days=60),
                      status="ms_inprog", order_index=3,
                      description="目前已延期 60 天，正在加班赶进度")
    ms3_4 = Milestone(project_id=p3.id, name="销售模块 + 全面上线", plan_date=today - timedelta(days=30),
                      status="ms_delay", order_index=4)
    ms3_5 = Milestone(project_id=p3.id, name="系统验收", plan_date=today + timedelta(days=60),
                      status="ms_notstart", order_index=5)
    db.add_all([ms3_1, ms3_2, ms3_3, ms3_4, ms3_5])
    db.flush()

    db.add_all([
        Task(project_id=p3.id, milestone_id=ms3_3.id, name="采购模块配置与开发",
             assignee="王顾问", plan_start=today - timedelta(days=90), plan_end=today - timedelta(days=30),
             status="ms_inprog", progress=80),
        Task(project_id=p3.id, milestone_id=ms3_3.id, name="生产计划模块配置",
             assignee="赵顾问", plan_start=today - timedelta(days=60), plan_end=today - timedelta(days=10),
             status="ms_inprog", progress=55),
        Task(project_id=p3.id, milestone_id=ms3_4.id, name="销售模块配置",
             assignee="王顾问", plan_start=today - timedelta(days=10), plan_end=today + timedelta(days=30),
             status="ms_inprog", progress=25),
        Task(project_id=p3.id, milestone_id=ms3_4.id, name="集成测试（全模块）",
             assignee="刘测试", plan_start=today + timedelta(days=20), plan_end=today + timedelta(days=50),
             status="ms_notstart", progress=0),
    ])

    db.add_all([
        Issue(project_id=p3.id, title="采购模块与现有 OA 系统集成接口报错",
              description="SAP BAPI 接口调用 OA 审批流程时返回权限错误，导致采购单无法自动流转",
              severity="isev_h", source="src_inter", assignee="王顾问",
              raised_date=today - timedelta(days=15), due_date=today + timedelta(days=7),
              status="ist_doing", resolution="正在与 OA 厂商联调"),
        Issue(project_id=p3.id, title="客户关键用户流失",
              description="财务模块核心关键用户离职，新接手人员需重新培训",
              severity="isev_h", source="src_client", assignee="刘总",
              raised_date=today - timedelta(days=20), due_date=today + timedelta(days=10),
              status="ist_open"),
        Issue(project_id=p3.id, title="生产 BOM 数据清洗质量低",
              description="生产模块依赖的 BOM 数据存在大量错误，需要客户重新整理",
              severity="isev_m", source="src_client", assignee="赵顾问",
              raised_date=today - timedelta(days=30), due_date=today + timedelta(days=30),
              status="ist_doing", resolution="已提供数据清洗模板，客户 IT 部门正在处理"),
        Issue(project_id=p3.id, title="前期需求调研文档遗漏部分税务场景",
              description="发现部分复杂税务处理场景未在调研阶段识别，需补充开发",
              severity="isev_h", source="src_inter", assignee="王顾问",
              raised_date=today - timedelta(days=45),
              resolved_date=today - timedelta(days=20),
              status="ist_closed", resolution="已完成补充开发并通过客户确认"),
    ])

    db.add_all([
        Risk(project_id=p3.id, title="整体项目严重超期，面临违约风险",
             description="项目已超原定完成日期 30 天，合同包含延期赔偿条款，继续延期将产生罚款",
             probability="rp_h", impact="ri_h", level="rl_h",
             assignee="刘总", mitigation="已与客户协议签署变更单，延期至 Q2 末完成，免除违约", status="rs_open"),
        Risk(project_id=p3.id, title="顾问团队疲劳，人员稳定性风险",
             description="团队连续高强度工作超过 3 个月，有成员辞职意向",
             probability="rp_m", impact="ri_h", level="rl_h",
             assignee="刘总", mitigation="申请增加 1 名外包顾问，批准中", status="rs_open"),
        Risk(project_id=p3.id, title="客户高层变动影响项目决策",
             description="分管信息化的副总裁已离职，新任副总裁对系统的支持态度待观察",
             probability="rp_l", impact="ri_h", level="rl_h",
             assignee="刘总", mitigation="安排公司一把手拜访客户新任副总裁", status="rs_mitig"),
    ])

    for i in range(1, 9):
        db.add(ManDay(project_id=p3.id, staff_name="刘总",  role="项目总监",
                      work_date=today - timedelta(days=i*7), days=2, is_billable=True, work_content="高层汇报、风险管控"))
        db.add(ManDay(project_id=p3.id, staff_name="王顾问", role="高级顾问",
                      work_date=today - timedelta(days=i*7), days=5, is_billable=True, work_content="采购/销售模块实施"))
        db.add(ManDay(project_id=p3.id, staff_name="赵顾问", role="顾问",
                      work_date=today - timedelta(days=i*7), days=5, is_billable=True, work_content="生产模块配置"))
    for i in range(1, 5):
        db.add(ManDay(project_id=p3.id, staff_name="刘测试", role="测试工程师",
                      work_date=today - timedelta(days=i*14), days=3, is_billable=False, work_content="测试用例编写"))

    db.commit()

    # 统计
    print(f"✅ 项目：已插入 3 个（正常/预警/延期各一）")
    print(f"   里程碑：{db.query(Milestone).count()} 个")
    print(f"   工作任务：{db.query(Task).count()} 个")
    print(f"   问题台账：{db.query(Issue).count()} 条")
    print(f"   风险台账：{db.query(Risk).count()} 条")
    print(f"   人天记录：{db.query(ManDay).count()} 条")


if __name__ == "__main__":
    print("=" * 60)
    print("→ PMO 系统测试数据初始化")
    print("=" * 60)

    clear_all()
    seed_dicts()
    seed_users()
    seed_projects_and_children()

    print("=" * 60)
    print("🎉 所有测试数据已成功写入数据库！")
    print()
    print("  测试用户账号：")
    print("    admin    / admin123   （系统管理员）")
    print("    pmo_zhang/ pmo123     （PMO 角色）")
    print("    pm_li    / pm123      （项目成员）")
    print("    viewer1  / view123    （只读用户）")
    print()
    print("  测试项目：")
    print("    PMO-2024-001 某银行信贷系统实施项目  → 状态：正常")
    print("    PMO-2024-002 某市政务服务平台改造   → 状态：预警")
    print("    PMO-2025-001 某制造集团 ERP 系统实施  → 状态：延期")
    print("=" * 60)

    db.close()
