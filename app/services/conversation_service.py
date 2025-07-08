import os
import requests
import time
from flask import current_app
from app.config.config import Config

class ConversationService:
    """会话服务类 - 专门处理Dify会话列表转发"""
    
    @classmethod
    def get_conversations_config(cls):
        """获取会话列表API配置"""
        api_url = Config.DIFY_CONVERSATIONS_API_URL
        api_key = Config.DIFY_CONVERSATIONS_API_KEY
        
        return {
            'api_url': api_url,
            'api_key': api_key,
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        }
    
    @classmethod
    def forward_conversations_request(cls, query_params, user_info):
        """
        转发会话列表请求到Dify API
        
        Args:
            query_params (dict): 查询参数，包含user、last_id、limit等
            user_info (dict): 用户信息，用于日志记录
            
        Returns:
            tuple: (success, data, status_code)
        """
        start_time = time.time()
        
        try:
            # 获取配置
            config = cls.get_conversations_config()
            
            current_app.logger.info(f"[会话列表转发] 用户: {user_info.get('username')} - 参数: {query_params}")
            
            # 构建请求URL
            response = requests.get(
                config['api_url'],
                params=query_params,
                headers=config['headers'],
                timeout=30
            )
            
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            
            if response.ok:
                response_data = response.json()
                current_app.logger.info(
                    f"[会话列表转发成功] 用户: {user_info.get('username')} - "
                    f"返回条数: {len(response_data.get('data', []))} - 耗时: {elapsed_time}ms"
                )
                return True, response_data, 200
            else:
                error_msg = f"Dify API返回错误: {response.status_code}"
                current_app.logger.error(
                    f"[会话列表转发失败] 用户: {user_info.get('username')} - "
                    f"状态码: {response.status_code} - 耗时: {elapsed_time}ms"
                )
                try:
                    error_detail = response.json()
                    return False, error_detail, response.status_code
                except:
                    return False, {'error': error_msg}, response.status_code
                    
        except requests.RequestException as e:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.error(
                f"[会话列表转发网络错误] 用户: {user_info.get('username')} - "
                f"错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True
            )
            return False, {'error': f'网络请求失败: {str(e)}'}, 500
            
        except Exception as e:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.error(
                f"[会话列表转发系统错误] 用户: {user_info.get('username')} - "
                f"错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True
            )
            return False, {'error': f'系统错误: {str(e)}'}, 500
    
    @classmethod
    def validate_query_params(cls, params):
        """
        验证查询参数
        
        Args:
            params (dict): 查询参数
            
        Returns:
            tuple: (is_valid, errors, cleaned_params)
        """
        errors = []
        cleaned_params = {}
        
        # 必需参数：user
        user = params.get('user', '').strip()
        if not user:
            errors.append('缺少必需参数: user')
        else:
            cleaned_params['user'] = user
        
        # 可选参数：last_id
        last_id = params.get('last_id', '').strip()
        if last_id:
            cleaned_params['last_id'] = last_id
        
        # 可选参数：limit（默认20，最大100）
        limit = params.get('limit', '20')
        try:
            limit = int(limit)
            if limit <= 0:
                limit = 20
            elif limit > 100:
                limit = 100
            cleaned_params['limit'] = limit
        except (ValueError, TypeError):
            cleaned_params['limit'] = 20
        
        is_valid = len(errors) == 0
        return is_valid, errors, cleaned_params
    
    @classmethod
    def get_messages_config(cls):
        """获取会话历史消息API配置"""
        api_url = Config.DIFY_MESSAGES_API_URL
        api_key = Config.DIFY_MESSAGES_API_KEY
        
        return {
            'api_url': api_url,
            'api_key': api_key,
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        }
    
    @classmethod
    def forward_messages_request(cls, query_params, user_info):
        """
        转发会话历史消息请求到Dify API
        
        Args:
            query_params (dict): 查询参数，包含user、conversation_id等
            user_info (dict): 用户信息，用于日志记录
            
        Returns:
            tuple: (success, data, status_code)
        """
        start_time = time.time()
        
        try:
            # 获取配置
            config = cls.get_messages_config()
            
            current_app.logger.info(f"[消息历史转发] 用户: {user_info.get('username')} - 参数: {query_params}")
            
            # 发送GET请求到Dify API
            response = requests.get(
                config['api_url'],
                params=query_params,
                headers=config['headers'],
                timeout=30
            )
            
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            
            if response.ok:
                response_data = response.json()
                current_app.logger.info(
                    f"[消息历史转发成功] 用户: {user_info.get('username')} - "
                    f"返回条数: {len(response_data.get('data', []))} - 耗时: {elapsed_time}ms"
                )
                return True, response_data, 200
            else:
                error_msg = f"Dify API返回错误: {response.status_code}"
                current_app.logger.error(
                    f"[消息历史转发失败] 用户: {user_info.get('username')} - "
                    f"状态码: {response.status_code} - 耗时: {elapsed_time}ms"
                )
                try:
                    error_detail = response.json()
                    return False, error_detail, response.status_code
                except:
                    return False, {'error': error_msg}, response.status_code
                    
        except requests.RequestException as e:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.error(
                f"[消息历史转发网络错误] 用户: {user_info.get('username')} - "
                f"错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True
            )
            return False, {'error': f'网络请求失败: {str(e)}'}, 500
            
        except Exception as e:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.error(
                f"[消息历史转发系统错误] 用户: {user_info.get('username')} - "
                f"错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True
            )
            return False, {'error': f'系统错误: {str(e)}'}, 500
    
    @classmethod
    def validate_messages_query_params(cls, params):
        """
        验证消息历史查询参数
        
        Args:
            params (dict): 查询参数
            
        Returns:
            tuple: (is_valid, errors, cleaned_params)
        """
        errors = []
        cleaned_params = {}
        
        # 必需参数：user
        user = params.get('user', '').strip()
        if not user:
            errors.append('缺少必需参数: user')
        else:
            cleaned_params['user'] = user
        
        # 可选参数：conversation_id
        conversation_id = params.get('conversation_id', '').strip()
        if conversation_id:
            cleaned_params['conversation_id'] = conversation_id
        
        # 可选参数：first_id（用于分页）
        first_id = params.get('first_id', '').strip()
        if first_id:
            cleaned_params['first_id'] = first_id
        
        # 可选参数：limit（默认20，最大100）
        limit = params.get('limit', '20')
        try:
            limit = int(limit)
            if limit <= 0:
                limit = 20
            elif limit > 100:
                limit = 100
            cleaned_params['limit'] = limit
        except (ValueError, TypeError):
            cleaned_params['limit'] = 20
        
        is_valid = len(errors) == 0
        return is_valid, errors, cleaned_params
    
    @classmethod
    def get_config_status(cls):
        """获取会话API配置状态"""
        conversations_config = cls.get_conversations_config()
        messages_config = cls.get_messages_config()
        
        return {
            'conversations': {
                'api_url': conversations_config['api_url'],
                'api_key_masked': f"{conversations_config['api_key'][:8]}...{conversations_config['api_key'][-4:]}" if conversations_config['api_key'] else None,
                'is_configured': bool(conversations_config['api_url'] and conversations_config['api_key'])
            },
            'messages': {
                'api_url': messages_config['api_url'],
                'api_key_masked': f"{messages_config['api_key'][:8]}...{messages_config['api_key'][-4:]}" if messages_config['api_key'] else None,
                'is_configured': bool(messages_config['api_url'] and messages_config['api_key'])
            }
        } 