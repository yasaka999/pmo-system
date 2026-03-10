# PMO 项目成员关联机制

## 概述

PMO 系统中，项目与创建者（成员）之间通过 `created_by` 字段建立关联。这种设计实现了项目的所有权管理和权限控制。

---

## 数据模型

### Project 表结构

```python
# backend/app/models/project.py
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    # ... 其他字段 ...
    
    # 关键关联字段
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者用户 ID")
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系定义
    creator = relationship("User", foreign_keys=[created_by])
```

### 关联关系

```
User (用户表)
  │
  │ 1:N
  ↓
Project (项目表)
  │
  └─ created_by → User.id
```

---

## 关联建立流程

### 1. 成员创建项目

**API 端点**: `POST /api/v1/projects/`

**代码逻辑**:
```python
# backend/app/api/v1/projects.py
@router.post("/", response_model=ProjectOut)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 获取当前登录用户
):
    # 检查项目编号是否已存在
    if db.query(Project).filter(Project.code == project_in.code).first():
        raise HTTPException(status_code=400, detail="项目编号已存在")
    
    # 关键：自动设置 created_by 为当前用户 ID
    project = Project(**project_in.model_dump(), created_by=current_user.id)
    
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
```

**流程说明**:
1. 用户登录系统，获得 JWT Token
2. 前端携带 Token 发起创建项目请求
3. 后端通过 `get_current_user` 解析 Token，获取当前用户信息
4. 创建项目时，自动将 `current_user.id` 赋值给 `created_by` 字段
5. 项目保存到数据库，关联关系建立完成

---

### 2. 查看关联关系

**查询项目时查看创建者**:
```python
# 获取项目详情
project = db.query(Project).filter(Project.id == 1).first()

# 访问创建者信息
creator = project.creator  # User 对象
print(f"创建者：{creator.username}")
print(f"创建时间：{project.created_at}")
```

**SQL 查询**:
```sql
-- 查询项目及其创建者
SELECT 
    p.id,
    p.code,
    p.name,
    p.created_by,
    u.username as creator_name,
    p.created_at
FROM projects p
LEFT JOIN users u ON p.created_by = u.id
WHERE p.id = 1;
```

---

## 权限控制逻辑

### 1. 项目访问权限

**代码实现**:
```python
# backend/app/api/v1/projects.py
@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # member 只能查看自己创建的项目
    if current_user.role not in ("admin", "pmo"):
        if project.created_by is not None and project.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问该项目")
    
    return project
```

**权限矩阵**:

| 用户角色 | 能访问的项目 |
|---------|------------|
| **admin** | 所有项目 |
| **pmo** | 所有项目 |
| **member** | 自己创建的项目（`created_by == current_user.id`） |
| **viewer** | 自己创建的项目 |

---

### 2. 项目列表查询

**代码实现**:
```python
@router.get("/", response_model=List[ProjectSummary])
def list_projects(
    statuses: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Project)
    
    # 角色权限过滤：member 只能看自己的
    if current_user.role not in ("admin", "pmo"):
        query = query.filter(
            (Project.created_by == current_user.id) | 
            (Project.created_by.is_(None))  # 允许查看公共项目
        )
    
    # ... 其他筛选条件 ...
    
    projects = query.all()
    return [_build_summary(p, db) for p in projects]
```

**查询示例**:

**admin/pmo 用户**:
```sql
-- 查看所有项目
SELECT * FROM projects;
```

**member 用户**（假设 user_id = 5）:
```sql
-- 只能查看自己创建的项目或公共项目
SELECT * FROM projects 
WHERE created_by = 5 OR created_by IS NULL;
```

---

### 3. 项目管理权限

**代码实现**:
```python
def _can_manage(project: Project, current_user: User) -> bool:
    """判断当前用户是否有权限管理该项目（编辑/删除）"""
    if current_user.role in ("admin", "pmo"):
        return True
    # member 只能管理自己创建的项目
    return project.created_by == current_user.id


@router.put("/{project_id}")
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404)
    
    # 检查权限
    if not _can_manage(project, current_user):
        raise HTTPException(status_code=403, detail="无权编辑该项目")
    
    # ... 更新逻辑 ...
```

---

## 特殊场景

### 1. 公共项目（created_by IS NULL）

**场景**: 某些项目不属于特定成员，而是公共项目

**查询逻辑**:
```python
# member 可以查看公共项目
query = query.filter(
    (Project.created_by == current_user.id) | 
    (Project.created_by.is_(None))
)
```

**数据库状态**:
```sql
INSERT INTO projects (code, name, created_by) 
VALUES ('PUBLIC001', '公共项目', NULL);
```

---

### 2. 转移项目所有权

**场景**: 成员离职，需要将其项目转移给其他成员

**实现方法**:
```python
# 更新项目的 created_by 字段
project = db.query(Project).filter(Project.id == project_id).first()
project.created_by = new_owner_id  # 新负责人 ID
db.commit()
```

