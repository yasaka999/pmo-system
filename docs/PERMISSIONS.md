# PMO 系统权限管理文档

## 概述

PMO 系统采用基于角色的访问控制（RBAC），定义了 4 种不同的用户角色，每种角色具有不同的权限级别。

---

## 用户角色

| 角色代码 | 角色名称 | 说明 | 适用人群 |
|---------|---------|------|---------|
| **admin** | 系统管理员 | 最高权限，管理所有资源和用户 | IT 管理员、系统运维 |
| **pmo** | PMO 管理员 | 管理所有项目，查看项目组合报告 | PMO 办公室成员 |
| **member** | 项目成员 | 管理自己创建的项目，参与项目执行 | 项目经理、项目成员 |
| **viewer** | 只读用户 | 只能查看项目信息，不能修改 | 高层管理者、审计人员 |

---

## 权限矩阵

### 1. 用户管理权限

| 功能 | admin | pmo | member | viewer |
|------|-------|-----|--------|--------|
| 查看所有用户 | ✅ | ❌ | ❌ | ❌ |
| 创建用户 | ✅ | ❌ | ❌ | ❌ |
| 编辑用户信息 | ✅ | ❌ | ❌ | ❌ |
| 启用/停用账号 | ✅ | ❌ | ❌ | ❌ |
| 删除用户 | ✅ | ❌ | ❌ | ❌ |
| 修改自己信息 | ✅ | ✅ | ✅ | ✅ |

**实现代码**:
```python
# backend/app/api/v1/users.py
@router.get("/", response_model=List[schemas.UserOut])
def read_users(...):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有权限查看所有用户")
```

---

### 2. 项目管理权限

| 功能 | admin | pmo | member | viewer |
|------|-------|-----|--------|--------|
| 查看所有项目 | ✅ | ✅ | ❌ | ❌ |
| 创建项目 | ✅ | ✅ | ✅ | ❌ |
| 编辑任意项目 | ✅ | ✅ | ❌ | ❌ |
| 编辑自己创建的项目 | ✅ | ✅ | ✅ | ❌ |
| 删除任意项目 | ✅ | ✅ | ❌ | ❌ |
| 删除自己创建的项目 | ✅ | ✅ | ✅ | ❌ |
| 查看自己创建的项目 | ✅ | ✅ | ✅ | ✅ |

**实现代码**:
```python
# backend/app/api/v1/projects.py
def _can_manage(project: Project, current_user: User) -> bool:
    """判断当前用户是否有权限管理该项目"""
    if current_user.role in ("admin", "pmo"):
        return True
    # member 只能管理自己创建的项目
    return project.created_by == current_user.id

# 项目列表查询时的权限过滤
if current_user.role not in ("admin", "pmo"):
    # member 只能看到自己的项目
    query = query.filter(
        (Project.created_by == current_user.id) | 
        (Project.created_by.is_(None))
    )
```

---

### 3. 里程碑与任务管理

| 功能 | admin | pmo | member | viewer |
|------|-------|-----|--------|--------|
| 创建里程碑 | ✅ | ✅ | ✅* | ❌ |
| 编辑里程碑 | ✅ | ✅ | ✅* | ❌ |
| 删除里程碑 | ✅ | ✅ | ✅* | ❌ |
| 创建任务 | ✅ | ✅ | ✅* | ❌ |
| 更新任务状态 | ✅ | ✅ | ✅* | ❌ |

*member 只能管理自己创建的项目中的里程碑和任务

---

### 4. 问题与风险管理

| 功能 | admin | pmo | member | viewer |
|------|-------|-----|--------|--------|
| 查看所有问题/风险 | ✅ | ✅ | ✅* | ✅* |
| 创建问题/风险 | ✅ | ✅ | ✅* | ❌ |
| 编辑问题/风险 | ✅ | ✅ | ✅* | ❌ |
| 关闭问题/风险 | ✅ | ✅ | ✅* | ❌ |

*member 只能查看自己创建的项目中的问题/风险

---

### 5. 人天管理

| 功能 | admin | pmo | member | viewer |
|------|-------|-----|--------|--------|
| 填报人天 | ✅ | ✅ | ✅ | ❌ |
| 查看所有人天 | ✅ | ✅ | ❌ | ❌ |
| 查看自己人天 | ✅ | ✅ | ✅ | ✅ |
| 编辑人天 | ✅ | ✅ | ✅* | ❌ |
| 删除人天 | ✅ | ✅ | ✅* | ❌ |

*member 只能编辑自己填报的人天

---

### 6. 周报管理

| 功能 | admin | pmo | member | viewer |
|------|-------|-----|--------|--------|
| 填写周报 | ✅ | ✅ | ✅ | ❌ |
| 查看所有周报 | ✅ | ✅ | ✅* | ✅* |
| 编辑周报 | ✅ | ✅ | ✅* | ❌ |
| 删除周报 | ✅ | ✅ | ✅* | ❌ |

*member 只能查看/编辑自己填写的周报

---

### 7. 报告生成

| 功能 | admin | pmo | member | viewer |
|------|-------|-----|--------|--------|
| 生成项目周报 | ✅ | ✅ | ✅* | ❌ |
| 生成项目月报 | ✅ | ✅ | ✅* | ❌ |
| 生成问题风险台账 | ✅ | ✅ | ✅* | ❌ |
| 生成人天统计 | ✅ | ✅ | ✅* | ❌ |
| 生成项目组合报告 | ✅ | ✅ | ❌ | ❌ |

