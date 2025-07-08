"""
日志工具模块
提供统一的日志记录功能，包括请求追踪、性能监控、安全事件记录等
"""

import time
import functools
from flask import request, current_app, g
import uuid
from datetime import datetime


def get_request_info():
    """获取请求基本信息"""
    return {
        'ip': request.remote_addr if request else 'Unknown',
        'user_agent': request.headers.get('User-Agent', 'Unknown') if request else 'Unknown',
        'method': request.method if request else 'Unknown',
        'path': request.path if request else 'Unknown',
        'request_id': getattr(g, 'request_id', str(uuid.uuid4()))
    }


def log_api_request(func):
    """API请求日志装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 生成请求ID
        g.request_id = str(uuid.uuid4())
        
        start_time = time.time()
        request_info = get_request_info()
        
        # 记录请求开始
        current_app.logger.info(
            f"API请求开始 - 方法: {request_info['method']} - "
            f"路径: {request_info['path']} - IP: {request_info['ip']} - "
            f"请求ID: {request_info['request_id']}"
        )
        
        try:
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 计算耗时
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            
            # 获取响应状态码
            status_code = result[1] if isinstance(result, tuple) and len(result) > 1 else 200
            
            # 记录请求成功
            current_app.logger.info(
                f"API请求完成 - 方法: {request_info['method']} - "
                f"路径: {request_info['path']} - 状态码: {status_code} - "
                f"耗时: {elapsed_time}ms - IP: {request_info['ip']} - "
                f"请求ID: {request_info['request_id']}"
            )
            
            return result
            
        except Exception as e:
            # 计算耗时
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            
            # 记录请求失败
            current_app.logger.error(
                f"API请求异常 - 方法: {request_info['method']} - "
                f"路径: {request_info['path']} - 耗时: {elapsed_time}ms - "
                f"IP: {request_info['ip']} - 请求ID: {request_info['request_id']} - "
                f"错误: {str(e)}", exc_info=True
            )
            
            raise
    
    return wrapper


class SecurityLogger:
    """安全事件日志记录器"""
    
    @staticmethod
    def log_login_attempt(username_or_email, success=True, reason=None, user_id=None):
        """记录登录尝试"""
        request_info = get_request_info()
        
        if success:
            current_app.logger.info(
                f"安全事件: 登录成功 - 用户: {username_or_email} - "
                f"用户ID: {user_id} - IP: {request_info['ip']} - "
                f"User-Agent: {request_info['user_agent'][:100]} - "
                f"请求ID: {request_info['request_id']}"
            )
        else:
            current_app.logger.warning(
                f"安全事件: 登录失败 - 用户: {username_or_email} - "
                f"原因: {reason} - IP: {request_info['ip']} - "
                f"User-Agent: {request_info['user_agent'][:100]} - "
                f"请求ID: {request_info['request_id']}"
            )
    
    @staticmethod
    def log_registration(username, email, success=True, reason=None, user_id=None):
        """记录用户注册"""
        request_info = get_request_info()
        
        if success:
            current_app.logger.info(
                f"安全事件: 用户注册成功 - 用户名: {username} - "
                f"邮箱: {email} - 用户ID: {user_id} - "
                f"IP: {request_info['ip']} - 请求ID: {request_info['request_id']}"
            )
        else:
            current_app.logger.warning(
                f"安全事件: 用户注册失败 - 用户名: {username} - "
                f"邮箱: {email} - 原因: {reason} - "
                f"IP: {request_info['ip']} - 请求ID: {request_info['request_id']}"
            )
    
    @staticmethod
    def log_logout(user_id, username):
        """记录用户登出"""
        request_info = get_request_info()
        
        current_app.logger.info(
            f"安全事件: 用户登出 - 用户ID: {user_id} - "
            f"用户名: {username} - IP: {request_info['ip']} - "
            f"请求ID: {request_info['request_id']}"
        )
    
    @staticmethod
    def log_password_change(user_id, username, success=True):
        """记录密码修改"""
        request_info = get_request_info()
        
        if success:
            current_app.logger.info(
                f"安全事件: 密码修改成功 - 用户ID: {user_id} - "
                f"用户名: {username} - IP: {request_info['ip']} - "
                f"请求ID: {request_info['request_id']}"
            )
        else:
            current_app.logger.warning(
                f"安全事件: 密码修改失败 - 用户ID: {user_id} - "
                f"用户名: {username} - IP: {request_info['ip']} - "
                f"请求ID: {request_info['request_id']}"
            )
    
    @staticmethod
    def log_suspicious_activity(activity_type, details, user_id=None):
        """记录可疑活动"""
        request_info = get_request_info()
        
        current_app.logger.warning(
            f"安全警告: {activity_type} - 详情: {details} - "
            f"用户ID: {user_id or 'Unknown'} - IP: {request_info['ip']} - "
            f"请求ID: {request_info['request_id']}"
        )


class BusinessLogger:
    """业务操作日志记录器"""
    
    @staticmethod
    def log_user_operation(operation, user_id, username, details=None):
        """记录用户操作"""
        request_info = get_request_info()
        
        current_app.logger.info(
            f"业务操作: {operation} - 用户ID: {user_id} - "
            f"用户名: {username} - 详情: {details or 'None'} - "
            f"IP: {request_info['ip']} - 请求ID: {request_info['request_id']}"
        )
    
    @staticmethod
    def log_database_operation(operation, table, record_id=None, details=None):
        """记录数据库操作"""
        request_info = get_request_info()
        
        current_app.logger.debug(
            f"数据库操作: {operation} - 表: {table} - "
            f"记录ID: {record_id or 'None'} - 详情: {details or 'None'} - "
            f"请求ID: {request_info['request_id']}"
        )


class PerformanceLogger:
    """性能监控日志记录器"""
    
    @staticmethod
    def log_slow_query(query_type, duration_ms, details=None):
        """记录慢查询"""
        request_info = get_request_info()
        
        current_app.logger.warning(
            f"性能警告: 慢查询 - 类型: {query_type} - "
            f"耗时: {duration_ms}ms - 详情: {details or 'None'} - "
            f"请求ID: {request_info['request_id']}"
        )
    
    @staticmethod
    def log_high_memory_usage(memory_mb, threshold_mb):
        """记录高内存使用"""
        request_info = get_request_info()
        
        current_app.logger.warning(
            f"性能警告: 高内存使用 - 当前: {memory_mb}MB - "
            f"阈值: {threshold_mb}MB - 请求ID: {request_info['request_id']}"
        )


class ErrorLogger:
    """错误日志记录器"""
    
    @staticmethod
    def log_error(error_type, error_message, user_id=None, stack_trace=None):
        """记录系统错误"""
        request_info = get_request_info()
        
        current_app.logger.error(
            f"系统错误: {error_type} - 消息: {error_message} - "
            f"用户ID: {user_id or 'Unknown'} - IP: {request_info['ip']} - "
            f"请求ID: {request_info['request_id']}"
        )
        
        if stack_trace:
            current_app.logger.error(f"错误堆栈: {stack_trace}")
    
    @staticmethod
    def log_validation_error(field, value, error_message, user_id=None):
        """记录数据验证错误"""
        request_info = get_request_info()
        
        current_app.logger.warning(
            f"验证错误: 字段 {field} - 值: {value} - "
            f"错误: {error_message} - 用户ID: {user_id or 'Unknown'} - "
            f"IP: {request_info['ip']} - 请求ID: {request_info['request_id']}"
        )


def init_request_logging():
    """初始化请求级别的日志记录"""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()


def log_request_summary():
    """记录请求总结"""
    if hasattr(g, 'start_time'):
        elapsed_time = round((time.time() - g.start_time) * 1000, 2)
        request_info = get_request_info()
        
        current_app.logger.debug(
            f"请求总结 - 总耗时: {elapsed_time}ms - "
            f"方法: {request_info['method']} - 路径: {request_info['path']} - "
            f"IP: {request_info['ip']} - 请求ID: {request_info['request_id']}"
        ) 