**SQL 方式**:
```sql
UPDATE projects 
SET created_by = 10  -- 新负责人 ID
WHERE id = 1;
```

---

### 3. 团队成员参与项目

**场景**: 多个成员参与同一个项目，但只有一个人是创建者

**解决方案**: 使用项目成员表（待实现）

```python
# 建议的项目成员表结构
class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String(50))  # 项目经理/成员/观察员
    joined_at = Column(DateTime, server_default=func.now())
    
    project = relationship("Project", back_populates="members")
    user = relationship("User")
```

**查询项目所有成员**:
```python
members = db.query(ProjectMember).filter(
    ProjectMember.project_id == project_id
).all()
```

---

## 实际案例

### 案例 1: 成员创建项目

**用户信息**:
- 用户名：`zhangsan`
- 用户 ID: `5`
- 角色：`member`

**创建项目**:
```bash
POST /api/v1/projects/
Authorization: Bearer <JWT_TOKEN>

{
  "code": "P2026001",
  "name": "测试项目",
  "manager": "张三"
}
```

**数据库记录**:
```sql
INSERT INTO projects (
    code, name, manager, created_by, created_at
) VALUES (
    'P2026001', '测试项目', '张三', 5, NOW()
);
```

**查询结果**:
```sql
SELECT id, code, name, created_by FROM projects WHERE created_by = 5;

-- 结果:
-- id | code     | name     | created_by
-- 1  | P2026001 | 测试项目 | 5
```

---

### 案例 2: 成员查看项目列表

**场景**: `zhangsan` (user_id=5) 登录系统后查看项目列表

**API 请求**:
```bash
GET /api/v1/projects/
Authorization: Bearer <JWT_TOKEN>
```

**后端处理**:
```python
# 检测到 current_user.role = "member"
# 自动添加权限过滤
query = db.query(Project).filter(
    (Project.created_by == 5) |  # 自己创建的项目
    (Project.created_by.is_(None))  # 或公共项目
)
```

**返回结果**:
```json
[
  {
    "id": 1,
    "code": "P2026001",
    "name": "测试项目",
    "created_by": 5,
    "creator_name": "zhangsan"
  }
]
```

---

### 案例 3: 越权访问被拒绝

**场景**: `lisi` (user_id=6) 尝试访问 `zhangsan` 创建的项目

**API 请求**:
```bash
GET /api/v1/projects/1
Authorization: Bearer <lisi_token>
```

**后端处理**:
```python
project = db.query(Project).filter(Project.id == 1).first()
# project.created_by = 5 (zhangsan)
# current_user.id = 6 (lisi)

if current_user.role not in ("admin", "pmo"):
    if project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该项目")
```

**返回结果**:
```json
{
  "detail": "无权访问该项目"
}
```

---

## 最佳实践

### 1. 创建项目时

✅ **推荐**:
- 始终由具体负责人创建项目
- 确保 `created_by` 字段正确设置
- 项目描述中明确团队角色

❌ **避免**:
- 使用 admin 账号代创建项目（会导致权限混乱）
- 创建项目后不设置负责人

---

### 2. 权限管理

✅ **推荐**:
- member 角色只创建自己负责的项目
- 需要多人管理时使用 pmo 角色
- 定期审查项目所有权

❌ **避免**:
- 随意将 member 提升为 pmo
- 项目创建后不管理权限

---

### 3. 人员变动处理

✅ **推荐**:
- 成员离职前转移项目所有权
- 使用 SQL 批量更新项目负责人
- 记录所有权变更历史

```sql
-- 批量转移离职员工的项目
UPDATE projects 
SET created_by = 10  -- 新负责人 ID
WHERE created_by = 5;  -- 离职员工 ID
```

---

## 常见问题

### Q1: member 能看到其他成员的项目吗？

**A**: 不能。member 角色只能看到：
- 自己创建的项目（`created_by == current_user.id`）
- 公共项目（`created_by IS NULL`）

---

### Q2: 如何查看某个成员创建的所有项目？

**A**: 使用 admin/pmo 账号查询：

```python
# admin/pmo 可以查看所有项目
projects = db.query(Project).filter(
    Project.created_by == user_id
).all()
```

---

### Q3: 项目创建后能修改 created_by 吗？

**A**: 可以，但需要 admin 权限：

```python
# 需要 admin 权限才能执行
project = db.query(Project).filter(Project.id == project_id).first()
project.created_by = new_user_id
db.commit()
```

---

### Q4: created_by 为 NULL 的项目谁都能看吗？

**A**: 是的。`created_by IS NULL` 表示公共项目：
- admin/pmo: 可以查看和编辑
- member/viewer: 可以查看，但不能编辑（除非是创建者）

---

### Q5: 一个项目能有多个创建者吗？

**A**: 不能。`created_by` 是单值字段，只能指向一个用户。

**解决方案**: 使用项目成员表（见上文"团队成员参与项目"部分）

---

## 相关文档

- [权限管理文档](./PERMISSIONS.md)
- [用户手册](../MANUAL.md)
- [API 文档](../API.md)
