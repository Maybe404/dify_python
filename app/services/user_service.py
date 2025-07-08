#!/usr/bin/env python3
"""
用户服务层
处理用户相关的业务逻辑
"""

from typing import Optional, Dict, Any
from app.models.user import User
from app.utils.security import validate_password
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class UserService:
    """用户业务逻辑服务"""
    
    @staticmethod
    def create_user(username: str, email: str, password: str) -> User:
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            ValueError: 当输入数据无效时
        """
        # 验证输入数据
        if not username or not email or not password:
            raise ValueError("用户名、邮箱和密码不能为空")
        
        # 验证密码强度
        is_valid, message = validate_password(password)
        if not is_valid:
            raise ValueError(f"密码不符合要求: {message}")
        
        # 检查用户名是否已存在
        if User.find_by_username(username):
            raise ValueError("用户名已被注册")
        
        # 检查邮箱是否已存在
        if User.find_by_email(email):
            raise ValueError("邮箱已被注册")
        
        try:
            # 创建用户
            user = User(username=username, email=email)
            user.password = password  # 密码会自动加密
            user.save()
            
            logger.info(f"用户创建成功: {username} ({email})")
            return user
            
        except Exception as e:
            logger.error(f"用户创建失败: {username} - 错误: {str(e)}")
            raise ValueError(f"用户创建失败: {str(e)}")
    
    @staticmethod
    def authenticate_user(credential: str, password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            credential: 用户名或邮箱
            password: 密码
            
        Returns:
            User: 认证成功返回用户对象，失败返回None
        """
        if not credential or not password:
            return None
        
        # 尝试通过用户名查找
        user = User.find_by_username(credential)
        
        # 如果用户名查找失败，尝试通过邮箱查找
        if not user:
            user = User.find_by_email(credential)
        
        # 验证密码
        if user and user.check_password(password):
            # 检查账户是否激活
            if not user.is_active:
                logger.warning(f"尝试登录被禁用账户: {credential}")
                return None
            
            # 更新最后登录时间
            user.update_last_login()
            logger.info(f"用户认证成功: {user.username} ({user.email})")
            return user
        
        logger.warning(f"用户认证失败: {credential}")
        return None
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            User: 用户对象或None
        """
        try:
            user = User.find_by_id(user_id)
            if user:
                logger.debug(f"获取用户信息: {user.username}")
            return user
        except Exception as e:
            logger.error(f"获取用户失败: {user_id} - 错误: {str(e)}")
            return None
    
    @staticmethod
    def update_user_profile(user_id: str, **kwargs) -> Optional[User]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段
            
        Returns:
            User: 更新后的用户对象或None
        """
        try:
            user = User.find_by_id(user_id)
            if not user:
                return None
            
            # 更新允许的字段
            allowed_fields = ['username', 'email']
            updated_fields = []
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    # 检查邮箱和用户名唯一性
                    if field == 'email' and value != user.email:
                        if User.find_by_email(value):
                            raise ValueError("邮箱已被其他用户使用")
                    
                    if field == 'username' and value != user.username:
                        if User.find_by_username(value):
                            raise ValueError("用户名已被其他用户使用")
                    
                    setattr(user, field, value)
                    updated_fields.append(field)
            
            if updated_fields:
                user.save()
                logger.info(f"用户信息更新成功: {user.username} - 字段: {updated_fields}")
            
            return user
            
        except Exception as e:
            logger.error(f"用户信息更新失败: {user_id} - 错误: {str(e)}")
            raise ValueError(f"更新失败: {str(e)}")
    
    @staticmethod
    def change_password(user_id: str, old_password: str, new_password: str) -> bool:
        """
        修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            bool: 修改成功返回True
        """
        try:
            user = User.find_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            # 验证旧密码
            if not user.check_password(old_password):
                raise ValueError("当前密码错误")
            
            # 验证新密码强度
            is_valid, message = validate_password(new_password)
            if not is_valid:
                raise ValueError(f"新密码不符合要求: {message}")
            
            # 检查新密码是否与旧密码相同
            if user.check_password(new_password):
                raise ValueError("新密码不能与当前密码相同")
            
            # 更新密码
            user.password = new_password
            user.save()
            
            logger.info(f"密码修改成功: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"密码修改失败: {user_id} - 错误: {str(e)}")
            raise ValueError(str(e))
    
    @staticmethod
    def deactivate_user(user_id: str) -> bool:
        """
        禁用用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 操作成功返回True
        """
        try:
            user = User.find_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            user.is_active = False
            user.save()
            
            logger.info(f"用户已禁用: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"用户禁用失败: {user_id} - 错误: {str(e)}")
            raise ValueError(str(e))
    
    @staticmethod
    def activate_user(user_id: str) -> bool:
        """
        激活用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 操作成功返回True
        """
        try:
            user = User.find_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            user.is_active = True
            user.save()
            
            logger.info(f"用户已激活: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"用户激活失败: {user_id} - 错误: {str(e)}")
            raise ValueError(str(e))
    
    @staticmethod
    def get_user_stats() -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            from sqlalchemy import func
            from app import db
            
            # 总用户数
            total_users = db.session.query(func.count(User.id)).scalar()
            
            # 活跃用户数
            active_users = db.session.query(func.count(User.id)).filter(User.is_active == True).scalar()
            
            # 近期注册用户数（7天内）
            from datetime import datetime, timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_users = db.session.query(func.count(User.id)).filter(
                User.created_at >= week_ago
            ).scalar()
            
            stats = {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'recent_registrations': recent_users
            }
            
            logger.debug(f"用户统计: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {str(e)}")
            return {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'recent_registrations': 0
            } 