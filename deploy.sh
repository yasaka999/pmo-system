#!/bin/bash
# PMO 系统部署脚本
# 使用方法: ./deploy.sh

SERVER="root@142.171.178.36"
SSH_PORT="2022"
REMOTE_DIR="/opt/pmo-system-new"

echo "=== 部署后端代码 ==="
# 同步后端代码，排除数据库和日志
rsync -avz --delete \
  --exclude='*.db' \
  --exclude='*.db-journal' \
  --exclude='*.log' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  -e "ssh -p $SSH_PORT" \
  ./backend/ $SERVER:$REMOTE_DIR/backend/

echo "=== 重启服务 ==="
ssh -p $SSH_PORT $SERVER "cd $REMOTE_DIR/backend && ps aux | grep uvicorn | grep -v grep | awk '{print \$2}' | xargs kill -9 2>/dev/null; sleep 1; nohup /usr/local/python3/bin/python3.8 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/pmo.log 2>&1 &"

echo "=== 部署完成 ==="
