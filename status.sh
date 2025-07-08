#!/bin/bash

# 查看用户管理系统后台服务状态

echo "📊 用户管理系统服务状态"
echo "========================="

PID_FILE="app.pid"

if [ ! -f $PID_FILE ]; then
    echo "❌ 状态: 未运行"
    echo "💡 启动命令: ./start_background.sh"
    exit 1
fi

PID=$(cat $PID_FILE)

if ps -p $PID > /dev/null 2>&1; then
    echo "✅ 状态: 运行中"
    echo "📍 PID: $PID"
    
    # 获取进程信息
    echo "⏰ 启动时间: $(ps -o lstart= -p $PID)"
    echo "💾 内存使用: $(ps -o rss= -p $PID | xargs -I {} echo 'scale=2; {}/1024' | bc)MB"
    echo "⚡ CPU使用: $(ps -o %cpu= -p $PID)%"
    
    # 检查端口是否监听
    if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
        echo "🌐 端口状态: 5000端口正在监听"
        echo "🔗 访问地址: http://localhost:5000"
    else
        echo "⚠️  端口状态: 5000端口未监听"
    fi
    
    # 检查日志文件
    if [ -f "logs/app.log" ]; then
        echo "📝 应用日志: logs/app.log ($(wc -l < logs/app.log) 行)"
        echo "📄 最新日志:"
        tail -3 logs/app.log | sed 's/^/   /'
    fi
    
    if [ -f "logs/nohup.log" ]; then
        echo "📝 系统日志: logs/nohup.log ($(wc -l < logs/nohup.log) 行)"
    fi
    
    echo ""
    echo "🔧 管理命令:"
    echo "   停止服务: ./stop_background.sh"
    echo "   查看日志: tail -f logs/app.log"
    echo "   重启服务: ./stop_background.sh && ./start_background.sh"
else
    echo "❌ 状态: 进程不存在 (PID: $PID)"
    echo "🧹 清理PID文件..."
    rm -f $PID_FILE
    echo "💡 启动命令: ./start_background.sh"
fi 