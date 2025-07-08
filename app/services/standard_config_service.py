import os
from flask import current_app

class StandardConfigService:
    """标准处理配置服务 - 管理六种标准处理类型的API配置"""
    
    # 标准处理类型配置映射
    STANDARD_TYPE_CONFIG = {
        'standard_interpretation': {
            'name': '标准解读',
            'url_env': 'DIFY_STANDARD_INTERPRETATION_URL',
            'key_env': 'DIFY_STANDARD_INTERPRETATION_KEY',
            'default_url': 'http://10.100.100.93/v1/chat-messages',
            'default_key': 'app-interpretation-key'
        },
        'standard_recommendation': {
            'name': '标准推荐',
            'url_env': 'DIFY_STANDARD_RECOMMENDATION_URL',
            'key_env': 'DIFY_STANDARD_RECOMMENDATION_KEY',
            'default_url': 'http://10.100.100.93/v1/chat-messages',
            'default_key': 'app-recommendation-key'
        },
        'standard_comparison': {
            'name': '标准对比',
            'url_env': 'DIFY_STANDARD_COMPARISON_URL',
            'key_env': 'DIFY_STANDARD_COMPARISON_KEY',
            'default_url': 'http://10.100.100.93/v1/chat-messages',
            'default_key': 'app-comparison-key'
        },
        'standard_international': {
            'name': '标准国际化辅助',
            'url_env': 'DIFY_STANDARD_INTERNATIONAL_URL',
            'key_env': 'DIFY_STANDARD_INTERNATIONAL_KEY',
            'default_url': 'http://10.100.100.93/v1/chat-messages',
            'default_key': 'app-international-key'
        },
        'standard_compliance': {
            'name': '标准符合性检查',
            'url_env': 'DIFY_STANDARD_COMPLIANCE_URL',
            'key_env': 'DIFY_STANDARD_COMPLIANCE_KEY',
            'default_url': 'http://10.100.100.93/v1/chat-messages',
            'default_key': 'app-compliance-key'
        },
        'standard_review': {
            'name': '标准审查',
            'url_env': 'DIFY_STANDARD_REVIEW_URL',
            'key_env': 'DIFY_STANDARD_REVIEW_KEY',
            'default_url': 'http://10.100.100.93/v1/chat-messages',
            'default_key': 'app-review-key'
        }
    }
    
    @classmethod
    def get_config_for_standard_type(cls, standard_type):
        """根据标准处理类型获取对应的Dify配置"""
        if standard_type not in cls.STANDARD_TYPE_CONFIG:
            current_app.logger.error(f"未知的标准处理类型: {standard_type}")
            raise ValueError(f"不支持的标准处理类型: {standard_type}")
        
        config = cls.STANDARD_TYPE_CONFIG[standard_type]
        
        api_url = os.getenv(config['url_env'], config['default_url'])
        api_key = os.getenv(config['key_env'], config['default_key'])
        
        current_app.logger.info(f"获取{config['name']}配置 - URL: {api_url[:50]}... - Key: {api_key[:10]}...")
        
        # 使用统一的文件上传URL配置
        file_upload_config = cls.get_file_upload_config()
        file_upload_url = file_upload_config['upload_url']
        
        return {
            'name': config['name'],
            'api_url': api_url,
            'api_key': api_key,
            'file_upload_url': file_upload_url,
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        }
    
    @classmethod
    def get_file_upload_config(cls):
        """获取文件上传配置"""
        upload_url = os.getenv('DIFY_FILE_UPLOAD_URL', 'http://10.100.100.93/v1/files/upload')
        
        return {
            'upload_url': upload_url
        }
    
    @classmethod
    def validate_standard_type(cls, standard_type):
        """验证标准处理类型是否有效"""
        return standard_type in cls.STANDARD_TYPE_CONFIG
    
    @classmethod
    def get_all_standard_types(cls):
        """获取所有支持的标准处理类型"""
        return [
            {
                'key': standard_type,
                'name': config['name'],
                'description': f'{config["name"]}服务'
            }
            for standard_type, config in cls.STANDARD_TYPE_CONFIG.items()
        ]
    
    @classmethod
    def check_config_completeness(cls):
        """检查所有标准处理类型的配置是否完整"""
        incomplete_configs = []
        
        for standard_type, config in cls.STANDARD_TYPE_CONFIG.items():
            api_url = os.getenv(config['url_env'])
            api_key = os.getenv(config['key_env'])
            
            if not api_url or not api_key:
                incomplete_configs.append({
                    'standard_type': standard_type,
                    'name': config['name'],
                    'missing_url': not api_url,
                    'missing_key': not api_key
                })
        
        return incomplete_configs
    
    @classmethod
    def get_config_status(cls):
        """获取所有配置的状态信息"""
        status_info = {
            'total_types': len(cls.STANDARD_TYPE_CONFIG),
            'configured_types': 0,
            'incomplete_configs': [],
            'type_details': []
        }
        
        for standard_type, config in cls.STANDARD_TYPE_CONFIG.items():
            api_url = os.getenv(config['url_env'])
            api_key = os.getenv(config['key_env'])
            
            is_configured = bool(api_url and api_key)
            
            if is_configured:
                status_info['configured_types'] += 1
            else:
                status_info['incomplete_configs'].append(standard_type)
            
            status_info['type_details'].append({
                'standard_type': standard_type,
                'name': config['name'],
                'is_configured': is_configured,
                'api_url': api_url[:50] + '...' if api_url else None,
                'has_api_key': bool(api_key)
            })
        
        return status_info 