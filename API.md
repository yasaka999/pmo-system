# PMO 项目管理系统 API 文档

## 概述

本文档提供 PMO 项目管理系统的完整 API 接口说明。

**基础 URL:** `http://142.171.178.36:8000/api/v1`

**API 版本:** v1

**最后更新:** 2026-03-06

---

## 目录

- [认证](#认证)
- [用户管理](#用户管理)
- [项目管理](#项目管理)
- [里程碑管理](#里程碑管理)
- [任务管理](#任务管理)
- [问题与风险](#问题与风险)
- [工时管理](#工时管理)
- [报表统计](#报表统计)
- [系统配置](#系统配置)

---

## 认证

### 登录

获取访问令牌。

**Endpoint:**
```
POST /auth/login
```

**Content-Type:** `application/x-www-form-urlencoded`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `username` | string | 是 | 用户名 |
| `password` | string | 是 | 密码 |

**示例请求:**
```bash
curl -X POST "http://142.171.178.36:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**成功响应 (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "full_name": "管理员",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true
  }
}
```

**错误响应:**
- `400` - 用户名或密码错误
- `400` - 用户已禁用

---

### 注册

创建新用户（仅管理员可用）。

**Endpoint:**
```
POST /auth/register
```

**请求体:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `username` | string | 是 | 用户名（唯一） |
| `password` | string | 是 | 密码 |
| `full_name` | string | 否 | 全名 |
| `email` | string | 否 | 邮箱 |
| `role` | string | 否 | 角色（admin/pmo/member/viewer） |

**示例请求:**
```bash
curl -X POST "http://142.171.178.36:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "username": "newuser",
    "password": "password123",
    "full_name": "新用户",
    "email": "newuser@example.com",
    "role": "member"
  }'
```

---

### 获取当前用户信息

**Endpoint:**
```
GET /auth/me
```

**认证:** 需要 Bearer Token

**示例请求:**
```bash
curl -X GET "http://142.171.178.36:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 用户管理

### 获取用户列表

**Endpoint:**
```
GET /users/
```

**认证:** 需要 Bearer Token（仅 admin/pmo）

**响应:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "full_name": "管理员",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true
  }
]
```

---

### 更新用户

**Endpoint:**
```
PUT /users/{user_id}
```

**认证:** 需要 Bearer Token（仅 admin/pmo）

**请求体:**
```json
{
  "full_name": "新名称",
  "email": "newemail@example.com",
  "role": "pmo",
  "is_active": true
}
```

---

### 删除用户

**Endpoint:**
```
DELETE /users/{user_id}
```

**认证:** 需要 Bearer Token（仅 admin）

---

## 项目管理

### 获取项目列表

获取项目摘要列表，支持多选筛选。

**Endpoint:**
```
GET /projects/
```

**认证:** 需要 Bearer Token

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `statuses` | string | 否 | 状态多选，逗号分隔（如：正常,预警,延期） |
| `phases` | string | 否 | 阶段多选，逗号分隔（如：启动,实施,验收） |

**示例请求:**
```bash
curl -X GET "http://142.171.178.36:8000/api/v1/projects?statuses=正常,预警&phases=实施,验收" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应:**
```json
[
  {
    "id": 1,
    "code": "PMO-2024-001",
    "name": "某银行信贷系统实施项目",
    "client": "某银行",
    "manager": "张三",
    "phase": "ms_impl",
    "status": "normal",
    "plan_start": "2024-01-15",
    "plan_end": "2024-06-30",
    "milestone_count": 5,
    "open_issue_count": 2,
    "open_risk_count": 1,
    "used_mandays": 120,
    "budget_mandays": 200,
    "contract_no": "HT-2024-001",
    "region": "北京",
    "plan_delivery_date": "2024-06-15",
    "actual_delivery_date": null,
    "plan_initial_acceptance_date": "2024-06-20",
    "actual_initial_acceptance_date": null,
    "plan_final_acceptance_date": "2024-06-30",
    "actual_final_acceptance_date": null
  }
]
```

---

### 获取单个项目详情

**Endpoint:**
```
GET /projects/{project_id}
```

**认证:** 需要 Bearer Token

**权限:** 
- admin/pmo：可查看所有项目
- member/viewer：只能查看自己创建的项目

**响应:**
```json
{
  "id": 1,
  "code": "PMO-2024-001",
  "name": "某银行信贷系统实施项目",
  "client": "某银行",
  "manager": "张三",
  "phase": "ms_impl",
  "status": "normal",
  "description": "项目描述...",
  "plan_start": "2024-01-15",
  "plan_end": "2024-06-30",
  "actual_start": "2024-01-20",
  "actual_end": null,
  "budget_mandays": 200,
  "contract_no": "HT-2024-001",
  "region": "北京",
  "plan_delivery_date": "2024-06-15",
  "actual_delivery_date": null,
  "plan_initial_acceptance_date": "2024-06-20",
  "actual_initial_acceptance_date": null,
  "plan_final_acceptance_date": "2024-06-30",
  "actual_final_acceptance_date": null,
  "created_by": 1,
  "created_at": "2024-01-10T08:00:00",
  "updated_at": "2024-03-05T16:30:00"
}
```

---

### 创建项目

**Endpoint:**
```
POST /projects/
```

**认证:** 需要 Bearer Token

**请求体:**
```json
{
  "code": "PMO-2024-002",
  "name": "新项目",
  "client": "客户名称",
  "manager": "项目经理",
  "phase": "ms_init",
  "status": "normal",
  "description": "项目描述",
  "plan_start": "2024-03-01",
  "plan_end": "2024-08-31",
  "budget_mandays": 300,
  "contract_no": "HT-2024-002",
  "region": "上海",
  "plan_delivery_date": "2024-08-15",
  "plan_initial_acceptance_date": "2024-08-20",
  "plan_final_acceptance_date": "2024-08-31"
}
```

**字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `code` | string | 是 | 项目编号（唯一） |
| `name` | string | 是 | 项目名称 |
| `client` | string | 否 | 客户名称 |
| `manager` | string | 否 | 项目经理 |
| `phase` | string | 否 | 项目阶段（字典值） |
| `status` | string | 否 | 项目状态（字典值） |
| `description` | string | 否 | 项目描述 |
| `plan_start` | date | 否 | 计划开始日期 |
| `plan_end` | date | 否 | 计划结束日期 |
| `budget_mandays` | integer | 否 | 预算人天 |
| `contract_no` | string | 否 | 合同编号 |
| `region` | string | 否 | 区域 |
| `plan_delivery_date` | date | 否 | 计划交付日期 |
| `plan_initial_acceptance_date` | date | 否 | 计划初验日期 |
| `plan_final_acceptance_date` | date | 否 | 计划终验日期 |

---

### 更新项目

**Endpoint:**
```
PUT /projects/{project_id}
```

**认证:** 需要 Bearer Token

**权限:** 仅项目创建者或 admin/pmo 可编辑

**请求体:** （部分更新，只传需要修改的字段）
```json
{
  "name": "更新后的项目名称",
  "status": "warning",
  "actual_end": "2024-07-15"
}
```

---

### 删除项目

**Endpoint:**
```
DELETE /projects/{project_id}
```

**认证:** 需要 Bearer Token

**权限:** 仅项目创建者或 admin/pmo 可删除

---

## 里程碑管理

### 获取里程碑列表

**Endpoint:**
```
GET /projects/{project_id}/milestones
```

**认证:** 需要 Bearer Token

**响应:**
```json
[
  {
    "id": 1,
    "project_id": 1,
    "name": "需求分析完成",
    "plan_date": "2024-02-15",
    "actual_date": "2024-02-14",
    "status": "ms_done",
    "order_index": 1
  }
]
```

---

### 创建里程碑

**Endpoint:**
```
POST /projects/{project_id}/milestones
```

**认证:** 需要 Bearer Token

**请求体:**
```json
{
  "name": "设计评审完成",
  "plan_date": "2024-03-15",
  "actual_date": null,
  "status": "ms_notstart",
  "order_index": 2
}
```

---

### 更新里程碑

**Endpoint:**
```
PUT /milestones/{milestone_id}
```

**认证:** 需要 Bearer Token

---

### 删除里程碑

**Endpoint:**
```
DELETE /milestones/{milestone_id}
```

**认证:** 需要 Bearer Token

---

## 任务管理

### 获取任务列表

**Endpoint:**
```
GET /projects/{project_id}/tasks
```

**认证:** 需要 Bearer Token

**响应:**
```json
[
  {
    "id": 1,
    "project_id": 1,
    "title": "数据库设计",
    "assignee": "李四",
    "status": "todo",
    "priority": "high",
    "due_date": "2024-03-10",
    "completed": false
  }
]
```

---

### 创建任务

**Endpoint:**
```
POST /projects/{project_id}/tasks
```

**认证:** 需要 Bearer Token

**请求体:**
```json
{
  "title": "API 接口开发",
  "assignee": "王五",
  "status": "in_progress",
  "priority": "medium",
  "due_date": "2024-03-20",
  "completed": false
}
```

---

### 更新任务

**Endpoint:**
```
PUT /tasks/{task_id}
```

**认证:** 需要 Bearer Token

---

### 删除任务

**Endpoint:**
```
DELETE /tasks/{task_id}
```

**认证:** 需要 Bearer Token

---

## 问题与风险

### 获取问题列表

**Endpoint:**
```
GET /projects/{project_id}/issues
```

**认证:** 需要 Bearer Token

**响应:**
```json
[
  {
    "id": 1,
    "project_id": 1,
    "title": "第三方接口延迟",
    "description": "供应商接口响应时间过长",
    "severity": "high",
    "status": "open",
    "created_at": "2024-03-01T10:00:00"
  }
]
```

---

### 创建问题

**Endpoint:**
```
POST /projects/{project_id}/issues
```

**认证:** 需要 Bearer Token

---

### 更新问题

**Endpoint:**
```
PUT /issues/{issue_id}
```

**认证:** 需要 Bearer Token

---

### 删除问题

**Endpoint:**
```
DELETE /issues/{issue_id}
```

**认证:** 需要 Bearer Token

---

### 获取风险列表

**Endpoint:**
```
GET /projects/{project_id}/risks
```

**认证:** 需要 Bearer Token

---

### 创建风险

**Endpoint:**
```
POST /projects/{project_id}/risks
```

**认证:** 需要 Bearer Token

---

## 工时管理

### 获取工时记录

**Endpoint:**
```
GET /projects/{project_id}/mandays
```

**认证:** 需要 Bearer Token

**响应:**
```json
[
  {
    "id": 1,
    "project_id": 1,
    "date": "2024-03-01",
    "person": "张三",
    "days": 1.0,
    "description": "需求分析"
  }
]
```

---

### 添加工时

**Endpoint:**
```
POST /projects/{project_id}/mandays
```

**认证:** 需要 Bearer Token

**请求体:**
```json
{
  "date": "2024-03-05",
  "person": "李四",
  "days": 0.5,
  "description": "代码评审"
}
```

---

### 更新工时

**Endpoint:**
```
PUT /mandays/{manday_id}
```

**认证:** 需要 Bearer Token

---

### 删除工时

**Endpoint:**
```
DELETE /mandays/{manday_id}
```

**认证:** 需要 Bearer Token

---

## 报表统计

### 获取项目统计

**Endpoint:**
```
GET /reports/projects
```

**认证:** 需要 Bearer Token

**响应:**
```json
{
  "total_projects": 23,
  "by_status": {
    "normal": 15,
    "warning": 5,
    "delayed": 3
  },
  "by_phase": {
    "ms_init": 3,
    "ms_impl": 12,
    "ms_accept": 8
  }
}
```

---

### 获取工时统计

**Endpoint:**
```
GET /reports/mandays
```

**认证:** 需要 Bearer Token

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `start_date` | date | 否 | 开始日期 |
| `end_date` | date | 否 | 结束日期 |
| `project_id` | integer | 否 | 项目ID |

---

## 系统配置

### 获取字典列表

**Endpoint:**
```
GET /sys-dicts/
```

**认证:** 需要 Bearer Token

**响应:**
```json
[
  {
    "id": 1,
    "dict_type": "project_status",
    "dict_value": "normal",
    "label": "正常",
    "color": "success",
    "sort_order": 1
  }
]
```

---

### 批量保存字典

**Endpoint:**
```
POST /sys-dicts/batch-save
```

**认证:** 需要 Bearer Token

**请求体:**
```json
{
  "items": [
    {
      "id": 1,
      "dict_type": "project_status",
      "dict_value": "normal",
      "label": "正常",
      "color": "success",
      "sort_order": 1
    },
    {
      "dict_type": "project_status",
      "dict_value": "paused",
      "label": "暂停",
      "color": "info",
      "sort_order": 4
    }
  ],
  "deleted_ids": [5, 6]
}
```

---

### 获取看板小部件配置

**Endpoint:**
```
GET /sys-dicts/widgets
```

**认证:** 需要 Bearer Token

**响应:**
```json
[
  {
    "id": 10,
    "dict_type": "dashboard_widget",
    "dict_value": "project_stats",
    "label": "项目统计",
    "color": "primary",
    "sort_order": 1,
    "enabled": true
  }
]
```

---

## 错误处理

### 错误响应格式

所有错误遵循以下格式：

```json
{
  "detail": "错误信息"
}
```

### HTTP 状态码

| 状态码 | 含义 | 常见场景 |
|--------|------|----------|
| 200 | 成功 | GET/PUT 请求成功 |
| 201 | 创建成功 | POST 请求成功 |
| 204 | 无内容 | DELETE 请求成功 |
| 400 | 请求错误 | 参数验证失败、重复数据 |
| 401 | 未认证 | 缺少 Token 或 Token 无效 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 未找到 | 资源不存在 |
| 422 | 验证错误 | 请求体格式错误 |
| 500 | 服务器错误 | 内部错误 |

---

## 数据字典

### 项目状态 (project_status)

| 值 | 标签 | 颜色 |
|----|------|------|
| normal | 正常 | success (绿色) |
| warning | 预警 | warning (黄色) |
| delayed | 延期 | danger (红色) |
| paused | 暂停 | info (蓝色) |

### 项目阶段 (project_phase)

| 值 | 标签 | 颜色 |
|----|------|------|
| ms_init | 启动 | primary |
| ms_plan | 规划 | info |
| ms_impl | 实施 | warning |
| ms_accept | 验收 | success |

### 里程碑状态 (milestone_status)

| 值 | 标签 | 颜色 |
|----|------|------|
| ms_notstart | 未开始 | info |
| ms_inprog | 进行中 | primary |
| ms_done | 已完成 | success |
| ms_delay | 延期 | danger |

### 用户角色

| 角色 | 权限 |
|------|------|
| admin | 完全权限 |
| pmo | 管理所有项目、用户 |
| member | 管理自己的项目 |
| viewer | 只读访问 |

---

## 前端访问地址

**Web 界面:** http://142.171.178.36:9000

**测试账号:**
- admin / admin123
- pmo_zhang / pmo123
- pm_li / pm123
- viewer1 / view123
