# Runbook: 数据库初始化

## 概述

PMO 系统提供两套数据库初始化方案：
- **SQLite** - 开发环境使用
- **PostgreSQL** - 生产环境使用

## 脚本清单

### 1. 核心初始化脚本

| 脚本名称 | 用途 | 适用环境 | 执行顺序 |
|---------|------|---------|---------|
| `init_data.py` | 创建基础数据（表结构+admin 用户 + 系统字典） | SQLite/PostgreSQL | 1️⃣ |
| `seed_data.py` | 创建测试数据（测试项目/用户/问题/风险等） | SQLite/PostgreSQL | 2️⃣ |

### 2. 数据迁移脚本

| 脚本名称 | 用途 | 适用场景 |
|---------|------|---------|
| `migrate_to_dict_codes.py` | 将中文值转换为字典代码 | 旧数据规范化 |
| `migrate_issues_risks.py` | 迁移问题和风险数据格式 | 数据格式统一 |
| `migrations/20250305_risk_level_dict.sql` | 风险等级字典化 | PostgreSQL |

### 3. Alembic 迁移

| 文件 | 用途 |
|------|------|
| `alembic/versions/add_weekly_progress.py` | 添加周报进展表 |

---

## 快速开始

### 开发环境（SQLite）

```bash
cd backend
source venv/bin/activate

# 1. 初始化基础数据
python init_data.py

# 2. （可选）创建测试数据
python seed_data.py
```

### 生产环境（PostgreSQL）

```bash
cd backend
source venv/bin/activate

# 1. 确保 PostgreSQL 已安装并运行
sudo systemctl start postgresql

# 2. 创建数据库和用户
sudo -u postgres psql <<EOF
CREATE DATABASE pmo_db;
CREATE USER pmo_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE pmo_db TO pmo_user;
\q
EOF

# 3. 配置 .env 文件
cat > .env <<EOF
DATABASE_URL=postgresql://pmo_user:your_secure_password@localhost/pmo_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EOF

# 4. 初始化基础数据
python init_data.py

# 5. （可选）创建测试数据
python seed_data.py
```

---

## 脚本详解

### init_data.py

**功能**:
1. ✅ 创建所有数据库表（如果不存在）
2. ✅ 创建 admin 用户（密码：admin123）
3. ✅ 写入系统字典（项目状态/阶段/问题/风险等枚举值）

**特点**:
- 可重复执行，不会清空已有数据
- 已存在的数据会跳过

**执行示例**:
```bash
$ python init_data.py
✅ 数据库表已创建
✅ admin 用户已创建 (admin/admin123)
✅ 系统字典已写入 (52 条记录)
```

### seed_data.py

**功能**:
1. ✅ 创建测试用户（4 个不同角色）
2. ✅ 创建测试项目（3 个不同状态）
3. ✅ 创建里程碑和任务
4. ✅ 创建问题和风险记录
5. ✅ 创建人天记录

**特点**:
- 会清空已有测试数据（保留 admin 用户）
- 用于快速搭建演示环境

**执行示例**:
```bash
$ python seed_data.py
✅ 已清空旧数据（admin 用户保留）
✅ 已创建 4 个测试用户
✅ 已创建 3 个测试项目
✅ 已创建 10 个里程碑
✅ 已创建 24 个任务
✅ 已创建 8 个问题
✅ 已创建 6 个风险
✅ 已创建 24 条人天记录
```

---

## 数据迁移

### 场景 1: 旧数据规范化

如果系统中有使用中文值的历史数据，执行：

```bash
python migrate_to_dict_codes.py
```

**迁移内容**:
- 项目阶段：启动 → ph_kickoff
- 项目状态：正常 → st_normal
- 里程碑状态：未开始 → ms_notstart
- 问题严重等级：高 → isev_h
- 风险概率：高 → rp_h
- 等等...

### 场景 2: 风险等级字典化

执行 SQL 迁移脚本：

```bash
sudo -u postgres psql -d pmo_db -f migrations/20250305_risk_level_dict.sql
```

---

## 验证

### 检查数据库表

```bash
# SQLite
sqlite3 data/pmo.db ".tables"

# PostgreSQL
psql -U pmo_user -d pmo_db -c "\dt"
```

### 检查系统字典

```bash
# SQLite
sqlite3 data/pmo.db "SELECT category, COUNT(*) FROM sys_dicts GROUP BY category;"

# PostgreSQL
psql -U pmo_user -d pmo_db -c "SELECT category, COUNT(*) FROM sys_dicts GROUP BY category;"
```

### 检查 admin 用户

```bash
# SQLite
sqlite3 data/pmo.db "SELECT id, username, role FROM users WHERE username='admin';"

# PostgreSQL
psql -U pmo_user -d pmo_db -c "SELECT id, username, role FROM users WHERE username='admin';"
```

---

## 常见问题

### 问题 1: 表已存在错误

**症状**:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) table 'projects' already exists
```

**解决**:
- 这是正常现象，`init_data.py` 使用 `CREATE TABLE IF NOT EXISTS`
- 如果确实需要重新建表，先删除数据库文件：
  ```bash
  rm data/pmo.db
  python init_data.py
  ```

### 问题 2: PostgreSQL 连接失败

**症状**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server failed
```

**解决**:
```bash
# 检查 PostgreSQL 服务
sudo systemctl status postgresql

# 检查数据库用户
sudo -u postgres psql -c "\du"

# 检查数据库
sudo -u postgres psql -c "\l"
```

### 问题 3: 主键序列错误（PostgreSQL）

**症状**:
```
(psycopg2.errors.NotNullViolation) null value in column "id" of relation "projects" violates not-null constraint
```

**解决**:
```sql
-- 为每个表创建序列
CREATE SEQUENCE IF NOT EXISTS projects_id_seq;
ALTER TABLE projects ALTER COLUMN id SET DEFAULT nextval('projects_id_seq');
SELECT setval('projects_id_seq', COALESCE((SELECT MAX(id) FROM projects), 0) + 1, false);
GRANT USAGE, SELECT, UPDATE ON SEQUENCE projects_id_seq TO pmo_user;

-- 重复以上步骤为其他表创建序列：
-- weekly_progress, issues, mandays, milestones, risks, tasks, users, sys_dicts
```

---

## 备份策略

### SQLite 备份

```bash
# 备份
cp data/pmo.db data/pmo.db.backup.$(date +%Y%m%d_%H%M)

# 恢复
cp data/pmo.db.backup.20260310_1200 data/pmo.db
```

### PostgreSQL 备份

```bash
# 备份
pg_dump -U pmo_user pmo_db > backups/pmo_db.$(date +%Y%m%d_%H%M).sql

# 恢复
psql -U pmo_user pmo_db < backups/pmo_db.20260310_1200.sql
```

---

## 最佳实践

### 开发环境
1. 使用 SQLite，零配置
2. 执行 `init_data.py` 创建基础数据
3. 执行 `seed_data.py` 创建测试数据
4. 随时可以删除重建

### 生产环境
1. 使用 PostgreSQL，支持高并发
2. 只执行 `init_data.py`，不执行 `seed_data.py`
3. 定期备份数据库
4. 迁移前务必备份

### 数据迁移
1. 迁移前备份数据库
2. 在测试环境验证迁移脚本
3. 生产环境执行迁移
4. 验证数据完整性

---

## 相关文档

- [本地开发指南](./local-dev.md)
- [生产部署指南](./deploy.md)
- [架构概览](../architecture/overview.md)
- [数据库迁移决策](../decisions/002-database-migration.md)
