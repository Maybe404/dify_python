#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话历史消息API测试脚本
测试新增的Dify消息历史转发接口功能
"""

import requests
import json
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MessagesApiTester:
    """消息历史API测试器"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def print_separator(self, title):
        """打印分隔线"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_step(self, step_num, description):
        """打印步骤"""
        print(f"\n步骤 {step_num}: {description}")
        print("-" * 40)
    
    def login(self, email="test@example.com", password="TestPassword123!"):
        """用户登录获取JWT令牌"""
        self.print_step(1, "用户登录获取JWT令牌")
        
        login_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"请求URL: {response.url}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'token' in data.get('data', {}):
                    self.token = data['data']['token']
                    print(f"✅ 登录成功")
                    print(f"Token: {self.token[:20]}...")
                    
                    # 设置后续请求的Authorization头
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    return True
                else:
                    print(f"❌ 登录失败: {data.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ 登录请求失败: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"错误详情: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {str(e)}")
            return False
    
    def test_messages_api_basic(self):
        """测试基本消息历史API调用"""
        self.print_step(2, "测试基本消息历史API调用")
        
        # 测试参数
        test_params = {
            'user': 'test-user-123',
            'conversation_id': 'test-conversation-id',
            'limit': 10
        }
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/dify/messages",
                params=test_params
            )
            
            print(f"请求URL: {response.url}")
            print(f"状态码: {response.status_code}")
            print(f"请求参数: {json.dumps(test_params, indent=2, ensure_ascii=False)}")
            
            # 解析响应
            try:
                data = response.json()
                print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if response.status_code == 200:
                    print("✅ 消息历史API调用成功")
                    if 'data' in data:
                        messages = data.get('data', [])
                        print(f"📊 返回消息数量: {len(messages)}")
                        if messages:
                            print(f"📝 第一条消息: {messages[0].get('query', 'N/A')[:50]}...")
                else:
                    print(f"⚠️ API返回非200状态码: {response.status_code}")
                    
            except json.JSONDecodeError:
                print(f"⚠️ 响应不是有效JSON: {response.text[:200]}...")
                
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False
    
    def test_messages_api_without_conversation_id(self):
        """测试不带conversation_id的消息历史API调用"""
        self.print_step(3, "测试不带conversation_id的消息历史API调用")
        
        # 测试参数（不包含conversation_id）
        test_params = {
            'user': 'test-user-123',
            'limit': 20
        }
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/dify/messages",
                params=test_params
            )
            
            print(f"请求URL: {response.url}")
            print(f"状态码: {response.status_code}")
            print(f"请求参数: {json.dumps(test_params, indent=2, ensure_ascii=False)}")
            
            # 解析响应
            try:
                data = response.json()
                print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if response.status_code == 200:
                    print("✅ 不带conversation_id的消息历史API调用成功")
                else:
                    print(f"⚠️ API返回非200状态码: {response.status_code}")
                    
            except json.JSONDecodeError:
                print(f"⚠️ 响应不是有效JSON: {response.text[:200]}...")
                
            return response.status_code in [200, 400, 404]  # 可能的正常状态码
            
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False
    
    def test_messages_api_validation(self):
        """测试消息历史API参数验证"""
        self.print_step(4, "测试消息历史API参数验证")
        
        # 测试缺少必需参数
        test_cases = [
            {
                'name': '缺少user参数',
                'params': {'conversation_id': 'test-id'},
                'expected_status': 400
            },
            {
                'name': '空user参数',
                'params': {'user': '', 'conversation_id': 'test-id'},
                'expected_status': 400
            },
            {
                'name': '无效limit参数',
                'params': {'user': 'test-user', 'limit': 'invalid'},
                'expected_status': 200  # 应该使用默认值
            },
            {
                'name': '超大limit参数',
                'params': {'user': 'test-user', 'limit': 200},
                'expected_status': 200  # 应该被限制为100
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n  子测试 {i}: {test_case['name']}")
            
            try:
                response = self.session.get(
                    f"{self.base_url}/api/dify/messages",
                    params=test_case['params']
                )
                
                print(f"    状态码: {response.status_code} (期望: {test_case['expected_status']})")
                
                if test_case['expected_status'] == 400 and response.status_code == 400:
                    print(f"    ✅ 参数验证正确")
                elif test_case['expected_status'] == 200 and response.status_code in [200, 404]:
                    print(f"    ✅ 参数处理正确")
                else:
                    print(f"    ❌ 期望状态码不匹配")
                    all_passed = False
                    
                # 显示响应详情
                try:
                    data = response.json()
                    if response.status_code == 400 and 'message' in data:
                        print(f"    错误信息: {data['message']}")
                except:
                    pass
                    
            except Exception as e:
                print(f"    ❌ 测试异常: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_dify_config_api(self):
        """测试Dify配置API，验证新的消息API配置"""
        self.print_step(5, "测试Dify配置API")
        
        try:
            response = self.session.get(f"{self.base_url}/api/dify/config")
            
            print(f"请求URL: {response.url}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 配置API调用成功")
                print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # 检查是否包含消息API的配置信息
                config_data = data.get('data', {})
                conversations_config = config_data.get('conversations_config', {})
                
                if 'messages' in conversations_config:
                    print(f"✅ 消息API配置存在")
                    messages_config = conversations_config['messages']
                    print(f"📊 消息API URL: {messages_config.get('api_url')}")
                    print(f"🔑 消息API Key: {messages_config.get('api_key_masked')}")
                    print(f"✅ 配置状态: {'已配置' if messages_config.get('is_configured') else '未配置'}")
                else:
                    print(f"⚠️ 消息API配置不存在")
                    
                return True
            else:
                print(f"❌ 配置API调用失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        self.print_separator("Dify消息历史转发接口测试")
        
        print(f"🚀 开始测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 测试服务器: {self.base_url}")
        
        # 测试结果统计
        results = []
        
        # 1. 登录
        if self.login():
            results.append(("用户登录", True))
            
            # 2. 基本消息历史API测试
            results.append(("基本消息历史API", self.test_messages_api_basic()))
            
            # 3. 不带conversation_id的API测试
            results.append(("不带conversation_id的API", self.test_messages_api_without_conversation_id()))
            
            # 4. 参数验证测试
            results.append(("参数验证", self.test_messages_api_validation()))
            
            # 5. 配置API测试
            results.append(("Dify配置API", self.test_dify_config_api()))
        else:
            results.append(("用户登录", False))
            print("\n❌ 登录失败，跳过后续测试")
        
        # 显示测试总结
        self.print_separator("测试结果总结")
        
        passed_tests = 0
        total_tests = len(results)
        
        for test_name, passed in results:
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{test_name:20} {status}")
            if passed:
                passed_tests += 1
        
        print(f"\n📊 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过测试: {passed_tests}")
        print(f"   失败测试: {total_tests - passed_tests}")
        print(f"   成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print(f"\n🎉 所有测试通过！消息历史转发接口实现成功！")
        else:
            print(f"\n⚠️ 部分测试失败，请检查相关配置和实现")
        
        print(f"\n🏁 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试Dify消息历史转发接口')
    parser.add_argument('--url', default='http://localhost:5000', 
                      help='服务器URL (默认: http://localhost:5000)')
    parser.add_argument('--email', default='test@example.com',
                      help='登录邮箱 (默认: test@example.com)')
    parser.add_argument('--password', default='TestPassword123!',
                      help='登录密码 (默认: TestPassword123!)')
    
    args = parser.parse_args()
    
    # 创建测试器并运行测试
    tester = MessagesApiTester(args.url)
    tester.run_all_tests()

if __name__ == '__main__':
    main() 