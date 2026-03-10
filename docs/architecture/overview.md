# PMO 项目管理系统 - 架构概览

## 系统概述

PMO（Project Management Office）项目管理系统是一个面向企业的项目管理解决方案，支持项目进度跟踪、问题风险管理、人天成本控制和报告生成。

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.12)
- **数据库**: PostgreSQL (生产环境) / SQLite (开发环境)
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT (JSON Web Tokens)
- **密码加密**: bcrypt

### 前端
- **框架**: Vue 3 + Vite
- **状态管理**: Pinia
- **UI 组件**: Element Plus
- **构建工具**: Vite
- **路由**: Vue Router

### 部署
- **后端端口**: 8000
- **前端端口**: 3000
- **反向代理**: 可选（Nginx/Cloudflare Tunnel）

## 系统架构

```
┌─────────────┐
│   用户界面   │
│  (浏览器)   │
└──────┬──────┘
       │ HTTP/HTTPS
       ▼
┌─────────────┐
│  前端服务    │
│ (Vue 3 SPA) │
│ Port: 3000  │
└──────┬──────┘
       │ REST API
       ▼
┌─────────────┐
│  后端服务    │
│ (FastAPI)   │
│ Port: 8000  │
└──────┬──────┘
       │ SQL
       ▼
┌─────────────┐
│  PostgreSQL │
│   数据库    │
└─────────────┘
```

## 核心模块

### 1. 项目管理模块
- 项目创建/编辑/删除
- 项目状态跟踪（正常/预警/延期/暂停/已完成）
- 项目阶段管理（售前/启动/实施/验收/收尾）
- 项目预算管理

### 2. 里程碑管理
- 里程碑计划
- 任务分解
- 进度跟踪
- 甘特图展示

### 3. 问题与风险管理
- 问题登记与跟踪
- 风险识别与评估
- 风险矩阵分析
- 问题/风险关闭流程

### 4. 人天成本管理
- 人天填报
- 成本统计
- 预算执行分析
- 计费/非计费区分

### 5. 周报管理
- 周报填报
- 周报汇总
- 项目进展跟踪
- 周报导出（Excel）

### 6. 报告生成
- 项目周报（Word）
- 项目月报（Word）
- 问题风险台账（Excel）
- 人天统计报表（Excel）
- 项目组合报告（Word/Excel）

## 数据模型

### 核心实体关系

```
User (用户)
  ├── creates → Project (项目)
  └── reports → WeeklyProgress (周报)

Project (项目)
  ├── has → Milestone (里程碑)
  │         └── has → Task (任务)
  ├── has → Issue (问题)
  ├── has → Risk (风险)
  ├── has → ManDay (人天)
  └── has → WeeklyProgress (周报)
```

## 安全机制

### 认证
- JWT Token 认证
- Token 有效期：8 小时
- 支持 Token 刷新

### 授权
- 角色基于权限控制（RBAC）
- 角色：admin / pmo / member / viewer
- 项目级权限控制

### 数据安全
- 密码 bcrypt 加密
- SQL 注入防护（ORM 参数化）
- CORS 跨域控制

## 性能优化

### 后端优化
- 数据库连接池
- 查询优化（聚合查询）
- API 响应时间：< 20ms

### 前端优化
- 组件懒加载
- 数据缓存
- 按需加载

## 部署架构

### 开发环境
```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

### 生产环境
```bash
# 后端（使用 systemd 或 supervisor）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 前端（使用 serve 或 Nginx）
serve -s dist -l 3000
```

## 监控与日志

### 日志
- 后端日志：`backend_log.txt`
- 前端错误：浏览器控制台
- 数据库日志：PostgreSQL 日志

### 监控指标
- API 响应时间
- 数据库查询性能
- 前端加载时间
- 错误率统计

## 扩展性

### 水平扩展
- 后端多实例部署
- 数据库读写分离
- 前端 CDN 加速

### 功能扩展
- 插件化架构
- API 版本控制
- Webhook 支持（计划中）

## 相关文档

- [数据流文档](./data-flow.md)
- [部署指南](../runbooks/deploy.md)
- [开发指南](../runbooks/local-dev.md)
- [API 文档](../../API.md)
