#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify API V2 接口测试脚本

用于测试所有V2接口的功能和性能
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DifyV2Tester:
    """Dify V2 API 测试类"""
    
    def __init__(self, base_url='http://localhost:5000', username=None, password=None):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.session = requests.Session()
        self.test_results = []
        
        print(f"🚀 Dify V2 API 测试开始")
        print(f"📡 服务器地址: {self.base_url}")
        print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 如果提供了用户名和密码，自动登录
        if username and password:
            self.login(username, password)
    
    def log_test(self, test_name, success, message, details=None):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        if details and not success:
            print(f"   详细信息: {details}")
    
    def login(self, username, password):
        """用户登录获取JWT Token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={
                    'username': username,
                    'password': password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data['data']['access_token']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    self.log_test("用户登录", True, f"登录成功，用户: {username}")
                    return True
                else:
                    self.log_test("用户登录", False, f"登录失败: {data.get('message')}")
                    return False
            else:
                self.log_test("用户登录", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("用户登录", False, f"登录异常: {str(e)}")
            return False
    
    def test_scenarios_list(self):
        """测试获取应用场景列表"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/dify/v2/scenarios",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    scenarios = data['data']['scenarios']
                    scenario_names = [s['name'] for s in scenarios]
                    self.log_test(
                        "获取应用场景列表", 
                        True, 
                        f"获取到 {len(scenarios)} 个场景: {', '.join(scenario_names)}"
                    )
                    return scenarios
                else:
                    self.log_test("获取应用场景列表", False, f"API返回失败: {data.get('message')}")
                    return []
            else:
                self.log_test("获取应用场景列表", False, f"HTTP {response.status_code}")
                return []
                
        except Exception as e:
            self.log_test("获取应用场景列表", False, f"请求异常: {str(e)}")
            return []
    
    def test_scenario_config(self, scenario):
        """测试获取指定场景配置"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/dify/v2/{scenario}/config",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    scenario_info = data['data']['scenario_info']
                    configured_apis = sum(1 for api in scenario_info['apis'].values() if api['is_configured'])
                    total_apis = len(scenario_info['apis'])
                    
                    self.log_test(
                        f"获取{scenario}配置", 
                        True, 
                        f"配置完整度: {configured_apis}/{total_apis}"
                    )
                    return data['data']
                else:
                    self.log_test(f"获取{scenario}配置", False, f"API返回失败: {data.get('message')}")
                    return None
            else:
                self.log_test(f"获取{scenario}配置", False, f"HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test(f"获取{scenario}配置", False, f"请求异常: {str(e)}")
            return None
    
    def test_chat_simple(self, scenario, test_message="你好，这是一个测试消息"):
        """测试聊天接口"""
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/api/dify/v2/{scenario}/chat-simple",
                json={
                    'inputs': {'query': test_message},
                    'query': test_message,
                    'response_mode': 'streaming',
                    'user': 'test_user'
                },
                timeout=30,
                stream=True
            )
            
            if response.status_code == 200:
                # 处理流式响应
                chunk_count = 0
                total_content = ""
                
                try:
                    for line in response.iter_lines(decode_unicode=True):
                        if line and line.startswith('data: '):
                            chunk_count += 1
                            try:
                                data = json.loads(line[6:])  # 去掉 'data: ' 前缀
                                if 'answer' in data:
                                    total_content += data['answer']
                            except json.JSONDecodeError:
                                pass
                    
                    elapsed_time = round((time.time() - start_time) * 1000, 2)
                    
                    if chunk_count > 0:
                        self.log_test(
                            f"{scenario}聊天接口", 
                            True, 
                            f"收到 {chunk_count} 个数据块，耗时 {elapsed_time}ms"
                        )
                        return True
                    else:
                        self.log_test(f"{scenario}聊天接口", False, "未收到任何响应数据")
                        return False
                        
                except Exception as stream_error:
                    self.log_test(f"{scenario}聊天接口", False, f"流式处理错误: {str(stream_error)}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(
                        f"{scenario}聊天接口", 
                        False, 
                        f"HTTP {response.status_code}: {error_data.get('message', response.text)}"
                    )
                except:
                    self.log_test(f"{scenario}聊天接口", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"{scenario}聊天接口", False, f"请求异常: {str(e)}")
            return False
    
    def test_conversations(self, scenario, user='test_user'):
        """测试获取会话列表"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/dify/v2/{scenario}/conversations",
                params={'user': user, 'limit': 10},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    conversation_count = len(data['data'])
                    self.log_test(
                        f"{scenario}会话列表", 
                        True, 
                        f"获取到 {conversation_count} 个会话"
                    )
                    return data['data']
                else:
                    self.log_test(f"{scenario}会话列表", False, f"响应格式错误: {data}")
                    return []
            else:
                try:
                    error_data = response.json()
                    self.log_test(
                        f"{scenario}会话列表", 
                        False, 
                        f"HTTP {response.status_code}: {error_data.get('message', response.text)}"
                    )
                except:
                    self.log_test(f"{scenario}会话列表", False, f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test(f"{scenario}会话列表", False, f"请求异常: {str(e)}")
            return []
    
    def test_messages(self, scenario, user='test_user', conversation_id=None):
        """测试获取消息历史"""
        try:
            params = {'user': user, 'limit': 10}
            if conversation_id:
                params['conversation_id'] = conversation_id
            
            response = self.session.get(
                f"{self.base_url}/api/dify/v2/{scenario}/messages",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    message_count = len(data['data'])
                    self.log_test(
                        f"{scenario}消息历史", 
                        True, 
                        f"获取到 {message_count} 条消息"
                    )
                    return data['data']
                else:
                    self.log_test(f"{scenario}消息历史", False, f"响应格式错误: {data}")
                    return []
            else:
                try:
                    error_data = response.json()
                    self.log_test(
                        f"{scenario}消息历史", 
                        False, 
                        f"HTTP {response.status_code}: {error_data.get('message', response.text)}"
                    )
                except:
                    self.log_test(f"{scenario}消息历史", False, f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test(f"{scenario}消息历史", False, f"请求异常: {str(e)}")
            return []
    
    def test_v1_compatibility(self):
        """测试V1兼容性接口"""
        print("\n📋 测试V1兼容性接口...")
        
        # 测试V1配置接口
        try:
            response = self.session.get(f"{self.base_url}/api/dify/config", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("V1配置接口", True, "V1配置接口工作正常")
                else:
                    self.log_test("V1配置接口", False, f"API返回失败: {data.get('message')}")
            else:
                self.log_test("V1配置接口", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("V1配置接口", False, f"请求异常: {str(e)}")
        
        # 测试V1会话列表接口
        try:
            response = self.session.get(
                f"{self.base_url}/api/dify/conversations",
                params={'user': 'test_user', 'limit': 5},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    self.log_test("V1会话列表", True, f"获取到 {len(data['data'])} 个会话")
                else:
                    self.log_test("V1会话列表", False, f"响应格式错误")
            else:
                self.log_test("V1会话列表", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("V1会话列表", False, f"请求异常: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        if not self.token:
            print("❌ 未登录，无法进行测试")
            return
        
        print("\n📋 开始V2接口全面测试...")
        
        # 1. 测试获取应用场景列表
        scenarios = self.test_scenarios_list()
        
        if not scenarios:
            print("❌ 无法获取应用场景，停止测试")
            return
        
        # 2. 测试每个场景的所有接口
        for scenario_info in scenarios:
            scenario_key = scenario_info['key']
            scenario_name = scenario_info['name']
            
            print(f"\n🔄 测试场景: {scenario_name} ({scenario_key})")
            
            # 测试配置接口
            self.test_scenario_config(scenario_key)
            
            # 测试聊天接口
            self.test_chat_simple(scenario_key)
            
            # 测试会话列表
            conversations = self.test_conversations(scenario_key)
            
            # 测试消息历史
            conversation_id = conversations[0]['id'] if conversations else None
            self.test_messages(scenario_key, conversation_id=conversation_id)
        
        # 3. 测试V1兼容性
        self.test_v1_compatibility()
        
        # 4. 输出测试报告
        self.print_test_report()
    
    def print_test_report(self):
        """打印测试报告"""
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {failed_tests}")
        print(f"📊 成功率: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "📊 成功率: 0%")
        
        if failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print(f"\n⏰ 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存测试报告到文件
        report_file = f"logs/dify_v2_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            os.makedirs('logs', exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'summary': {
                        'total_tests': total_tests,
                        'passed_tests': passed_tests,
                        'failed_tests': failed_tests,
                        'success_rate': (passed_tests/total_tests*100) if total_tests > 0 else 0,
                        'test_time': datetime.now().isoformat()
                    },
                    'results': self.test_results
                }, f, ensure_ascii=False, indent=2)
            print(f"📄 详细报告已保存到: {report_file}")
        except Exception as e:
            print(f"⚠️  保存报告失败: {e}")

def main():
    """主函数"""
    print("🧪 Dify API V2 接口测试工具")
    print("=" * 60)
    
    # 配置参数
    base_url = os.getenv('TEST_BASE_URL', 'http://localhost:5000')
    username = os.getenv('TEST_USERNAME')
    password = os.getenv('TEST_PASSWORD')
    
    # 如果没有环境变量，提示用户输入
    if not username:
        username = input("请输入测试用户名 (或设置 TEST_USERNAME 环境变量): ").strip()
    if not password:
        password = input("请输入测试密码 (或设置 TEST_PASSWORD 环境变量): ").strip()
    
    if not username or not password:
        print("❌ 需要用户名和密码才能进行测试")
        return
    
    # 创建测试器并运行测试
    tester = DifyV2Tester(base_url, username, password)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 