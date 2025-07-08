#!/usr/bin/env python3
"""
认证服务层
处理JWT认证相关的业务逻辑
"""

from typing import Dict, Any, Optional
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt
from app.models.user import User
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """认证业务逻辑服务"""
    
    @staticmethod
    def login(credential: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            credential: 用户名或邮箱
            password: 密码
            
        Returns:
            Dict: 登录结果
        """
        try:
            # 验证用户凭据
            user = UserService.authenticate_user(credential, password)
            
            if not user:
                return {
                    'success': False,
                    'message': '用户名/邮箱或密码错误',
                    'code': 401
                }
            
            # 生成访问令牌
            access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active
                }
            )
            
            logger.info(f"用户登录成功: {user.username} ({user.email})")
            
            return {
                'success': True,
                'message': '登录成功',
                'data': {
                    'access_token': access_token,
                    'token_type': 'Bearer',
                    'user': user.to_dict()
                },
                'code': 200
            }
            
        except Exception as e:
            logger.error(f"登录过程发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'登录失败: {str(e)}',
                'code': 500
            }
    
    @staticmethod
    def register(username: str, email: str, password: str) -> Dict[str, Any]:
        """
        用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            
        Returns:
            Dict: 注册结果
        """
        try:
            # 创建用户
            user = UserService.create_user(username, email, password)
            
            logger.info(f"用户注册成功: {username} ({email})")
            
            return {
                'success': True,
                'message': '注册成功',
                'data': {
                    'user': user.to_dict()
                },
                'code': 201
            }
            
        except ValueError as e:
            logger.warning(f"用户注册失败: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'code': 400
            }
        except Exception as e:
            logger.error(f"注册过程发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'注册失败: {str(e)}',
                'code': 500
            }
    
    @staticmethod
    def get_current_user() -> Optional[User]:
        """
        获取当前登录用户
        
        Returns:
            User: 当前用户对象或None
        """
        try:
            current_user_id = get_jwt_identity()
            if current_user_id:
                return UserService.get_user_by_id(current_user_id)
            return None
        except Exception as e:
            logger.error(f"获取当前用户失败: {str(e)}")
            return None
    
    @staticmethod
    def verify_token() -> Dict[str, Any]:
        """
        验证当前token
        
        Returns:
            Dict: 验证结果
        """
        try:
            user = AuthService.get_current_user()
            
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在或token无效',
                    'code': 401
                }
            
            if not user.is_active:
                return {
                    'success': False,
                    'message': '账户已被禁用',
                    'code': 403
                }
            
            # 获取token信息
            jwt_claims = get_jwt()
            
            return {
                'success': True,
                'message': 'Token验证成功',
                'data': {
                    'user': user.to_dict(),
                    'token_info': {
                        'exp': jwt_claims.get('exp'),
                        'iat': jwt_claims.get('iat'),
                        'jti': jwt_claims.get('jti')
                    }
                },
                'code': 200
            }
            
        except Exception as e:
            logger.error(f"Token验证过程发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'Token验证失败: {str(e)}',
                'code': 500
            }
    
    @staticmethod
    def change_password(current_password: str, new_password: str) -> Dict[str, Any]:
        """
        修改密码
        
        Args:
            current_password: 当前密码
            new_password: 新密码
            
        Returns:
            Dict: 修改结果
        """
        try:
            user = AuthService.get_current_user()
            
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'code': 404
                }
            
            # 使用用户服务修改密码
            UserService.change_password(user.id, current_password, new_password)
            
            return {
                'success': True,
                'message': '密码修改成功',
                'code': 200
            }
            
        except ValueError as e:
            return {
                'success': False,
                'message': str(e),
                'code': 400
            }
        except Exception as e:
            logger.error(f"修改密码过程发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'密码修改失败: {str(e)}',
                'code': 500
            }
    
    @staticmethod
    def update_profile(**kwargs) -> Dict[str, Any]:
        """
        更新用户资料
        
        Args:
            **kwargs: 要更新的字段
            
        Returns:
            Dict: 更新结果
        """
        try:
            user = AuthService.get_current_user()
            
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'code': 404
                }
            
            # 使用用户服务更新资料
            updated_user = UserService.update_user_profile(user.id, **kwargs)
            
            if updated_user:
                return {
                    'success': True,
                    'message': '资料更新成功',
                    'data': {
                        'user': updated_user.to_dict()
                    },
                    'code': 200
                }
            else:
                return {
                    'success': False,
                    'message': '更新失败',
                    'code': 400
                }
                
        except ValueError as e:
            return {
                'success': False,
                'message': str(e),
                'code': 400
            }
        except Exception as e:
            logger.error(f"更新资料过程发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'资料更新失败: {str(e)}',
                'code': 500
            }
    
    @staticmethod
    def logout() -> Dict[str, Any]:
        """
        用户登出
        
        Returns:
            Dict: 登出结果
        """
        try:
            # 获取当前token的JTI
            jwt_claims = get_jwt()
            jti = jwt_claims.get('jti')
            
            # 将token加入撤销列表
            from app.routes.auth import revoked_tokens
            revoked_tokens.add(jti)
            
            user = AuthService.get_current_user()
            if user:
                logger.info(f"用户登出: {user.username}")
            
            return {
                'success': True,
                'message': '登出成功',
                'code': 200
            }
            
        except Exception as e:
            logger.error(f"登出过程发生错误: {str(e)}")
            return {
                'success': False,
                'message': f'登出失败: {str(e)}',
                'code': 500
            } 