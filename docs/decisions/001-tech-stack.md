# ADR-001: 技术栈选择

## 状态
✅ Accepted

## 日期
2026-03-09

## 背景
需要为 PMO 项目管理系统选择合适的技术栈，满足以下要求：
- 快速开发和部署
- 易于维护和扩展
- 性能良好
- 团队熟悉度高

## 决策

### 后端技术栈
**决定**: Python + FastAPI

**理由**:
1. **开发效率高** - Python 语法简洁，FastAPI 自动生成交互式文档
2. **性能优秀** - 基于 Starlette 和 Pydantic，性能接近 Node.js
3. **类型安全** - Pydantic 提供数据验证和类型检查
4. **生态丰富** - SQLAlchemy、Alembic 等成熟库
5. **团队熟悉** - 团队有 Python 开发经验

**备选方案**:
- Node.js + Express - 考虑过，但团队更熟悉 Python
- Java + Spring Boot - 过于重量级，开发周期长
- Go + Gin - 性能好，但生态不如 Python 丰富

### 前端技术栈
**决定**: Vue 3 + Vite + Element Plus

**理由**:
1. **学习曲线低** - Vue 3 易于上手，文档完善
2. **开发体验好** - Vite 热更新快速，开发效率高
3. **组件丰富** - Element Plus 提供完整的企业级组件
4. **性能优秀** - Vue 3 组合式 API，性能优于 Vue 2
5. **状态管理** - Pinia 轻量级状态管理

**备选方案**:
- React + Ant Design - 考虑过，但 Vue 学习曲线更低
- Angular - 过于重量级
- Svelte - 生态不够成熟

### 数据库
**决定**: PostgreSQL (生产) + SQLite (开发)

**理由**:
1. **PostgreSQL** - 功能强大，支持高并发，ACID 事务
2. **SQLite** - 开发环境零配置，便于快速启动
3. **SQLAlchemy** - ORM 抽象，切换数据库成本低

**备选方案**:
- MySQL - 考虑过，但 PostgreSQL 功能更强大
- MongoDB - 不适合关系型数据
- Redis - 仅作缓存，不适合作为主数据库

### 认证方案
**决定**: JWT (JSON Web Tokens)

**理由**:
1. **无状态** - 服务端不存储 session，易于扩展
2. **跨域支持** - 天然支持 CORS
3. **标准化** - RFC 7519 标准
4. **灵活性** - 可自定义 payload

**备选方案**:
- Session + Cookie - 需要考虑 CSRF，跨域复杂
- OAuth2 - 过于复杂，不适合内部系统

## 结果

### 正面影响
- ✅ 开发效率高，快速上线
- ✅ 代码质量好，类型安全
- ✅ 性能满足需求
- ✅ 团队上手快

### 负面影响
- ⚠️ Python GIL 限制并发性能（通过多进程解决）
- ⚠️ SQLite 不支持高并发（生产环境使用 PostgreSQL）

### 经验教训
- 选择团队熟悉的技术栈比追求新技术更重要
- 前后端分离架构便于独立开发和部署
- ORM 抽象为数据库切换提供便利

## 相关文档
- [架构概览](../architecture/overview.md)
- [部署指南](../runbooks/deploy.md)
