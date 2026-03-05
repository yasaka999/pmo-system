# PMO 系统架构文档

## 系统概述

PMO 项目管理系统是一个面向项目管理办公室（PMO）的轻量级 Web 应用，用于跟踪项目全生命周期、管理里程碑、记录问题风险、统计工时投入，并生成各类报告。

---

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Web 浏览器  │  │   移动端    │  │    报告下载 (Word/Excel) │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                           │
                    HTTP/HTTPS
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                      Nginx (反向代理)                         │
│              端口: 9000 (前端) / 8000 (API)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
┌─────────▼──────────┐           ┌──────────▼──────────┐
│     前端服务        │           │      后端服务        │
│   Vue 3 + Vite     │           │   FastAPI (Python)  │
│   Element Plus UI  │◄─────────►│   SQLite 数据库      │
│   Pinia 状态管理   │   REST API │   JWT 认证          │
└────────────────────┘           └─────────────────────┘
```

---

## 技术栈详解

### 后端技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | FastAPI | 0.104+ | 高性能异步 Web 框架 |
| ORM | SQLAlchemy | 2.0+ | 数据库对象关系映射 |
| 数据库 | SQLite | 3.x | 轻量级文件数据库 |
| 认证 | PyJWT | 2.8+ | JWT Token 生成与验证 |
| 密码哈希 | Passlib | 1.7+ | bcrypt 密码加密 |
| 文档生成 | python-docx | 1.1+ | Word 报告生成 |
| Excel 处理 | openpyxl | 3.1+ | Excel 报表生成 |
| 服务器 | Uvicorn | 0.24+ | ASGI 服务器 |

### 前端技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | Vue 3 | 3.3+ | 渐进式 JavaScript 框架 |
| 构建工具 | Vite | 5.0+ | 快速开发构建工具 |
| UI 组件库 | Element Plus | 2.4+ | Vue 3 企业级组件库 |
| 状态管理 | Pinia | 2.1+ | Vue 官方状态管理 |
| HTTP 客户端 | Axios | 1.6+ | API 请求封装 |
| 路由 | Vue Router | 4.2+ | 单页应用路由管理 |
| 图标 | Element Plus Icons | - | 图标库 |

---

## 目录结构

```
pmo-system/
├── backend/                          # 后端代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 应用入口
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py             # 路由聚合器
│   │   │   └── v1/                   # API v1 版本
│   │   │       ├── __init__.py
│   │   │       ├── auth.py           # 认证相关（登录/注册/用户信息）
│   │   │       ├── projects.py       # 项目管理 CRUD
│   │   │       ├── milestones.py     # 里程碑 & 任务管理
│   │   │       ├── issues_risks.py   # 问题 & 风险管理
│   │   │       ├── mandays.py        # 工时管理
│   │   │       ├── reports.py        # 报告生成
│   │   │       ├── users.py          # 用户管理
│   │   │       └── sys_dicts.py      # 系统字典配置
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # 应用配置
│   │   │   └── security.py           # 安全/认证工具
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   ├── crud_project.py       # 项目数据操作
│   │   │   ├── crud_milestone.py     # 里程碑数据操作
│   │   │   ├── crud_issue.py         # 问题数据操作
│   │   │   ├── crud_risk.py          # 风险数据操作
│   │   │   ├── crud_manday.py        # 工时数据操作
│   │   │   ├── crud_user.py          # 用户数据操作
│   │   │   └── crud_sys_dict.py      # 字典数据操作
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # SQLAlchemy 基类
│   │   │   └── session.py            # 数据库会话管理
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── project.py            # 项目模型
│   │   │   ├── milestone.py          # 里程碑 & 任务模型
│   │   │   ├── issue.py              # 问题模型
│   │   │   ├── risk.py               # 风险模型
│   │   │   ├── manday.py             # 工时模型
│   │   │   ├── user.py               # 用户模型
│   │   │   └── sys_dict.py           # 字典模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py            # Pydantic 数据模型
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── report_generator.py   # Word 报告生成
│   │       └── excel_generator.py    # Excel 报表生成
│   ├── migrations/                   # 数据库迁移（预留）
│   ├── init_data.py                  # 基础数据初始化
│   ├── seed_data.py                  # 测试数据注入
│   ├── requirements.txt              # Python 依赖
│   └── start.sh                      # 启动脚本
│
├── frontend/                         # 前端代码
│   ├── src/
│   │   ├── api/
│   │   │   ├── index.js              # API 接口封装
│   │   │   └── request.js            # Axios 实例配置
│   │   ├── components/
│   │   │   └── ConfigSection.vue     # 配置区块组件
│   │   ├── layouts/
│   │   │   └── MainLayout.vue        # 主布局组件
│   │   ├── router/
│   │   │   └── index.js              # 路由配置
│   │   ├── stores/
│   │   │   ├── auth.js               # 认证状态管理
│   │   │   └── dict.js               # 字典状态管理
│   │   ├── views/
│   │   │   ├── LoginView.vue         # 登录页面
│   │   │   ├── DashboardView.vue     # 总览看板
│   │   │   ├── ProjectListView.vue   # 项目列表
│   │   │   ├── ProjectDetailView.vue # 项目详情
│   │   │   ├── MilestoneView.vue     # 里程碑管理
│   │   │   ├── IssueView.vue         # 问题台账
│   │   │   ├── RiskView.vue          # 风险台账
│   │   │   ├── ManDayView.vue        # 工时管理
│   │   │   ├── ReportView.vue        # 报告中心
│   │   │   ├── UserListView.vue      # 用户管理
│   │   │   └── SystemConfigView.vue  # 系统配置
│   │   ├── App.vue                   # 根组件
│   │   └── main.js                   # 应用入口
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── docs/                             # 文档
│   ├── API.md                        # API 接口文档
│   ├── ARCHITECTURE.md               # 架构文档
│   └── DEPLOYMENT.md                 # 部署指南
│
└── README.md                         # 项目说明
```

---

## 数据模型关系

```
┌─────────────────┐
│     User        │
├─────────────────┤
│ id (PK)         │
│ username        │
│ hashed_password │
│ full_name       │
│ email           │
│ role            │
│ is_active       │
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────┐
│    Project      │◄──────│   Milestone     │
├─────────────────┤  1:N  ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ code            │       │ project_id (FK) │
│ name            │       │ name            │
│ client          │       │ plan_date       │
│ manager         │       │ actual_date     │
│ phase           │       │ status          │
│ status          │       │ order_index     │
│ description     │       └─────────────────┘
│ plan_start      │
│ plan_end        │       ┌─────────────────┐
│ actual_start    │◄──────│      Task       │
│ actual_end      │  1:N  ├─────────────────┤
│ budget_mandays  │       │ id (PK)         │
│ contract_no     │       │ project_id (FK) │
│ region          │       │ title           │
│ created_by (FK) │       │ assignee        │
└────────┬────────┘       │ status          │
         │                │ priority        │
         │ 1:N            │ due_date        │
         ▼                │ completed       │
