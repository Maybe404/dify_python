#!/usr/bin/env python3
"""
测试删除会话接口的响应格式转换
验证Dify的原始响应是否正确转换为系统统一格式
"""

import requests
import json

# 测试配置
BASE_URL = "http://localhost:5000/api"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

def get_auth_token():
    """获取认证令牌"""
    login_url = f"{BASE_URL}/auth/login"
    data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('access_token')
                print(f"✅ 登录成功，获取token: {token[:20]}...")
                return token
            else:
                print(f"❌ 登录失败: {result.get('message')}")
                return None
        else:
            print(f"❌ 登录请求失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return None

def test_delete_response(token):
    """测试删除会话接口的响应"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n" + "="*60)
    print("测试删除会话接口响应格式转换")
    print("="*60)
    
    # 测试场景
    scenarios = ['multilingual_qa', 'standard_query']
    test_conversation_id = "472326ac-b441-4372-8eeb-da9d277b31e1"
    
    for scenario in scenarios:
        print(f"\n🔍 测试场景: {scenario}")
        print("-" * 40)
        
        delete_url = f"{BASE_URL}/dify/v2/{scenario}/conversations/{test_conversation_id}"
        print(f"URL: DELETE {delete_url}")
        
        delete_data = {
            "user": "test-user-123"
        }
        
        try:
            response = requests.delete(delete_url, json=delete_data, headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应头Content-Type: {response.headers.get('content-type', '未设置')}")
            print(f"响应长度: {len(response.text)} 字符")
            
            if response.status_code in [200, 204]:
                print("✅ 删除请求状态正常")
                
                # 尝试解析响应
                try:
                    response_data = response.json()
                    print(f"✅ 响应JSON解析成功:")
                    print(f"   {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                    
                    # 检查是否包含期望的字段
                    if response_data.get('success') == 'true' and response_data.get('message') == '删除成功':
                        print("✅ 响应包含期望的统一格式: success='true', message='删除成功'")
                    elif response_data.get('result') == 'success':
                        print("⚠️  响应是Dify原始格式，应该已转换为统一格式")
                    else:
                        print(f"⚠️  响应内容与期望不符: {response_data}")
                        
                except Exception as e:
                    print(f"❌ JSON解析失败: {str(e)}")
                    print(f"   原始响应文本: '{response.text}'")
                    
            elif response.status_code == 404:
                print("⚠️  会话不存在（这是正常的，因为使用的是测试ID）")
                try:
                    error_data = response.json()
                    print(f"   错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                except:
                    print(f"   错误响应: {response.text}")
                    
            else:
                print(f"❌ 删除请求失败")
                try:
                    error_data = response.json()
                    print(f"   错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                except:
                    print(f"   错误响应: {response.text}")
                    
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")

def main():
    """主函数"""
    print("="*60)
    print("删除会话响应格式转换测试工具")
    print("="*60)
    
    # 获取认证令牌
    token = get_auth_token()
    if not token:
        print("❌ 无法获取认证令牌，测试终止")
        return
    
    # 测试删除响应
    test_delete_response(token)
    
    print(f"\n" + "="*60)
    print("测试完成")
    print("="*60)
    print("\n说明:")
    print("- 如果返回404是正常的，因为测试的会话ID可能不存在")
    print("- 重点关注成功删除时是否返回了统一的响应格式:")
    print("  期望: {\"success\": \"true\", \"message\": \"删除成功\"}")
    print("- 修复后应该看到响应格式转换的详细日志信息")

if __name__ == "__main__":
    main() 