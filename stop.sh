#!/bin/bash

# 停止用户管理系统后台服务

echo "🛑 停止用户管理系统后台服务"

PID_FILE="app.pid"

if [ ! -f $PID_FILE ]; then
    echo "⚠️  PID文件不存在，服务可能未运行"
    exit 1
fi

PID=$(cat $PID_FILE)

if ps -p $PID > /dev/null 2>&1; then
    echo "🔄 正在停止服务 (PID: $PID)..."
    kill $PID
    
    # 等待进程结束
    for i in {1..10}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "✅ 服务已停止"
            rm -f $PID_FILE
            exit 0
        fi
        sleep 1
    done
    
    # 强制终止
    echo "⚠️  强制终止服务..."
    kill -9 $PID
    echo "✅ 服务已强制停止"
    rm -f $PID_FILE
else
    echo "⚠️  进程不存在 (PID: $PID)"
    rm -f $PID_FILE
fi 