┌─────────────────┐       └─────────────────┘
│      Issue      │
├─────────────────┤
│ id (PK)         │       ┌─────────────────┐
│ project_id (FK) │◄──────│      Risk       │
│ title           │  1:N  ├─────────────────┤
│ description     │       │ id (PK)         │
│ severity        │       │ project_id (FK) │
│ source          │       │ title           │
│ owner           │       │ probability     │
│ solution        │       │ impact          │
│ status          │       │ level           │
│ due_date        │       │ status          │
└─────────────────┘       │ mitigation      │
                          └─────────────────┘
┌─────────────────┐
│     ManDay      │
├─────────────────┤
│ id (PK)         │
│ project_id (FK) │
│ date            │
│ person          │
│ days            │
│ description     │
└─────────────────┘

┌─────────────────┐
│    SysDict      │
├─────────────────┤
│ id (PK)         │
│ dict_type       │
│ dict_value      │
│ label           │
│ color           │
│ sort_order      │
└─────────────────┘
```

---

## 核心流程

### 1. 用户认证流程

```
┌─────────┐    POST /auth/login    ┌─────────┐    验证密码    ┌─────────┐
│  客户端  │ ──────────────────────►│  FastAPI │──────────────►│  SQLite  │
│         │  {username, password}  │         │               │         │
│         │◄───────────────────────│         │◄──────────────│         │
│         │   {token, user_info}   │         │   生成 JWT    │         │
└─────────┘                        └─────────┘               └─────────┘
```

### 2. 项目创建流程

```
┌─────────┐   POST /projects/   ┌─────────┐   权限检查   ┌─────────┐
│  客户端  │ ──────────────────►│  FastAPI │───────────►│  当前用户 │
│         │  {project_data}    │         │            │         │
│         │◄───────────────────│         │◄───────────│         │
│         │   {project_out}    │         │  写入数据库  │  SQLite  │
└─────────┘                    └─────────┘────────────►│         │
                                                       └─────────┘
