import os
from datetime import timedelta
from dotenv import load_dotenv

# 确保加载.env文件
load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 数据库配置 - 仅支持MySQL
    # 优先使用完整的DATABASE_URL，否则使用分别配置的变量
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # 从环境变量构建MySQL连接字符串
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = int(os.getenv('DB_PORT', 3306))
        DB_USERNAME = os.getenv('DB_USERNAME', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'defaultpassword')
        DB_NAME = os.getenv('DB_NAME', 'user_system')
        
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'charset': 'utf8mb4'} if 'mysql' in os.getenv('DATABASE_URL', '') else {}
    }
    
    # MySQL特定配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USERNAME = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'user_system')
    
    # ============================================================================
    # 文件存储配置 - 可通过环境变量自定义存储路径
    # ============================================================================
    
    # 数据根目录 - 所有文件存储的基础目录
    DATA_ROOT_DIR = os.getenv('DATA_ROOT_DIR', 'data')
    
    # 上传文件存储目录 - 用户上传的原始文件
    UPLOAD_FILES_DIR = os.getenv('UPLOAD_FILES_DIR', os.path.join(DATA_ROOT_DIR, 'uploads'))
    
    # 导出文件存储目录 - PDF、Excel、Markdown等导出文件
    EXPORT_FILES_DIR = os.getenv('EXPORT_FILES_DIR', os.path.join(DATA_ROOT_DIR, 'exports'))
    
    # 临时文件目录 - 处理过程中的临时文件
    TEMP_FILES_DIR = os.getenv('TEMP_FILES_DIR', os.path.join(DATA_ROOT_DIR, 'temp'))
    
    @classmethod
    def get_data_directory(cls):
        """获取数据根目录的绝对路径"""
        if os.path.isabs(cls.DATA_ROOT_DIR):
            # 如果是绝对路径，直接使用
            data_dir = cls.DATA_ROOT_DIR
        else:
            # 如果是相对路径，相对于项目根目录
            data_dir = os.path.join(os.getcwd(), cls.DATA_ROOT_DIR)
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    @classmethod
    def get_upload_directory(cls):
        """获取上传文件目录的绝对路径"""
        if os.path.isabs(cls.UPLOAD_FILES_DIR):
            upload_dir = cls.UPLOAD_FILES_DIR
        else:
            upload_dir = os.path.join(cls.get_data_directory(), os.path.basename(cls.UPLOAD_FILES_DIR))
        
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    
    @classmethod
    def get_export_directory(cls):
        """获取导出文件目录的绝对路径"""
        if os.path.isabs(cls.EXPORT_FILES_DIR):
            export_dir = cls.EXPORT_FILES_DIR
        else:
            export_dir = os.path.join(cls.get_data_directory(), os.path.basename(cls.EXPORT_FILES_DIR))
        
        if not os.path.exists(export_dir):
            os.makedirs(export_dir, exist_ok=True)
        return export_dir
    
    @classmethod
    def get_temp_directory(cls):
        """获取临时文件目录的绝对路径"""
        if os.path.isabs(cls.TEMP_FILES_DIR):
            temp_dir = cls.TEMP_FILES_DIR
        else:
            temp_dir = os.path.join(cls.get_data_directory(), os.path.basename(cls.TEMP_FILES_DIR))
        
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 43200)))  # 12小时 = 43200秒
    JWT_ALGORITHM = 'HS256'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_HEADER_NAME = 'Authorization'
    JWT_TOKEN_LOCATION = ['headers']
    JWT_DECODE_LEEWAY = 10  # 允许10秒的时钟偏差
    
    # CORS配置
    CORS_HEADERS = 'Content-Type'
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO' if not DEBUG else 'DEBUG')
    LOG_TO_STDOUT = os.getenv('LOG_TO_STDOUT', 'True' if DEBUG else 'False').lower() == 'true'
    LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'True').lower() == 'true'
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '10'))
    
    # 会话列表专用Dify API配置（独立管理）
    DIFY_CONVERSATIONS_API_URL = os.getenv('DIFY_CONVERSATIONS_API_URL', 'http://10.100.100.93/v1/conversations')
    DIFY_CONVERSATIONS_API_KEY = os.getenv('DIFY_CONVERSATIONS_API_KEY', 'app-conversations-key')
    
    # 会话历史消息专用Dify API配置（独立管理）
    DIFY_MESSAGES_API_URL = os.getenv('DIFY_MESSAGES_API_URL', 'http://10.100.100.93/v1/messages')
    DIFY_MESSAGES_API_KEY = os.getenv('DIFY_MESSAGES_API_KEY', 'app-messages-key')
    
    @classmethod
    def init_app(cls, app):
        """初始化应用配置"""
        # 配置日志
        import logging
        import os
        from logging.handlers import RotatingFileHandler
        
        # 设置日志级别
        log_level = getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)
        app.logger.setLevel(log_level)
        
        # 创建日志目录
        log_dir = os.path.dirname(cls.LOG_FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 日志格式 - 确保支持中文
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s [in %(pathname)s:%(lineno)d]',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 清除已有的处理器，避免重复
        app.logger.handlers.clear()
        
        # 文件日志处理器
        if cls.LOG_TO_FILE:
            file_handler = RotatingFileHandler(
                cls.LOG_FILE_PATH,
                maxBytes=cls.LOG_MAX_BYTES,
                backupCount=cls.LOG_BACKUP_COUNT,
                encoding='utf-8',  # UTF-8编码
                delay=True  # 延迟创建文件，确保编码正确
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            app.logger.addHandler(file_handler)
        
        # 控制台日志处理器
        if cls.LOG_TO_STDOUT or app.debug:
            import sys
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(log_level)
            app.logger.addHandler(console_handler)
        
        # 设置根日志记录器，避免重复日志
        app.logger.propagate = False
        
        # 记录应用启动
        environment = 'development' if app.debug else 'production'
        app.logger.info(f'应用启动 - {environment}环境')
        app.logger.info(f'日志级别: {cls.LOG_LEVEL}')
        app.logger.info(f'日志文件: {cls.LOG_FILE_PATH if cls.LOG_TO_FILE else "仅控制台输出"}')
        
        # 记录文件存储配置
        app.logger.info(f'数据根目录: {cls.get_data_directory()}')
        app.logger.info(f'上传文件目录: {cls.get_upload_directory()}')
        app.logger.info(f'导出文件目录: {cls.get_export_directory()}')
        app.logger.info(f'临时文件目录: {cls.get_temp_directory()}') 