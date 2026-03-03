# PMO 实施项目管理系统

> 面向 PMO 团队的轻量级项目进度管理与汇报平台

## ✨ 功能特性

- **项目管理** 项目全生命周期跟踪（状态/阶段/计划日期/预算人天）
- **里程碑 & 任务** 里程碑节点+工作任务分解，甘特式进度追踪
- **问题台账** 多维度问题管理（严重等级/来源/负责人/解决方案）
- **风险台账** 风险概率×影响矩阵，自动生成风险级别
- **人天管理** 按项目跟踪投入人天，预算/实际对比进度条
- **报告导出** 一键生成 Word 项目周报/月报、Excel 台账；整体 Portfolio Report（Word + Excel）
- **系统配置** 可视化管理所有可配置选项（项目状态/阶段/问题/风险等字段枚举值）
- **用户管理** 多角色权限（admin / pmo / member / viewer），admin 统一管理用户
- **总览看板** 统计卡片可点击展示详情（问题/风险/项目列表等）
- **筛选多选** 项目列表支持状态/阶段多选筛选

## 🏗️ 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.10+ / FastAPI / SQLAlchemy / SQLite |
| 报告生成 | python-docx / openpyxl |
| 前端 | Vue 3 / Vite / Element Plus / Pinia |
| 认证 | JWT Bearer Token |

## 📁 项目结构

```
pmo-system/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # FastAPI 路由（projects/issues/risks/milestones/mandays/reports/users）
│   │   ├── core/          # 安全/认证配置
│   │   ├── crud/          # 数据库 CRUD 操作
│   │   ├── db/            # 数据库会话/基类
│   │   ├── models/        # SQLAlchemy 模型
│   │   ├── schemas/       # Pydantic 请求/响应 Schema
│   │   └── services/      # 报告生成服务
│   ├── seed_data.py       # 测试数据初始化脚本
│   ├── requirements.txt
│   └── start.sh
└── frontend/
    ├── src/
    │   ├── api/           # Axios API 封装
    │   ├── components/    # 公共组件（ConfigSection 等）
    │   ├── layouts/       # 主布局（侧边栏/顶栏）
    │   ├── router/        # Vue Router
    │   ├── stores/        # Pinia Store（auth/dict）
    │   └── views/         # 页面视图
    ├── vite.config.js
    └── package.json
```

## 🚀 快速启动

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 注入测试数据（可选）

```bash
cd backend && python seed_data.py
```

### 前端

```bash
cd frontend
npm install
npm run dev        # 开发模式，访问 http://localhost:3000
```

## 🔑 默认账户

| 账号 | 密码 | 角色 |
|---|---|---|
| `admin` | `admin123` | 系统管理员（全权限） |
| `pmo_zhang` | `pmo123` | PMO（管理所有项目 + 整体报告） |
| `pm_li` | `pm123` | 项目成员（仅管理自己的项目） |
| `viewer1` | `view123` | 只读用户 |

## 📋 角色权限说明

| 功能 | member | pmo | admin |
|---|---|---|---|
| 查看/管理自己的项目 | ✅ | ✅ | ✅ |
| 管理所有项目 | ❌ | ✅ | ✅ |
| 整体报告 | ❌ | ✅ | ✅ |
| 用户管理 / 系统配置 | ❌ | ❌ | ✅ |

## 📄 License

MIT
