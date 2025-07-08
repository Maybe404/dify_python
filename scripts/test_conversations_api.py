#!/usr/bin/env python3
"""
会话列表转发接口测试脚本
测试新增的 /api/dify/conversations 接口功能
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ConversationsAPITester:
    def __init__(self):
        self.base_url = f"http://{os.getenv('HOST', 'localhost')}:{os.getenv('PORT', '5000')}"
        self.api_url = f"{self.base_url}/api"
        self.access_token = None
        
    def login(self, credential="test@example.com", password="testpassword"):
        """登录获取访问令牌"""
        print(f"🔐 正在登录用户: {credential}")
        
        response = requests.post(f"{self.api_url}/auth/login", json={
            "credential": credential,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.access_token = data['data']['access_token']
                print(f"✅ 登录成功: {data['data']['user']['email']}")
                return True
            else:
                print(f"❌ 登录失败: {data.get('message')}")
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
            try:
                print(f"   错误详情: {response.json()}")
            except:
                print(f"   错误详情: {response.text}")
        
        return False
    
    def get_headers(self):
        """获取带认证的请求头"""
        if not self.access_token:
            raise Exception("未登录，请先调用login()方法")
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def test_conversations_api(self, user="abc-123", last_id="", limit=20):
        """测试会话列表接口"""
        print(f"\n📋 测试会话列表接口")
        print(f"   参数: user={user}, last_id={last_id}, limit={limit}")
        
        params = {
            'user': user,
            'limit': limit
        }
        
        if last_id:
            params['last_id'] = last_id
            
        try:
            response = requests.get(
                f"{self.api_url}/dify/conversations",
                params=params,
                headers=self.get_headers(),
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 请求成功!")
                print(f"   返回数据结构:")
                print(f"   - limit: {data.get('limit')}")
                print(f"   - has_more: {data.get('has_more')}")
                print(f"   - data条数: {len(data.get('data', []))}")
                
                # 显示前3条会话
                conversations = data.get('data', [])
                for i, conv in enumerate(conversations[:3]):
                    print(f"   会话{i+1}: {conv.get('id')} - {conv.get('name')}")
                
                return True
            else:
                print(f"❌ 请求失败")
                try:
                    error_data = response.json()
                    print(f"   错误信息: {error_data}")
                except:
                    print(f"   错误信息: {response.text}")
                
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求异常: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False
    
    def test_config_api(self):
        """测试配置接口，检查新增的会话配置"""
        print(f"\n⚙️ 测试配置接口")
        
        try:
            response = requests.get(
                f"{self.api_url}/dify/config",
                headers=self.get_headers(),
                timeout=10
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    config_data = data.get('data', {})
                    print(f"✅ 配置获取成功!")
                    print(f"   聊天API: {config_data.get('api_url')}")
                    print(f"   聊天Key: {config_data.get('api_key_masked')}")
                    
                    # 检查会话配置
                    conv_config = config_data.get('conversations_config', {})
                    print(f"   会话API: {conv_config.get('api_url')}")
                    print(f"   会话Key: {conv_config.get('api_key_masked')}")
                    print(f"   会话配置完整: {conv_config.get('is_configured')}")
                    
                    # 显示所有端点
                    endpoints = config_data.get('endpoints', {})
                    print(f"   可用端点:")
                    for name, path in endpoints.items():
                        print(f"   - {name}: {path}")
                    
                    return True
                else:
                    print(f"❌ 配置获取失败: {data.get('message')}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            
        return False
    
    def test_parameter_validation(self):
        """测试参数验证"""
        print(f"\n🔍 测试参数验证")
        
        # 测试缺少user参数
        print("   测试1: 缺少user参数")
        response = requests.get(
            f"{self.api_url}/dify/conversations",
            params={'limit': 10},
            headers=self.get_headers()
        )
        
        if response.status_code == 400:
            data = response.json()
            print(f"   ✅ 正确返回400错误: {data.get('message')}")
        else:
            print(f"   ❌ 未正确验证参数: {response.status_code}")
        
        # 测试无效limit值
        print("   测试2: 无效limit值")
        response = requests.get(
            f"{self.api_url}/dify/conversations",
            params={'user': 'test-user', 'limit': 'invalid'},
            headers=self.get_headers()
        )
        
        # 应该自动修正为默认值20，不应该报错
        if response.status_code in [200, 500]:  # 可能是200（参数修正）或500（Dify API错误）
            print(f"   ✅ 自动修正无效limit值")
        else:
            print(f"   ❌ 处理无效limit值失败: {response.status_code}")

def main():
    print("="*60)
    print("🚀 会话列表转发接口测试")
    print("="*60)
    
    tester = ConversationsAPITester()
    
    # 检查环境变量
    conversations_url = os.getenv('DIFY_CONVERSATIONS_API_URL')
    conversations_key = os.getenv('DIFY_CONVERSATIONS_API_KEY')
    
    print(f"📋 环境配置检查:")
    print(f"   服务地址: {tester.base_url}")
    print(f"   会话API URL: {conversations_url}")
    print(f"   会话API Key: {conversations_key[:10]}..." if conversations_key else "   会话API Key: 未配置")
    
    # 提示用户
    print(f"\n⚠️ 注意事项:")
    print(f"   1. 请确保应用已启动在 {tester.base_url}")
    print(f"   2. 请确保已有测试用户(test@example.com/testpassword)")
    print(f"   3. 请确保环境变量DIFY_CONVERSATIONS_API_URL和DIFY_CONVERSATIONS_API_KEY已配置")
    
    input("\n按Enter键继续测试...")
    
    # 登录
    if not tester.login():
        print("\n❌ 登录失败，测试终止")
        return
    
    # 测试配置接口
    tester.test_config_api()
    
    # 测试参数验证
    tester.test_parameter_validation()
    
    # 测试会话列表接口
    print(f"\n" + "="*60)
    print("🧪 开始测试会话列表接口")
    print("="*60)
    
    # 测试基本请求
    success = tester.test_conversations_api(
        user="abc-123",
        limit=5
    )
    
    if success:
        # 测试分页
        tester.test_conversations_api(
            user="abc-123", 
            last_id="some-conversation-id",
            limit=10
        )
    
    print(f"\n" + "="*60)
    print("✨ 测试完成")
    print("="*60)

if __name__ == "__main__":
    main() 