```

### 3. 报告生成流程

```
┌─────────┐  GET /reports/portfolio  ┌─────────┐  查询数据  ┌─────────┐
│  客户端  │ ────────────────────────►│  FastAPI │─────────►│  SQLite  │
│         │                          │         │          │         │
│         │◄─────────────────────────│         │◄─────────│         │
│         │   application/vnd.openxml│  Report │  生成文档 │         │
│         │   (Word/Excel 文件流)     │Generator│          │         │
└─────────┘                          └─────────┘          └─────────┘
```

---

## 权限控制设计

### 角色权限矩阵

| 功能 | viewer | member | pmo | admin |
|------|--------|--------|-----|-------|
| 查看所有项目 | ✅ | ✅ | ✅ | ✅ |
| 创建项目 | ❌ | ✅ | ✅ | ✅ |
| 编辑自己的项目 | ❌ | ✅ | ✅ | ✅ |
| 编辑所有项目 | ❌ | ❌ | ✅ | ✅ |
| 删除自己的项目 | ❌ | ✅ | ✅ | ✅ |
| 删除所有项目 | ❌ | ❌ | ✅ | ✅ |
| 查看所有用户 | ❌ | ❌ | ✅ | ✅ |
| 管理用户 | ❌ | ❌ | ❌ | ✅ |
| 系统配置 | ❌ | ❌ | ❌ | ✅ |
| 整体报告 | ❌ | ❌ | ✅ | ✅ |

### 权限检查实现

```python
# backend/app/api/v1/projects.py

def _can_manage(project: Project, current_user: User) -> bool:
    """判断当前用户是否有权限管理该项目（编辑/删除）"""
    if current_user.role in ("admin", "pmo"):
        return True
    # member/viewer 只能管理自己创建的项目
    return project.created_by == current_user.id

@router.put("/{project_id}")
def update_project(...):
    if not _can_manage(project, current_user):
        raise HTTPException(status_code=403, detail="无权编辑该项目")
    # ...
```

---

## 关键设计决策

### 1. 为什么选择 SQLite？

**决策:** 使用 SQLite 作为生产数据库

**原因:**
- 部署简单，无需单独安装数据库服务
- 适合中小型项目（<100个项目，<10个并发用户）
- 单文件备份方便
- 性能足够满足当前需求

**权衡:**
- 不支持高并发写入
- 无内置用户权限管理
- 不适合水平扩展

**未来演进:** 如需支持更多用户，可迁移至 PostgreSQL

---

### 2. 前后端分离 vs 单体应用

**决策:** 前后端分离架构

**原因:**
- 前端可以独立开发和部署
- 后端 API 可被其他客户端复用（如移动端）
- 团队分工明确

**实现:**
- 前端：Vue 3 SPA，Nginx 托管
- 后端：FastAPI，提供 RESTful API
- 通信：JSON over HTTP

---

### 3. 字典值存储设计

**决策:** 数据库中存储字典值（code），界面显示标签（label）

**示例:**
```python
# 数据库中存储
project.status = "normal"  # 不是 "正常"

