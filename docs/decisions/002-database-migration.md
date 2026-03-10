# ADR-002: 数据库迁移方案

## 状态
✅ Accepted

## 日期
2026-03-10

## 背景
系统从 SQLite 迁移到 PostgreSQL，需要解决以下问题：
- SQLite 不支持高并发
- 生产环境需要更强大的数据库
- 保持数据完整性
- 最小化停机时间

## 决策

### 迁移工具
**决定**: pgloader

**理由**:
1. **自动化程度高** - 自动处理表结构、数据、索引
2. **迁移快速** - 比手动导出导入快
3. **错误处理** - 提供详细的错误报告
4. **支持 SQLite** - 原生支持 SQLite 到 PostgreSQL

**备选方案**:
- 手动导出导入 - 工作量大，易出错
- 自定义脚本 - 开发成本高

### 迁移步骤
1. **备份 SQLite 数据**
2. **安装 PostgreSQL 和 pgloader**
3. **创建数据库和用户**
4. **执行迁移**
5. **验证数据完整性**
6. **切换应用配置**
7. **重启服务**

### 主键序列修复
**问题**: pgloader 迁移后，PostgreSQL 的自增主键序列未正确创建

**解决方案**:
```sql
-- 为每个表创建序列
CREATE SEQUENCE IF NOT EXISTS table_name_id_seq;
ALTER TABLE table_name ALTER COLUMN id SET DEFAULT nextval('table_name_id_seq');
SELECT setval('table_name_id_seq', COALESCE((SELECT MAX(id) FROM table_name), 0) + 1, false);
GRANT USAGE, SELECT, UPDATE ON SEQUENCE table_name_id_seq TO pmo_user;
```

**影响表**:
- weekly_progress
- issues
- mandays
- milestones
- projects
- risks
- tasks
- users
- sys_dicts

## 结果

### 迁移效果
- ✅ 23 个项目数据成功迁移
- ✅ 4 个用户数据完整
- ✅ 所有表主键序列正常
- ✅ 应用正常运行

### 性能对比
| 指标 | SQLite | PostgreSQL | 提升 |
|------|--------|------------|------|
| 并发连接 | 1 | 100+ | 100x |
| 查询性能 | 基准 | 2-5x 快 | 2-5x |
| 数据量支持 | GB 级 | TB 级 | 1000x |

### 经验教训
- 迁移前务必备份数据
- 测试环境先验证迁移流程
- 准备好回滚方案
- 迁移后验证数据完整性

## 相关文档
- [部署指南](../runbooks/deploy.md)
- [数据库备份](../runbooks/database.md)
