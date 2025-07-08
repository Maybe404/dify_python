#!/bin/bash

# Linux服务器部署脚本
# 用于将用户管理系统部署到Linux服务器

set -e  # 遇到错误时停止执行

echo "🚀 开始部署用户管理系统到Linux服务器"
echo "=========================================="

# 检查Python版本
echo "📋 检查系统环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ 错误: 未找到Python3，请先安装Python3.7+"
    exit 1
fi

# 检查pip
pip3 --version
if [ $? -ne 0 ]; then
    echo "❌ 错误: 未找到pip3，请先安装pip3"
    exit 1
fi

# 安装中文字体支持
echo "🔤 安装中文字体支持..."
sudo apt-get update
sudo apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei fonts-noto-cjk fontconfig
sudo fc-cache -fv
echo "✅ 中文字体安装完成"

# 创建项目目录
PROJECT_DIR="/opt/user_system"
echo "📁 创建项目目录: $PROJECT_DIR"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# 复制项目文件（假设当前目录是项目根目录）
echo "📦 复制项目文件..."
cp -r . $PROJECT_DIR/
cd $PROJECT_DIR

# 创建虚拟环境
echo "🐍 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📚 安装项目依赖..."
pip install -r requirements.txt

# 创建环境变量文件
echo "🔧 配置环境变量..."
if [ ! -f .env ]; then
    cp env_example.txt .env
    echo "⚠️  请编辑 .env 文件配置数据库连接等信息"
    echo "   配置文件路径: $PROJECT_DIR/.env"
fi

# 创建日志目录
echo "📝 创建日志目录..."
mkdir -p logs
chmod 755 logs

# 创建systemd服务文件
echo "🔧 配置systemd服务..."
sudo tee /etc/systemd/system/user-system.service > /dev/null <<EOF
[Unit]
Description=User Management System Flask App
After=network.target mysql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/run.py
Restart=always
RestartSec=5
StandardOutput=append:$PROJECT_DIR/logs/systemd.log
StandardError=append:$PROJECT_DIR/logs/systemd.log

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用服务（开机自启动）
sudo systemctl enable user-system.service

echo ""
echo "✅ 部署完成！"
echo "=========================================="
echo "📍 项目路径: $PROJECT_DIR"
echo "🔧 配置文件: $PROJECT_DIR/.env"
echo "📝 日志文件: $PROJECT_DIR/logs/"
echo ""
echo "🎛️  服务管理命令:"
echo "   启动服务: sudo systemctl start user-system"
echo "   停止服务: sudo systemctl stop user-system"
echo "   重启服务: sudo systemctl restart user-system"
echo "   查看状态: sudo systemctl status user-system"
echo "   查看日志: sudo journalctl -u user-system -f"
echo "   查看应用日志: tail -f $PROJECT_DIR/logs/app.log"
echo ""
echo "🌐 服务访问:"
echo "   本地访问: http://localhost:5000"
echo "   如需外网访问，请配置防火墙和反向代理"
echo ""
echo "⚠️  下一步操作:"
echo "1. 编辑配置文件: nano $PROJECT_DIR/.env"
echo "2. 配置数据库连接信息"
echo "3. 启动服务: sudo systemctl start user-system"
echo "4. 检查服务状态: sudo systemctl status user-system" 