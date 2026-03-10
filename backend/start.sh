#!/bin/bash
# PMO系统后端启动脚本

cd "$(dirname "$0")"

echo "🚀 正在启动 PMO项目管理系统 后端..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt -q

# 启动服务
echo "✅ 启动 FastAPI 服务 (http://localhost:8000)"
echo "📖 API文档: http://localhost:8000/docs"
echo "🔑 默认账号: admin / admin123"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
