# PMO 系统更新日志 - 2026 年 3 月 10 日

## 新增功能

### 1. 项目负责人重新分配功能

**功能描述**: 允许 admin 和 pmo 用户重新分配项目的负责人

**访问路径**: 系统配置 → 项目负责人分配

**权限控制**:
- 查看权限：admin, pmo
- 操作权限：admin, pmo

**API 端点**:
- `GET /api/v1/admin/project-owners` - 获取项目列表及负责人
- `GET /api/v1/admin/users` - 获取用户列表
- `PUT /api/v1/admin/project/{id}/owner` - 重新分配负责人

**相关文件**:
- `backend/app/api/v1/admin.py` - 后端 API
- `frontend/src/views/AdminProjectOwner.vue` - 前端页面
- `frontend/src/api/index.js` - API 客户端

---

## Bug 修复

### 1. 项目负责人分配页面加载失败

**问题**: 点击"项目负责人分配"菜单后报错"加载项目列表失败"

**原因**: 
- 前端 API 定义中 `admin` 对象被错误地嵌套在 `reportApi` 里面
- 组件调用 `api.admin.getProjectOwners()` 时找不到该方法

**修复**:
- 将 `adminApi` 独立导出并挂载到 `api.admin` 上
- 修正 `reassignOwner` 的请求体格式

**文件**: `frontend/src/api/index.js`

---

### 2. 后端 API 路由 404 错误

**问题**: 访问 `/api/v1/admin/project-owners` 返回 404

**原因**: 
- `router.py` 中 admin 路由的 prefix 设置为 `/admin`
- `admin.py` 中的路由路径也包含了 `/admin`
- 导致实际路径变成 `/admin/admin/project-owners`

**修复**:
- 将 router.py 中 admin 路由的 prefix 从 `"/admin"` 改为 `""`

**文件**: `backend/app/api/router.py`

---

### 3. 前端菜单变量名混用

**问题**: 菜单显示错误 `Cannot read properties of undefined (reading 'user')`

**原因**: 模板中混用了 `auth.user` 和 `authStore.user` 两个变量名

**修复**: 统一使用 `auth.user`

**文件**: `frontend/src/layouts/MainLayout.vue`

---

### 4. 后端模块导入失败

**问题**: 后端启动时报 `ImportError: cannot import name 'admin'`

**原因**: `app/api/v1/__init__.py` 未导出 admin 模块

**修复**: 添加 admin 模块导入

**文件**: `backend/app/api/v1/__init__.py`

---

## 技术改进

### 1. 代码结构优化

- 将管理员专用 API 独立为 `admin.py` 模块
- 前端 API 客户端按功能模块组织
- 统一变量命名规范

### 2. 权限控制增强

- 所有 admin API 都增加了角色验证
- 仅 admin 和 pmo 角色可访问
- 返回友好的权限错误提示

---

## 验证结果

| API | 状态 | 返回数据 |
|-----|------|---------|
| `GET /api/v1/admin/project-owners` | ✅ 200 OK | 24 个项目 |
| `GET /api/v1/admin/users` | ✅ 200 OK | 6 个用户 |
| `PUT /api/v1/admin/project/{id}/owner` | ✅ 待测试 | - |

| 前端功能 | 状态 |
|---------|------|
| 菜单显示 | ✅ 正常 |
| 页面加载 | ✅ 正常 |
| 项目列表 | ✅ 正常 |
| 用户选择 | ✅ 正常 |
| 重新分配 | ✅ 待测试 |

---

## 部署步骤

1. **后端部署**:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt  # 如有新依赖
   ```

2. **前端部署**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

3. **重启服务**:
   ```bash
   # 后端
   pkill -f uvicorn
   cd backend && source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
   
   # Nginx 会自动处理前端静态文件
   ```

---

## 回滚方案

如需回滚，使用以下 Git 命令：
```bash
git reset --hard <previous-commit>
git push -f origin master
```

---

## 相关文档

- [项目负责人分配功能说明](./PROJECT-ASSIGNMENT.md)
- [权限管理文档](./PERMISSIONS.md)
- [API 文档](../API.md)

---

**更新时间**: 2026-03-10 12:28 UTC  
**更新人员**: xhan  
**Git 提交**: 577c339
