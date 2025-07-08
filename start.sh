#!/bin/bash

# 后台运行用户管理系统
# 适用于简单的Linux服务器环境

echo "🚀 启动用户管理系统后台服务"

# 检查是否已经在运行
PID_FILE="app.pid"
if [ -f $PID_FILE ]; then
    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  服务已在运行 (PID: $PID)"
        echo "如需重启，请先运行: ./stop_background.sh"
        exit 1
    else
        echo "🧹 清理过期的PID文件"
        rm -f $PID_FILE
    fi
fi

# 创建日志目录
mkdir -p logs

# 启动应用并记录PID
echo "▶️  启动Flask应用..."
nohup python3 run.py > logs/nohup.log 2>&1 &
PID=$!

# 保存PID
echo $PID > $PID_FILE

# 验证启动
sleep 2
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ 服务启动成功!"
    echo "📍 PID: $PID"
    echo "📝 日志文件: logs/nohup.log"
    echo "📝 应用日志: logs/app.log"
    echo "🌐 访问地址: http://localhost:5000"
    echo ""
    echo "🔧 管理命令:"
    echo "   查看状态: ./status_background.sh"
    echo "   停止服务: ./stop_background.sh"
    echo "   查看日志: tail -f logs/nohup.log"
    echo "   查看应用日志: tail -f logs/app.log"
else
    echo "❌ 服务启动失败"
    echo "📝 请查看日志: cat logs/nohup.log"
    rm -f $PID_FILE
    exit 1
fi 