# PMO 系统部署指南

## 环境要求

### 服务器配置

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 1 核 | 2 核+ |
| 内存 | 1 GB | 2 GB+ |
| 磁盘 | 10 GB | 20 GB+ |
| 操作系统 | CentOS 7+ / Ubuntu 18.04+ | CentOS 8 / Ubuntu 22.04 |

### 软件依赖

| 软件 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 后端运行环境 |
| Node.js | 18+ | 前端构建工具 |
| Nginx | 1.18+ | 反向代理 & 静态文件服务 |
| SQLite | 3.x | 数据库 |
| Git | 2.x+ | 代码管理 |

---

## 部署架构

```
┌─────────────────────────────────────────┐
│              用户浏览器                   │
└─────────────────┬───────────────────────┘
                  │ HTTPS (建议)
┌─────────────────▼───────────────────────┐
│              Nginx                      │
│  ├─ 端口 9000 → 前端静态文件 (dist)      │
│  └─ 端口 8000 → FastAPI 后端 (反向代理)   │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌────▼────┐   ┌────▼────┐
│ 前端   │   │  后端    │   │ 数据库   │
│(静态)  │   │ FastAPI │   │ SQLite  │
└───────┘   └────┬────┘   └────┬────┘
                 │             │
            ┌────▼─────────────▼────┐
            │    pmo.db (数据文件)   │
            └─────────────────────────┘
```

---

## 方式一：手动部署（生产环境）

### 1. 服务器准备

```bash
# 登录服务器
ssh -p 2022 root@142.171.178.36

# 安装基础依赖
yum update -y                    # CentOS
apt update && apt upgrade -y     # Ubuntu

# 安装 Python 3.8+
yum install python3 python3-pip -y

# 安装 Nginx
yum install nginx -y
systemctl enable nginx
systemctl start nginx

# 安装 Node.js 18+
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
yum install nodejs -y
```

### 2. 部署后端

```bash
# 创建应用目录
mkdir -p /opt/pmo-system-new
cd /opt/pmo-system-new

# 克隆代码（或上传代码）
git clone https://github.com/yasaka999/python.git temp
cp -r temp/pmo-system/* .
rm -rf temp

# 进入后端目录
cd backend

# 安装依赖
pip3 install -r requirements.txt

# 初始化数据库（首次部署必须执行！）
python3 init_data.py

# 启动服务（使用 nohup 后台运行）
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/pmo.log 2>&1 &

# 检查服务状态
ps aux | grep uvicorn
curl http://localhost:8000/api/v1/projects/
```

### 3. 部署前端

**注意：** 如果服务器 Node.js 版本较旧，建议在本地构建后上传。

#### 方案 A：本地构建后上传（推荐）

```bash
# 在本地开发机执行
cd /path/to/pmo-system/frontend
npm install
npm run build

# 上传到服务器
rsync -avz --delete -e "ssh -p 2022" dist/ root@142.171.178.36:/opt/pmo-system-new/frontend/dist/
```

#### 方案 B：服务器上构建（需要 Node.js 18+）

```bash
# 在服务器执行
cd /opt/pmo-system-new/frontend
npm install
npm run build
```

### 4. 配置 Nginx

```bash
# 编辑 Nginx 配置
vim /etc/nginx/conf.d/pmo.conf
```

添加以下内容：

```nginx
# 前端服务（端口 9000）
server {
    listen 9000;
    server_name _;
    
    location / {
        root /opt/pmo-system-new/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# 后端 API（端口 8000，反向代理到 Uvicorn）
server {
    listen 8000;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 测试配置并重启 Nginx
nginx -t
systemctl restart nginx
```

### 5. 验证部署

```bash
# 测试后端 API
curl http://142.171.178.36:8000/api/v1/projects/

# 浏览器访问
http://142.171.178.36:9000
```

---

## 方式二：Docker 部署（可选）

### Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/pmo.db
    restart: unless-stopped

  frontend:
    image: nginx:alpine
    ports:
      - "9000:80"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend
    restart: unless-stopped
```

---

## 日常运维

### 查看服务状态

```bash
# 查看后端进程
ps aux | grep uvicorn

# 查看后端日志
tail -f /tmp/pmo.log

# 查看 Nginx 状态
systemctl status nginx

