from app import db, bcrypt
from datetime import datetime, timedelta
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
import secrets

class User(db.Model):
    """用户模型"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='用户唯一标识符（UUID格式）')
    username = db.Column(db.String(80), unique=True, nullable=True, index=True, comment='用户名（可选）')
    email = db.Column(db.String(120), unique=True, nullable=False, index=True, comment='邮箱地址')
    _password_hash = db.Column('password_hash', db.String(255), nullable=False, comment='密码哈希')
    
    # 密码重置相关字段
    reset_token = db.Column(db.String(255), nullable=True, comment='密码重置令牌')
    reset_token_expires = db.Column(db.DateTime, nullable=True, comment='重置令牌过期时间')
    
    is_active = db.Column(db.Boolean, default=True, nullable=False, comment='是否激活')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    last_login = db.Column(db.DateTime, nullable=True, comment='最后登录时间')
    
    @hybrid_property
    def password(self):
        """密码属性（只写）"""
        raise AttributeError('密码不可读')
    
    @password.setter
    def password(self, password):
        """设置密码（自动加密）"""
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        return bcrypt.check_password_hash(self._password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        return data
    
    @staticmethod
    def find_by_username(username):
        """根据用户名查找用户"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_email(email):
        """根据邮箱查找用户"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_id(user_id):
        """根据ID查找用户"""
        return User.query.get(user_id)
    
    def save(self):
        """保存用户到数据库"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """从数据库删除用户"""
        db.session.delete(self)
        db.session.commit()
    
    def generate_reset_token(self, expires_in=3600):
        """生成密码重置令牌（默认1小时过期）"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(seconds=expires_in)
        db.session.commit()
        return self.reset_token
    
    def verify_reset_token(self, token):
        """验证密码重置令牌"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        
        if datetime.utcnow() > self.reset_token_expires:
            # 令牌已过期，清除令牌
            self.clear_reset_token()
            return False
        
        return self.reset_token == token
    
    def clear_reset_token(self):
        """清除密码重置令牌"""
        self.reset_token = None
        self.reset_token_expires = None
        db.session.commit()
    
    def reset_password(self, new_password, token):
        """重置密码"""
        if not self.verify_reset_token(token):
            return False
        
        self.password = new_password
        self.clear_reset_token()
        return True
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def find_by_reset_token(token):
        """根据重置令牌查找用户"""
        return User.query.filter_by(reset_token=token).first()
    
    def __repr__(self):
        return f'<User {self.username or self.email}>' 