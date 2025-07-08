import os
import requests
import time
from flask import current_app
from app.config.config import Config

class DifyAppService:
    """Dify应用场景服务 - 管理不同页面的API配置"""
    
    # 应用场景配置映射
    APP_SCENARIOS = {
        'multilingual_qa': {
            'name': '多语言问答',
            'description': '多语言问答页面专用配置',
            'chat_url_env': 'DIFY_MULTILINGUAL_CHAT_URL',
            'chat_key_env': 'DIFY_MULTILINGUAL_CHAT_KEY',
            'conversations_url_env': 'DIFY_MULTILINGUAL_CONVERSATIONS_URL',
            'conversations_key_env': 'DIFY_MULTILINGUAL_CONVERSATIONS_KEY',
            'messages_url_env': 'DIFY_MULTILINGUAL_MESSAGES_URL',
            'messages_key_env': 'DIFY_MULTILINGUAL_MESSAGES_KEY',
            # 会话操作使用相同的conversations配置
            'conversation_ops_url_env': 'DIFY_MULTILINGUAL_CONVERSATIONS_URL',
            'conversation_ops_key_env': 'DIFY_MULTILINGUAL_CONVERSATIONS_KEY',
            # 默认值 (向后兼容)
            'default_chat_url': 'http://10.100.100.93/v1/chat-messages',
            'default_chat_key': 'app-rNTm2hs2XdVDFHBrHekqhjfn',
            'default_conversations_url': 'http://10.100.100.93/v1/conversations',
            'default_conversations_key': 'app-rNTm2hs2XdVDFHBrHekqhjfn',
            'default_messages_url': 'http://10.100.100.93/v1/messages',
            'default_messages_key': 'app-rNTm2hs2XdVDFHBrHekqhjfn',
            'default_conversation_ops_url': 'http://10.100.100.93/v1/conversations',
            'default_conversation_ops_key': 'app-rNTm2hs2XdVDFHBrHekqhjfn'
        },
        'standard_query': {
            'name': '标准查询',
            'description': '标准查询页面专用配置',
            'chat_url_env': 'DIFY_STANDARD_QUERY_CHAT_URL',
            'chat_key_env': 'DIFY_STANDARD_QUERY_CHAT_KEY',
            'conversations_url_env': 'DIFY_STANDARD_QUERY_CONVERSATIONS_URL',
            'conversations_key_env': 'DIFY_STANDARD_QUERY_CONVERSATIONS_KEY',
            'messages_url_env': 'DIFY_STANDARD_QUERY_MESSAGES_URL',
            'messages_key_env': 'DIFY_STANDARD_QUERY_MESSAGES_KEY',
            # 会话操作使用相同的conversations配置
            'conversation_ops_url_env': 'DIFY_STANDARD_QUERY_CONVERSATIONS_URL',
            'conversation_ops_key_env': 'DIFY_STANDARD_QUERY_CONVERSATIONS_KEY',
            # 标准查询的默认配置
            'default_chat_url': 'http://10.100.100.93/v1/chat-messages',
            'default_chat_key': 'app-eAQPcdggI62ZJpMKJxuLK7y3',
            'default_conversations_url': 'http://10.100.100.93/v1/conversations',
            'default_conversations_key': 'app-eAQPcdggI62ZJpMKJxuLK7y3',
            'default_messages_url': 'http://10.100.100.93/v1/messages',
            'default_messages_key': 'app-eAQPcdggI62ZJpMKJxuLK7y3',
            'default_conversation_ops_url': 'http://10.100.100.93/v1/conversations',
            'default_conversation_ops_key': 'app-eAQPcdggI62ZJpMKJxuLK7y3'
        }
    }
    
    @classmethod
    def get_app_config(cls, scenario, api_type):
        """
        获取指定应用场景的API配置
        
        Args:
            scenario (str): 应用场景 ('multilingual_qa' 或 'standard_query')
            api_type (str): API类型 ('chat', 'conversations', 'messages')
            
        Returns:
            dict: API配置信息
        """
        if scenario not in cls.APP_SCENARIOS:
            error_msg = f"未知的应用场景: {scenario}，支持的场景: {list(cls.APP_SCENARIOS.keys())}"
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)
        
        if api_type not in ['chat', 'conversations', 'messages', 'conversation_ops']:
            error_msg = f"未知的API类型: {api_type}，支持的类型: ['chat', 'conversations', 'messages', 'conversation_ops']"
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)
        
        scenario_config = cls.APP_SCENARIOS[scenario]
        
        # 获取对应的环境变量和默认值
        url_env_key = scenario_config[f'{api_type}_url_env']
        key_env_key = scenario_config[f'{api_type}_key_env']
        default_url = scenario_config[f'default_{api_type}_url']
        default_key = scenario_config[f'default_{api_type}_key']
        
        api_url = os.getenv(url_env_key, default_url)
        api_key = os.getenv(key_env_key, default_key)
        
        # 验证配置是否有效
        if not api_url or not api_key:
            error_msg = f"场景 {scenario} 的 {api_type} API配置不完整: URL={api_url}, Key={'已设置' if api_key else '未设置'}"
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)
        
        current_app.logger.info(
            f"获取{scenario_config['name']}-{api_type}配置 - "
            f"URL: {api_url} - Key: {api_key[:10]}***{api_key[-5:] if len(api_key) > 15 else api_key}"
        )
        
        return {
            'scenario': scenario,
            'api_type': api_type,
            'name': scenario_config['name'],
            'api_url': api_url,
            'api_key': api_key,
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        }
    
    @classmethod
    def forward_request(cls, scenario, api_type, request_method='GET', 
                       query_params=None, json_data=None, user_info=None, stream=False):
        """
        通用的Dify API请求转发方法
        
        Args:
            scenario (str): 应用场景
            api_type (str): API类型
            request_method (str): 请求方法 ('GET', 'POST')
            query_params (dict): 查询参数
            json_data (dict): JSON数据
            user_info (dict): 用户信息
            stream (bool): 是否流式响应
            
        Returns:
            tuple: (success, data_or_response, status_code)
        """
        start_time = time.time()
        
        try:
            # 获取配置
            config = cls.get_app_config(scenario, api_type)
            
            user_name = user_info.get('username', 'unknown') if user_info else 'system'
            current_app.logger.info(
                f"[{config['name']}-{api_type}转发] 用户: {user_name} - "
                f"方法: {request_method} - URL: {config['api_url']}"
            )
            
            # 构建请求
            kwargs = {
                'headers': config['headers'],
                'timeout': 60  # 增加超时时间
            }
            
            if request_method.upper() == 'GET':
                if query_params:
                    kwargs['params'] = query_params
                    current_app.logger.debug(f"GET参数: {query_params}")
                response = requests.get(config['api_url'], **kwargs)
            elif request_method.upper() == 'POST':
                if json_data:
                    kwargs['json'] = json_data
                    current_app.logger.debug(f"POST数据: {json_data}")
                if stream:
                    kwargs['stream'] = True
                response = requests.post(config['api_url'], **kwargs)
            elif request_method.upper() == 'PATCH':
                if json_data:
                    kwargs['json'] = json_data
                    current_app.logger.debug(f"PATCH数据: {json_data}")
                response = requests.patch(config['api_url'], **kwargs)
            elif request_method.upper() == 'DELETE':
                if query_params:
                    kwargs['params'] = query_params
                    current_app.logger.debug(f"DELETE参数: {query_params}")
                response = requests.delete(config['api_url'], **kwargs)
            else:
                raise ValueError(f"不支持的请求方法: {request_method}")
            
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            
            current_app.logger.info(
                f"[{config['name']}-{api_type}响应] 状态码: {response.status_code} - 耗时: {elapsed_time}ms"
            )
            
            if stream:
                # 流式响应直接返回response对象
                if response.ok:
                    current_app.logger.info(
                        f"[{config['name']}-{api_type}流式开始] 用户: {user_name} - 耗时: {elapsed_time}ms"
                    )
                    return True, response, 200
                else:
                    current_app.logger.error(
                        f"[{config['name']}-{api_type}流式失败] 状态码: {response.status_code} - 响应: {response.text[:200]}"
                    )
                    try:
                        error_detail = response.json()
                        return False, error_detail, response.status_code
                    except:
                        return False, {'error': f'API返回错误: {response.status_code}', 'detail': response.text[:200]}, response.status_code
            
            if response.ok:
                response_data = response.json()
                data_count = len(response_data.get('data', [])) if isinstance(response_data.get('data'), list) else 'N/A'
                current_app.logger.info(
                    f"[{config['name']}-{api_type}成功] 用户: {user_name} - "
                    f"返回条数: {data_count} - 耗时: {elapsed_time}ms"
                )
                return True, response_data, 200
            else:
                current_app.logger.error(
                    f"[{config['name']}-{api_type}失败] 用户: {user_name} - "
                    f"状态码: {response.status_code} - 响应: {response.text[:200]} - 耗时: {elapsed_time}ms"
                )
                try:
                    error_detail = response.json()
                    return False, error_detail, response.status_code
                except:
                    return False, {'error': f'API返回错误: {response.status_code}', 'detail': response.text[:200]}, response.status_code
                    
        except requests.RequestException as e:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.error(
                f"[{config['name']}-{api_type}网络错误] 用户: {user_name if 'user_name' in locals() else 'unknown'} - "
                f"错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True
            )
            return False, {'error': f'网络请求失败: {str(e)}'}, 500
            
        except Exception as e:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.error(
                f"[{config['name'] if 'config' in locals() else scenario}-{api_type}系统错误] 用户: {user_name if 'user_name' in locals() else 'unknown'} - "
                f"错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True
            )
            return False, {'error': f'系统错误: {str(e)}'}, 500
    
    @classmethod
    def get_all_scenarios(cls):
        """获取所有支持的应用场景"""
        return [
            {
                'key': scenario,
                'name': config['name'],
                'description': config['description']
            }
            for scenario, config in cls.APP_SCENARIOS.items()
        ]
    
    @classmethod
    def get_scenario_status(cls, scenario):
        """获取指定场景的配置状态"""
        if scenario not in cls.APP_SCENARIOS:
            return None
        
        scenario_config = cls.APP_SCENARIOS[scenario]
        status = {
            'scenario': scenario,
            'name': scenario_config['name'],
            'apis': {}
        }
        
        for api_type in ['chat', 'conversations', 'messages', 'conversation_ops']:
            try:
                config = cls.get_app_config(scenario, api_type)
                status['apis'][api_type] = {
                    'api_url': config['api_url'],
                    'api_key_masked': f"{config['api_key'][:8]}...{config['api_key'][-4:]}" if config['api_key'] else None,
                    'is_configured': bool(config['api_url'] and config['api_key'])
                }
            except Exception as e:
                status['apis'][api_type] = {
                    'error': str(e),
                    'is_configured': False
                }
        
        return status
    
    @classmethod
    def validate_scenario_params(cls, scenario, api_type, params):
        """
        验证API参数
        
        Args:
            scenario (str): 应用场景
            api_type (str): API类型
            params (dict): 参数
            
        Returns:
            tuple: (is_valid, errors, cleaned_params)
        """
        errors = []
        cleaned_params = {}
        
        if api_type in ['conversations', 'messages']:
            # user参数验证
            user = params.get('user', '').strip()
            if not user:
                errors.append('缺少必需参数: user')
            else:
                cleaned_params['user'] = user
            
            # limit参数验证
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
        
        if api_type == 'conversations':
            # last_id参数验证
            last_id = params.get('last_id', '').strip()
            if last_id:
                cleaned_params['last_id'] = last_id
        
        elif api_type == 'messages':
            # conversation_id参数验证
            conversation_id = params.get('conversation_id', '').strip()
            if conversation_id:
                cleaned_params['conversation_id'] = conversation_id
            
            # first_id参数验证
            first_id = params.get('first_id', '').strip()
            if first_id:
                cleaned_params['first_id'] = first_id
        
        is_valid = len(errors) == 0
        return is_valid, errors, cleaned_params 