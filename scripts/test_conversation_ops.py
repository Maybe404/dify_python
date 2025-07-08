#!/usr/bin/env python3
"""
测试会话操作接口（重命名和删除）
"""

import requests
import json
import sys
import os

# 测试配置
BASE_URL = "http://localhost:5000/api"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

# 测试场景
SCENARIOS = ['multilingual_qa', 'standard_query']

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

def test_conversation_ops(token):
    """测试会话操作接口"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n" + "="*60)
    print("开始测试会话操作接口")
    print("="*60)
    
    for scenario in SCENARIOS:
        print(f"\n🔍 测试场景: {scenario}")
        print("-" * 40)
        
        # 测试会话重命名接口
        test_conversation_id = "test_conversation_123"
        rename_url = f"{BASE_URL}/dify/v2/{scenario}/conversations/{test_conversation_id}/name"
        
        print(f"\n1. 测试会话重命名接口:")
        print(f"   URL: POST {rename_url}")
        
        rename_data = {
            "name": "新的会话名称",
            "auto_generate": True,
            "user": "test-user-123"
        }
        
        try:
            response = requests.post(rename_url, json=rename_data, headers=headers)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ 重命名接口响应正常")
                try:
                    result = response.json()
                    print(f"   响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
                except:
                    print(f"   响应内容: {response.text[:200]}")
            else:
                print(f"   ❌ 重命名接口失败")
                try:
                    error = response.json()
                    print(f"   错误信息: {json.dumps(error, ensure_ascii=False, indent=2)}")
                except:
                    print(f"   错误内容: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ 重命名接口异常: {str(e)}")
        
        # 测试会话删除接口
        delete_url = f"{BASE_URL}/dify/v2/{scenario}/conversations/{test_conversation_id}"
        
        print(f"\n2. 测试会话删除接口:")
        print(f"   URL: DELETE {delete_url}")
        
        delete_data = {
            "user": "test-user-123"
        }
        
        try:
            response = requests.delete(delete_url, json=delete_data, headers=headers)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code in [200, 204]:
                print("   ✅ 删除接口响应正常")
                try:
                    result = response.json()
                    print(f"   响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
                except:
                    print(f"   响应内容: {response.text[:200] if response.text else '空响应'}")
            else:
                print(f"   ❌ 删除接口失败")
                try:
                    error = response.json()
                    print(f"   错误信息: {json.dumps(error, ensure_ascii=False, indent=2)}")
                except:
                    print(f"   错误内容: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ 删除接口异常: {str(e)}")

def test_endpoint_list(token):
    """测试端点列表是否包含新接口"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n" + "="*60)
    print("检查端点配置")
    print("="*60)
    
    for scenario in SCENARIOS:
        print(f"\n🔍 检查场景配置: {scenario}")
        config_url = f"{BASE_URL}/dify/v2/{scenario}/config"
        
        try:
            response = requests.get(config_url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                endpoints = result.get('data', {}).get('endpoints', {})
                
                print("   可用端点:")
                for name, url in endpoints.items():
                    print(f"   - {name}: {url}")
                
                # 检查新端点是否存在
                if 'rename_conversation' in endpoints and 'delete_conversation' in endpoints:
                    print("   ✅ 新的会话操作端点已正确配置")
                else:
                    print("   ❌ 新的会话操作端点配置缺失")
                    
            else:
                print(f"   ❌ 获取配置失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 获取配置异常: {str(e)}")

def main():
    """主函数"""
    print("="*60)
    print("Dify会话操作接口测试工具")
    print("="*60)
    
    # 获取认证令牌
    token = get_auth_token()
    if not token:
        print("❌ 无法获取认证令牌，测试终止")
        sys.exit(1)
    
    # 测试会话操作接口
    test_conversation_ops(token)
    
    # 测试端点配置
    test_endpoint_list(token)
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
    print("\n注意:")
    print("- 这些接口实际调用Dify API，可能返回404或其他错误（正常现象）")
    print("- 重点关注接口是否正确路由和转发，而不是Dify的具体响应")
    print("- 如果状态码为401，请检查JWT token配置")
    print("- 如果状态码为500，请检查Dify API配置和网络连接")

if __name__ == "__main__":
    main() 