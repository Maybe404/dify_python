#!/usr/bin/env python3
"""
验证standard_review配置脚本
检查新添加的标准审查任务类型的配置是否完整
使用方法: python scripts/verify_standard_review_config.py
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.standard_config_service import StandardConfigService
from app.models.task import Task

def verify_standard_review_config():
    """验证standard_review配置"""
    print("=" * 50)
    print("验证标准审查(standard_review)配置")
    print("=" * 50)
    
    success = True
    
    # 1. 检查StandardConfigService中的配置
    print("\n1. 检查StandardConfigService配置...")
    try:
        if 'standard_review' in StandardConfigService.STANDARD_TYPE_CONFIG:
            config = StandardConfigService.STANDARD_TYPE_CONFIG['standard_review']
            print(f"   ✅ 配置存在: {config['name']}")
            print(f"   - URL环境变量: {config['url_env']}")
            print(f"   - Key环境变量: {config['key_env']}")
        else:
            print("   ❌ 配置不存在")
            success = False
    except Exception as e:
        print(f"   ❌ 检查失败: {str(e)}")
        success = False
    
    # 2. 检查环境变量
    print("\n2. 检查环境变量...")
    url_var = 'DIFY_STANDARD_REVIEW_URL'
    key_var = 'DIFY_STANDARD_REVIEW_KEY'
    
    url_value = os.getenv(url_var)
    key_value = os.getenv(key_var)
    
    if url_value:
        print(f"   ✅ {url_var}: {url_value}")
    else:
        print(f"   ⚠️  {url_var}: 未设置（将使用默认值）")
    
    if key_value:
        print(f"   ✅ {key_var}: {key_value[:10]}...")
    else:
        print(f"   ⚠️  {key_var}: 未设置（将使用默认值）")
    
    # 3. 检查Task模型的枚举
    print("\n3. 检查Task模型枚举...")
    try:
        task_types = Task.get_task_type_choices()
        review_exists = any(choice[0] == 'standard_review' for choice in task_types)
        
        if review_exists:
            print("   ✅ Task模型包含standard_review类型")
            for choice in task_types:
                if choice[0] == 'standard_review':
                    print(f"   - {choice[0]}: {choice[1]}")
        else:
            print("   ❌ Task模型缺少standard_review类型")
            success = False
    except Exception as e:
        print(f"   ❌ 检查失败: {str(e)}")
        success = False
    
    # 4. 测试配置服务方法
    print("\n4. 测试配置服务方法...")
    try:
        # 测试验证方法
        is_valid = StandardConfigService.validate_standard_type('standard_review')
        if is_valid:
            print("   ✅ validate_standard_type('standard_review'): True")
        else:
            print("   ❌ validate_standard_type('standard_review'): False")
            success = False
        
        # 测试获取所有类型
        all_types = StandardConfigService.get_all_standard_types()
        review_in_list = any(t['key'] == 'standard_review' for t in all_types)
        
        if review_in_list:
            print("   ✅ get_all_standard_types()包含standard_review")
            for t in all_types:
                if t['key'] == 'standard_review':
                    print(f"   - {t['key']}: {t['name']} - {t['description']}")
        else:
            print("   ❌ get_all_standard_types()缺少standard_review")
            success = False
        
        # 测试获取配置（需要应用上下文）
        try:
            # 创建一个临时的Flask应用上下文
            from app import create_app
            app = create_app()
            with app.app_context():
                config = StandardConfigService.get_config_for_standard_type('standard_review')
                print(f"   ✅ get_config_for_standard_type('standard_review'):")
                print(f"   - 名称: {config['name']}")
                print(f"   - API URL: {config['api_url']}")
                print(f"   - API Key: {config['api_key'][:10]}...")
                print(f"   - 文件上传URL: {config['file_upload_url']}")
        except Exception as e:
            print(f"   ⚠️  get_config_for_standard_type测试跳过: {str(e)}")
        
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        success = False
    
    # 5. 检查配置状态
    print("\n5. 检查整体配置状态...")
    try:
        status = StandardConfigService.get_config_status()
        print(f"   - 总类型数: {status['total_types']}")
        print(f"   - 已配置类型数: {status['configured_types']}")
        
        if status['incomplete_configs']:
            print(f"   ⚠️  未完整配置的类型: {', '.join(status['incomplete_configs'])}")
        
        # 查找standard_review的详细状态
        for detail in status['type_details']:
            if detail['standard_type'] == 'standard_review':
                print(f"   - standard_review状态:")
                print(f"     * 已配置: {'✅' if detail['is_configured'] else '❌'}")
                print(f"     * API URL: {detail['api_url'] or '未设置'}")
                print(f"     * 有API Key: {'✅' if detail['has_api_key'] else '❌'}")
                break
        
    except Exception as e:
        print(f"   ❌ 检查失败: {str(e)}")
        success = False
    
    # 总结
    print("\n" + "=" * 50)
    if success:
        print("🎉 验证完成！standard_review配置正确")
        print("\n下一步：")
        print("1. 运行数据库迁移脚本: python scripts/add_standard_review_migration.py")
        print("2. 在.env文件中设置具体的API Key值")
        print("3. 重启应用以加载新配置")
    else:
        print("❌ 验证失败！请检查上述错误并修正")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    verify_standard_review_config() 