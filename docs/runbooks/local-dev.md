# Runbook: 本地开发环境搭建

## 前置条件

### 系统要求
- ✅ Python 3.12+
- ✅ Node.js 18+
- ✅ Git

### 检查命令
```bash
python --version    # 应该显示 Python 3.12.x
node --version      # 应该显示 v18.x.x 或更高
npm --version       # 应该显示 9.x.x 或更高
git --version       # 应该显示 git version 2.x.x
```

---

## 步骤

### 1. 克隆项目
```bash
cd /root/.openclaw/workspace/projects
git clone https://github.com/yasaka999/pmo-system.git
cd pmo-system
```

### 2. 后端环境搭建

#### 2.1 创建虚拟环境
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.3 配置数据库
```bash
# 开发环境使用 SQLite，无需额外配置
# 确保 .env 文件存在
cat .env
```

#### 2.4 启动后端服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**验证**: 访问 http://localhost:8000/docs 查看 API 文档

### 3. 前端环境搭建

#### 3.1 安装依赖
```bash
cd ../frontend
npm install
```

#### 3.2 启动开发服务器
```bash
npm run dev
```

**验证**: 访问 http://localhost:5173 查看前端

---

## 验证

### 后端检查清单
- [ ] API 文档可访问 (http://localhost:8000/docs)
- [ ] 健康检查通过 (http://localhost:8000/health)
- [ ] 数据库连接正常

### 前端检查清单
- [ ] 登录页面可访问
- [ ] 无控制台错误
- [ ] 可以正常登录

---

## 常见问题

### 问题 1: Python 版本不匹配
**症状**: `pip install` 报错

**解决**:
```bash
# 检查 Python 版本
python --version

# 如果版本不对，安装 Python 3.12
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv

# macOS
brew install python@3.12
```

### 问题 2: 端口被占用
**症状**: `Address already in use`

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8000
lsof -i :5173

# 杀死进程
kill -9 <PID>
```

### 问题 3: 前端依赖安装失败
**症状**: `npm install` 报错

**解决**:
```bash
# 清理缓存
npm cache clean --force

# 删除 node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 问题 4: 数据库连接失败
**症状**: 登录时报错，无法连接数据库

**解决**:
```bash
# 检查数据库文件是否存在
ls -la ../data/pmo.db

# 如果不存在，创建初始数据
cd backend
python init_data.py
```

---

## 开发工作流

### 1. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

### 2. 开发功能
- 后端修改 → 自动热重载
- 前端修改 → 自动热重载

### 3. 测试
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

### 4. 提交代码
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request
在 GitHub 上创建 PR，请求合并到 `master` 分支

---

## 调试技巧

### 后端调试
```python
# 使用 print 调试
print(f"Debug: {variable}")

# 使用 Python debugger
import pdb; pdb.set_trace()

# 查看日志
tail -f backend_log.txt
```

### 前端调试
```javascript
// 使用 console.log
console.log('Debug:', variable)

// 使用浏览器开发者工具
// F12 → Console → 查看日志
```

---

## 下一步

- [ ] 阅读 [架构文档](../architecture/overview.md)
- [ ] 了解 [产品功能](../../FEATURES.md)
- [ ] 查看 [用户手册](../../MANUAL.md)
- [ ] 学习 [部署指南](./deploy.md)

---

## 相关文档

- [部署指南](./deploy.md)
- [数据库管理](./database.md)
- [架构概览](../architecture/overview.md)