*member 只能生成自己参与项目的报告

---

### 8. 系统配置

| 功能 | admin | pmo | member | viewer |
|------|-------|-----|--------|--------|
| 管理系统字典 | ✅ | ❌ | ❌ | ❌ |
| 查看系统配置 | ✅ | ❌ | ❌ | ❌ |

---

## 权限实现细节

### 认证流程

```python
# backend/app/core/security.py
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 权限检查装饰器

```python
# backend/app/api/v1/projects.py
def _can_manage(project: Project, current_user: User) -> bool:
    """判断当前用户是否有权限管理该项目"""
    if current_user.role in ("admin", "pmo"):
        return True
    # member 只能管理自己创建的项目
    return project.created_by == current_user.id
```

### 数据过滤

```python
# backend/app/api/v1/projects.py
@router.get("/", response_model=List[ProjectSummary])
def list_projects(...):
    query = db.query(Project)
    
    # 角色权限过滤：member 只能看自己的
    if current_user.role not in ("admin", "pmo"):
        query = query.filter(
            (Project.created_by == current_user.id) | 
            (Project.created_by.is_(None))
        )
    
    projects = query.all()
    return [_build_summary(p, db) for p in projects]
```

---

## 默认账号

### 初始管理员

系统初始化时会创建默认管理员账号：

| 字段 | 值 |
|------|-----|
| **用户名** | admin |
| **密码** | admin123 |
| **角色** | admin |
| **全名** | 系统管理员 |
| **邮箱** | admin@pmo.local |

**重要**: 首次登录后应立即修改默认密码！

---

## 角色使用场景

### admin（系统管理员）

**典型用户**: IT 部门技术人员

**主要职责**:
- 系统维护和配置
- 用户账号管理
- 数据备份和恢复
- 系统监控

**典型操作**:
```
1. 创建新用户账号
2. 分配用户角色
3. 启用/停用账号
4. 管理系统字典
5. 查看所有数据
```

---

### pmo（PMO 管理员）

**典型用户**: PMO 办公室成员

**主要职责**:
- 项目组合管理
- 项目监控
- 报告生成
- 资源协调

**典型操作**:
```
1. 查看所有项目状态
2. 生成项目组合报告
3. 监控项目风险
4. 协调项目资源
5. 创建新项目
```

---

### member（项目成员）

**典型用户**: 项目经理、项目顾问

**主要职责**:
- 项目执行
- 任务管理
- 进度填报
- 问题反馈

**典型操作**:
```
1. 创建自己负责的项目
2. 管理项目里程碑
3. 分配和更新任务
4. 填报人天和周报
5. 登记问题和风险
```

---

### viewer（只读用户）

**典型用户**: 高层管理者、审计人员

**主要职责**:
- 查看项目状态
- 审阅报告
- 了解项目进展

**典型操作**:
```
1. 查看项目列表
2. 查看项目详情
3. 查看项目报告
4. 导出只读数据
```

---

## 权限扩展

### 添加新权限

如需添加新的权限控制，遵循以下步骤：

1. **定义权限检查函数**:
```python
def can_view_report(project: Project, current_user: User) -> bool:
    if current_user.role in ("admin", "pmo"):
        return True
    return project.created_by == current_user.id
```

2. **在 API 中使用**:
```python
@router.get("/reports/{project_id}")
def get_report(project_id: int, ...):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404)
    
    if not can_view_report(project, current_user):
        raise HTTPException(status_code=403, detail="无权查看此报告")
    
    # ... 生成报告
```

---

## 安全最佳实践

### 1. 最小权限原则

- 用户只应拥有完成工作所需的最小权限
- 默认角色应为 `member` 或 `viewer`
- `admin` 角色应严格限制

### 2. 定期审查

- 定期审查用户角色分配
- 清理离职用户账号
- 调整岗位变动用户的权限

### 3. 密码策略

- 首次登录后立即修改默认密码
- 使用强密码（8 位以上，包含大小写、数字、特殊字符）
- 定期更换密码

### 4. 审计日志

- 记录所有敏感操作
- 定期审计权限使用情况
- 监控异常访问

---

## 常见问题

### Q1: member 角色能看到其他成员的项目吗？

**A**: 不能。member 角色只能看到：
- 自己创建的项目
- `created_by` 为空的项目（公共项目）

### Q2: pmo 和 admin 的区别是什么？

**A**: 主要区别在用户管理：
- `admin` 可以管理用户（创建/编辑/删除）
- `pmo` 不能管理用户，但可以管理所有项目

### Q3: 如何给 member 分配更多权限？

**A**: 有两种方式：
1. 将用户角色改为 `pmo`（推荐）
2. 将项目 `created_by` 设为该用户

### Q4: viewer 角色有什么实际用途？

**A**: viewer 适合：
- 高层领导查看项目进展
- 审计人员检查项目合规性
- 外部顾问了解项目情况

---

## 相关文档

- [用户手册](../MANUAL.md)
- [功能列表](../FEATURES.md)
- [API 文档](../API.md)
- [数据库初始化](runbooks/database-init.md)
