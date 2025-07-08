#!/usr/bin/env python3
"""
健康检查路由
提供系统状态检查接口
"""

from flask import Blueprint, jsonify
from datetime import datetime
import time

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        return jsonify({
            'status': 'healthy',
            'message': '系统运行正常',
            'timestamp': datetime.utcnow().isoformat(),
            'server_time': time.time()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': f'系统异常: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/ping', methods=['GET'])
def ping():
    """简单的ping接口"""
    return jsonify({
        'message': 'pong',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@health_bp.route('/status', methods=['GET'])
def status():
    """系统状态接口"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'message': '用户管理系统 API 服务正在运行',
        'timestamp': datetime.utcnow().isoformat()
    }), 200 