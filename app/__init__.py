from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from app.config.config import Config

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)
    
    # 配置JWT错误处理器
    setup_jwt_error_handlers(app)
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.health import health_bp
    from app.routes.dify_v2 import dify_v2_bp
    from app.routes.tasks import tasks_bp
    from app.routes.neo4j_routes import neo4j_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(dify_v2_bp, url_prefix='/api/dify/v2')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(neo4j_bp, url_prefix='/api/neo4j')
    
    # 初始化应用配置（包括日志）
    Config.init_app(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app

def setup_jwt_error_handlers(app):
    """设置JWT错误处理器"""
    from flask import jsonify
    
    # 导入撤销token列表
    from app.routes.auth import revoked_tokens
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """检查token是否被撤销"""
        jti = jwt_payload['jti']
        return jti in revoked_tokens
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token已过期，请重新登录'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        app.logger.warning(f"无效的token: {error}")
        return jsonify({
            'success': False,
            'message': 'Token无效，请检查格式或重新登录'
        }), 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': '缺少授权token，请先登录'
        }), 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': '需要刷新token'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token已被撤销，请重新登录'
        }), 401 