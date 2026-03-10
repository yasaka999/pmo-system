# Runbook: 生产环境部署

## 前置条件

### 服务器要求
- ✅ Linux (Ubuntu 20.04+ 或 CentOS 7+)
- ✅ 2GB+ RAM
- ✅ 10GB+ 磁盘空间
- ✅ Python 3.12+
- ✅ Node.js 18+

### 软件要求
- ✅ PostgreSQL 14+
- ✅ Nginx (可选，用于反向代理)
- ✅ Git

---

## 步骤

### 1. 系统准备

#### 1.1 更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

#### 1.2 安装依赖
```bash
# Python
sudo apt install -y python3.12 python3.12-venv python3-pip

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Nginx (可选)
sudo apt install -y nginx
```

### 2. 数据库配置

#### 2.1 创建数据库
```bash
sudo -u postgres psql <<EOF
CREATE DATABASE pmo_db;
CREATE USER pmo_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE pmo_db TO pmo_user;
\q
EOF
```

#### 2.2 配置远程访问（可选）
```bash
# 编辑 PostgreSQL 配置
sudo nano /etc/postgresql/14/main/postgresql.conf
# 修改：listen_addresses = '*'

# 编辑 pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf
# 添加：host    pmo_db    pmo_user    0.0.0.0/0    md5

# 重启 PostgreSQL
sudo systemctl restart postgresql
```

### 3. 代码部署

#### 3.1 克隆项目
```bash
cd /var/www
sudo git clone https://github.com/yasaka999/pmo-system.git pmo-system
sudo chown -R $USER:$USER pmo-system
cd pmo-system
```

#### 3.2 部署后端

##### 创建虚拟环境
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

##### 安装依赖
```bash
pip install -r requirements.txt
pip install psycopg2-binary  # PostgreSQL 驱动
```

##### 配置文件
```bash
# 创建 .env 文件
cat > .env <<EOF
DATABASE_URL=postgresql://pmo_user:your_secure_password@localhost/pmo_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EOF
```

##### 创建 systemd 服务
```bash
sudo nano /etc/systemd/system/pmo-backend.service
```

内容：
```ini
[Unit]
Description=PMO Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/pmo-system/backend
Environment="PATH=/var/www/pmo-system/backend/venv/bin"
ExecStart=/var/www/pmo-system/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

##### 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable pmo-backend
sudo systemctl start pmo-backend
sudo systemctl status pmo-backend
```

#### 3.3 部署前端

##### 安装依赖
```bash
cd ../frontend
npm install
```

##### 构建生产版本
```bash
npm run build
```

##### 配置 Nginx
```bash
sudo nano /etc/nginx/sites-available/pmo-system
```

内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/pmo-system/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

##### 启用站点
```bash
sudo ln -s /etc/nginx/sites-available/pmo-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. 初始化数据

```bash
cd /var/www/pmo-system/backend
source venv/bin/activate
python init_data.py
```

---

## 验证

### 检查清单
- [ ] 后端服务运行正常
- [ ] 前端页面可访问
- [ ] 数据库连接正常
- [ ] 可以正常登录
- [ ] API 调用正常

### 验证命令
```bash
# 检查后端服务
sudo systemctl status pmo-backend

# 检查 Nginx
sudo systemctl status nginx

# 测试 API
curl http://localhost:8000/health

# 测试前端
curl http://localhost:80
```

---

## 常见问题

### 问题 1: 后端服务无法启动
**症状**: `systemctl status pmo-backend` 显示失败

**解决**:
```bash
# 查看日志
sudo journalctl -u pmo-backend -n 50

# 检查端口占用
lsof -i :8000

# 检查数据库连接
psql -h localhost -U pmo_user -d pmo_db
```

### 问题 2: 前端页面 404
**症状**: 访问页面显示 404

**解决**:
```bash
# 检查 Nginx 配置
sudo nginx -t

# 检查静态文件路径
ls -la /var/www/pmo-system/frontend/dist

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/error.log
```

### 问题 3: 数据库连接失败
**症状**: 登录时报数据库错误

**解决**:
```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 检查数据库用户
sudo -u postgres psql -c "\du"

# 检查数据库
sudo -u postgres psql -c "\l"
```

---

## 备份策略

### 数据库备份
```bash
# 创建备份脚本
cat > /var/www/pmo-system/backup.sh <<EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M)
pg_dump -U pmo_user pmo_db > /var/www/pmo-system/backups/pmo_db_\$DATE.sql
# 保留最近 7 天备份
find /var/www/pmo-system/backups -name "*.sql" -mtime +7 -delete
EOF

chmod +x /var/www/pmo-system/backup.sh
```

### 定时备份
```bash
# 添加 cron 任务
crontab -e
# 每天凌晨 2 点备份
0 2 * * * /var/www/pmo-system/backup.sh
```

---

## 监控

### 服务监控
```bash
# 检查服务状态
sudo systemctl status pmo-backend
sudo systemctl status nginx
sudo systemctl status postgresql
```

### 日志监控
```bash
# 后端日志
sudo journalctl -u pmo-backend -f

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# PostgreSQL 日志
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

---

## 下一步

- [ ] 配置 HTTPS (Let's Encrypt)
- [ ] 设置监控告警
- [ ] 配置日志轮转
- [ ] 制定灾难恢复计划

---

## 相关文档

- [本地开发](./local-dev.md)
- [数据库管理](./database.md)
- [架构概览](../architecture/overview.md)
