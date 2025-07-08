"""
多环境配置文件（可选实施）
这是一个更完善的环境配置方案，可以替代当前的 config.py
"""

import os
from datetime import timedelta

class BaseConfig:
    """基础配置类 - 包含所有环境通用的配置"""
    
    # Flask基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据库基础配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT基础配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 43200)))  # 12小时 = 43200秒
    JWT_ALGORITHM = 'HS256'
    
    # 数据库连接配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USERNAME = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'user_system')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """动态生成数据库URI"""
        return os.getenv('DATABASE_URL') or \
               f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    
    # 开发环境特有配置
    DEBUG = True
    FLASK_ENV = 'development'
    
    # 开发环境数据库配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        **BaseConfig.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': True,  # 开发环境下显示SQL语句
    }
    
    # 开发环境CORS配置（更宽松）
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "file://"]
    
    # 开发环境日志配置
    LOG_LEVEL = 'DEBUG'
    LOG_TO_STDOUT = True
    
    # 开发环境安全配置（较宽松）
    WTF_CSRF_ENABLED = False  # 开发时可能需要关闭CSRF
    
    @classmethod
    def init_app(cls, app):
        """开发环境特有的应用初始化"""
        print("🔧 运行在开发环境")

class ProductionConfig(BaseConfig):
    """生产环境配置"""
    
    # 生产环境特有配置
    DEBUG = False
    FLASK_ENV = 'production'
    
    # 生产环境数据库配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        **BaseConfig.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': 20,  # 生产环境增加连接池
        'max_overflow': 30,
        'connect_args': {
            'charset': 'utf8mb4',
            'connect_timeout': 60,
            'read_timeout': 30,
            'write_timeout': 30,
        }
    }
    
    # 生产环境CORS配置（严格）
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    
    # 生产环境日志配置
    LOG_LEVEL = 'INFO'
    LOG_TO_STDOUT = False
    LOG_FILE = 'logs/app.log'
    
    # 生产环境安全配置（严格）
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True  # 要求HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 生产环境性能配置
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(days=365)  # 静态文件缓存一年
    
    @classmethod
    def init_app(cls, app):
        """生产环境特有的应用初始化"""
        print("🚀 运行在生产环境")
        
        # 生产环境日志配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            # 创建日志目录
            os.makedirs('logs', exist_ok=True)
            
            # 配置文件日志
            file_handler = RotatingFileHandler(
                'logs/app.log', 
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('应用启动 - 生产环境')

class TestingConfig(BaseConfig):
    """测试环境配置"""
    
    # 测试环境特有配置
    TESTING = True
    DEBUG = True
    FLASK_ENV = 'testing'
    
    # 测试环境数据库配置（使用MySQL测试数据库）
    # 建议创建专门的测试数据库，如 user_system_test
    DB_HOST = os.getenv('TEST_DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('TEST_DB_PORT', 3306))
    DB_USERNAME = os.getenv('TEST_DB_USERNAME', 'root')
    DB_PASSWORD = os.getenv('TEST_DB_PASSWORD', os.getenv('DB_PASSWORD', 'defaultpassword'))
    DB_NAME = os.getenv('TEST_DB_NAME', 'user_system_test')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """测试环境MySQL数据库URI"""
        return f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # 测试环境JWT配置（较短的过期时间）
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=60)  # 1分钟过期，便于测试
    
    # 测试环境安全配置
    WTF_CSRF_ENABLED = False
    
    @classmethod
    def init_app(cls, app):
        """测试环境特有的应用初始化"""
        print("🧪 运行在测试环境 (MySQL)")

# 环境配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config_class(config_name=None):
    """获取配置类"""
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')
    return config.get(config_name, config['default']) 