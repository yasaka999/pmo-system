from fastapi import APIRouter
from app.api.v1 import auth, projects, milestones, issues_risks, mandays, reports, sys_dicts, users, weekly_progress, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["系统管理 - 用户"])
api_router.include_router(sys_dicts.router, prefix="/sys-dicts", tags=["系统管理 - 数据字典"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理员功能"])  # 新增
api_router.include_router(projects.router, prefix="/projects", tags=["项目管理"])
api_router.include_router(milestones.router, prefix="", tags=["里程碑与任务"])
api_router.include_router(issues_risks.router, prefix="", tags=["问题与风险"])
api_router.include_router(mandays.router, prefix="", tags=["人天管理"])
api_router.include_router(weekly_progress.router, prefix="", tags=["周报进展"])
api_router.include_router(reports.router, prefix="", tags=["报告生成"])