# 界面显示通过字典转换
label = dict_store.get_label("project_status", "normal")  # "正常"
color = dict_store.get_color("project_status", "normal")  # "success"
```

**优点:**
- 支持多语言
- 标签可修改不影响数据
- 便于程序逻辑判断

---

### 4. 批量保存优化

**问题:** 系统配置页面有 50+ 字典项，逐个保存需要 50+ 次 API 请求

**解决方案:**
```python
# 新增批量保存端点
@router.post("/sys-dicts/batch-save")
def batch_save_sys_dicts(data: SysDictBatchSave, ...):
    # 批量插入/更新
    for item in data.items:
        if item.id:
            update_item(item)
        else:
            create_item(item)
    # 批量删除
    for id in data.deleted_ids:
        delete_item(id)
```

---

## 性能考虑

### 数据库优化

1. **索引设计**
   - `project.code` - 唯一索引
   - `project.status`, `project.phase` - 普通索引（筛选用）
   - `milestone.project_id` - 外键索引
   - `issue.project_id`, `risk.project_id` - 外键索引

2. **查询优化**
   - 项目列表使用摘要视图（ProjectSummary），避免加载完整项目数据
   - 关联查询使用 SQLAlchemy 的 `joinedload` 减少 N+1 问题

### 缓存策略

- **字典数据:** 前端 Pinia Store 缓存，登录时一次性加载
- **用户会话:** JWT Token，服务端无状态

---

## 安全设计

### 1. 认证机制

- JWT Bearer Token
- Token 有效期：默认 24 小时
- 密码：bcrypt 哈希存储

### 2. 权限控制

- 基于角色的访问控制（RBAC）
- 资源级别权限检查（只能操作自己的项目）

### 3. 输入验证

- Pydantic Schema 自动验证
- SQL 注入防护：SQLAlchemy ORM 参数化查询
- XSS 防护：前端 Vue 模板自动转义

### 4. 部署安全

- 生产环境关闭调试模式
- 使用 HTTPS（建议配置 SSL 证书）
- 数据库文件权限限制

---

## 扩展性设计

### 1. 模块化架构

- API 版本化（/api/v1/）
- 按功能模块划分（projects, issues, risks 等）
- 服务层抽象（report_generator, excel_generator）

### 2. 插件化报告

```python
# 可扩展的报告生成器
class ReportGenerator:
    def generate_word(self, template, data): ...
    def generate_excel(self, template, data): ...
    
# 新增报告类型只需添加方法
def generate_pdf(self, template, data): ...
```

### 3. 字典驱动的 UI

- 所有下拉选项通过字典配置
- 新增选项无需修改代码
- 支持颜色、排序等可视化配置

---

## 监控与运维

### 日志

- 后端：Uvicorn 访问日志 + 应用日志
- 前端：浏览器控制台日志

### 备份

```bash
# 数据库自动备份脚本（已配置 cron）
0 2 * * * cp /opt/pmo-system-new/backend/pmo.db /backup/pmo_$(date +\%Y\%m\%d).db
```

### 健康检查

```bash
# API 健康检查
curl http://localhost:8000/api/v1/projects/
```

---

## 开发规范

### Git 提交规范

使用 Conventional Commits：

```
feat: 新增功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

### 代码风格

- Python: PEP 8，使用 Black 格式化
- JavaScript: ESLint + Prettier

---

## 待改进项

1. **数据库迁移** - 使用 Alembic 管理 schema 变更
2. **单元测试** - 补充 pytest 测试用例
3. **API 文档** - 集成 Swagger UI 自动生成
4. **性能监控** - 添加响应时间统计
5. **消息通知** - 里程碑到期提醒、问题分配通知