# 查看 Nginx 访问日志
tail -f /var/log/nginx/access.log
```

### 重启服务

```bash
# 重启后端
pkill -f uvicorn
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/pmo.log 2>&1 &

# 重启 Nginx
systemctl restart nginx
```

### 数据库备份

```bash
# 手动备份
cp /opt/pmo-system-new/backend/pmo.db /backup/pmo_$(date +%Y%m%d).db

# 自动备份（添加到 crontab）
0 2 * * * cp /opt/pmo-system-new/backend/pmo.db /backup/pmo_$(date +\%Y\%m\%d).db
```

### 更新部署

```bash
# 1. 拉取最新代码
cd /opt/pmo-system-new
git pull origin master

# 2. 如果有新的依赖
cd backend
pip3 install -r requirements.txt

# 3. 重启后端
pkill -f uvicorn
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/pmo.log 2>&1 &

# 4. 重新构建前端（如果在服务器构建）
cd ../frontend
npm install
npm run build

# 或者从本地上传新的 dist 目录
```

---

## 故障排查

### 问题 1：后端无法启动

**现象:** `uvicorn` 命令报错

**排查:**
```bash
# 检查 Python 版本
python3 --version

# 检查依赖是否安装
pip3 list | grep fastapi

# 查看详细错误
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 问题 2：前端页面空白

**现象:** 访问 9000 端口显示空白页

**排查:**
```bash
# 检查 dist 目录是否存在
ls -la /opt/pmo-system-new/frontend/dist/

# 检查 index.html 是否存在
cat /opt/pmo-system-new/frontend/dist/index.html

# 检查 Nginx 配置
cat /etc/nginx/conf.d/pmo.conf

# 检查 Nginx 错误日志
tail -f /var/log/nginx/error.log
```

### 问题 3：API 请求 404

**现象:** 前端提示 API 接口不存在

**排查:**
```bash
# 测试后端是否运行
curl http://localhost:8000/api/v1/projects/

# 检查 Nginx 反向代理配置
# 确保 proxy_pass 指向正确的后端地址
```

### 问题 4：数据库锁定

**现象:** SQLite database is locked

**解决:**
```bash
# 检查是否有多个进程访问数据库
lsof /opt/pmo-system-new/backend/pmo.db

# 重启后端服务
pkill -f uvicorn
sleep 2
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/pmo.log 2>&1 &
```

---

## 安全配置

### 1. 配置防火墙

```bash
# 开放必要端口
firewall-cmd --permanent --add-port=9000/tcp
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload
```

### 2. 配置 HTTPS（推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
yum install certbot python3-certbot-nginx -y

# 申请证书
certbot --nginx -d your-domain.com

# 自动续期测试
certbot renew --dry-run
```

### 3. 修改默认密码

首次登录后务必修改默认账户密码：
- admin / admin123
- pmo_zhang / pmo123

---

## 性能优化

### 1. 启用 Gzip 压缩

```nginx
# 在 nginx.conf 中添加
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

### 2. 配置进程数

```bash
# 根据 CPU 核心数调整 Uvicorn worker 数量
# 公式：2 * CPU核心数 + 1
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 3 > /tmp/pmo.log 2>&1 &
```

### 3. 数据库优化

```bash
# 定期清理旧数据（可选）
# 在 SQLite 中执行 VACUUM 优化存储
sqlite3 pmo.db "VACUUM;"
```

---

## 监控告警

### 简单健康检查脚本

```bash
#!/bin/bash
# /opt/monitor.sh

# 检查后端
if ! curl -sf http://localhost:8000/api/v1/projects/ > /dev/null; then
    echo "Backend is down! Restarting..."
    pkill -f uvicorn
    cd /opt/pmo-system-new/backend
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/pmo.log 2>&1 &
fi

# 检查 Nginx
if ! systemctl is-active --quiet nginx; then
    echo "Nginx is down! Restarting..."
    systemctl restart nginx
fi
```

添加到定时任务：
```bash
*/5 * * * * /opt/monitor.sh >> /var/log/pmo-monitor.log 2>&1
```

---

## 联系支持

如有部署问题，请检查：
1. 日志文件 `/tmp/pmo.log`
2. Nginx 错误日志 `/var/log/nginx/error.log`
3. 系统资源使用情况 `top` / `free -h` / `df -h`
