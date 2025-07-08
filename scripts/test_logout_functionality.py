#!/usr/bin/env python3
"""
登出功能测试脚本
专门测试登出功能是否正常工作
"""

import sys
import os
import requests
import json
import time

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LogoutTester:
    """登出功能测试器"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        
    def print_step(self, step, message):
        """打印测试步骤"""
        print(f"\n{step}. {message}")
        print("=" * 60)
    
    def print_result(self, success, message, data=None):
        """打印测试结果"""
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status}: {message}")
        if data:
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    def test_server_connection(self):
        """测试服务器连接"""
        self.print_step("1", "测试服务器连接")
        
        try:
            response = requests.post(f"{self.base_url}/api/auth/verify-token", 
                                   headers={'Authorization': 'Bearer invalid-token'},
                                   timeout=5)
            if response.status_code in [401, 422]:  # 预期的未授权状态码
                self.print_result(True, "服务器连接正常")
                return True
            else:
                self.print_result(False, f"服务器响应异常: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_result(False, "无法连接到服务器，请确保应用正在运行")
            return False
        except Exception as e:
            self.print_result(False, f"连接异常: {e}")
            return False
    
    def register_and_login(self):
        """注册并登录用户"""
        self.print_step("2", "注册并登录测试用户")
        
        # 注册新用户
        timestamp = int(time.time())
        user_data = {
            'username': f'logouttest{timestamp}',
            'email': f'logouttest{timestamp}@gmail.com',
            'password': 'LogoutTest123!@#$%'  # 满足新的密码要求：>=16位
        }
        
        try:
            # 注册
            register_response = requests.post(f'{self.base_url}/api/auth/register', 
                                            json=user_data, timeout=10)
            if register_response.status_code != 201:
                register_result = register_response.json()
                self.print_result(False, f"注册失败: {register_result.get('message')}")
                return False
            
            self.print_result(True, "用户注册成功")
            
            # 登录
            login_data = {
                'credential': user_data['email'],
                'password': user_data['password']
            }
            
            login_response = requests.post(f'{self.base_url}/api/auth/login', 
                                         json=login_data, timeout=10)
            if login_response.status_code != 200:
                login_result = login_response.json()
                self.print_result(False, f"登录失败: {login_result.get('message')}")
                return False
            
            login_result = login_response.json()
            
            if 'data' in login_result and 'access_token' in login_result['data']:
                self.token = login_result['data']['access_token']
                user_info = login_result['data']['user']
                self.print_result(True, f"登录成功，获得token", {
                    "user": user_info,
                    "token_preview": f"{self.token[:20]}...{self.token[-10:]}"
                })
                return True
            else:
                self.print_result(False, "登录响应中没有access_token")
                return False
                
        except Exception as e:
            self.print_result(False, f"注册登录异常: {e}")
            return False
    
    def test_token_before_logout(self):
        """测试登出前token是否有效"""
        self.print_step("3", "测试登出前token是否有效")
        
        if not self.token:
            self.print_result(False, "没有token可供测试")
            return False
        
        try:
            # 测试验证token接口
            verify_response = requests.post(f'{self.base_url}/api/auth/verify-token',
                                          headers={'Authorization': f'Bearer {self.token}'},
                                          timeout=10)
            
            if verify_response.status_code == 200:
                verify_result = verify_response.json()
                if verify_result.get('success'):
                    self.print_result(True, "Token在登出前有效", verify_result)
                    return True
                else:
                    self.print_result(False, f"Token验证失败: {verify_result.get('message')}")
                    return False
            else:
                verify_result = verify_response.json()
                self.print_result(False, f"Token验证请求失败: {verify_result.get('message')}")
                return False
                
        except Exception as e:
            self.print_result(False, f"Token验证异常: {e}")
            return False
    
    def test_logout(self):
        """测试登出功能"""
        self.print_step("4", "执行登出操作")
        
        if not self.token:
            self.print_result(False, "没有token可供登出")
            return False
        
        try:
            logout_response = requests.post(f'{self.base_url}/api/auth/logout',
                                          headers={'Authorization': f'Bearer {self.token}'},
                                          timeout=10)
            
            if logout_response.status_code == 200:
                logout_result = logout_response.json()
                if logout_result.get('success'):
                    self.print_result(True, "登出请求成功", logout_result)
                    return True
                else:
                    self.print_result(False, f"登出失败: {logout_result.get('message')}")
                    return False
            else:
                logout_result = logout_response.json()
                self.print_result(False, f"登出请求失败: {logout_result.get('message')}")
                return False
                
        except Exception as e:
            self.print_result(False, f"登出操作异常: {e}")
            return False
    
    def test_token_after_logout(self):
        """测试登出后token是否失效"""
        self.print_step("5", "测试登出后token是否失效")
        
        if not self.token:
            self.print_result(False, "没有token可供测试")
            return False
        
        try:
            # 测试各个需要认证的接口
            test_endpoints = [
                {'name': 'verify-token', 'url': '/api/auth/verify-token', 'method': 'POST'},
                {'name': 'profile', 'url': '/api/auth/profile', 'method': 'GET'},
                {'name': 'change-password', 'url': '/api/auth/change-password', 'method': 'POST', 
                 'data': {'current_password': 'old', 'new_password': 'new123456789012345'}}
            ]
            
            all_failed = True
            
            for endpoint in test_endpoints:
                print(f"\n   测试 {endpoint['name']} 接口...")
                
                headers = {'Authorization': f'Bearer {self.token}'}
                if endpoint['method'] == 'POST':
                    headers['Content-Type'] = 'application/json'
                
                response = requests.request(
                    method=endpoint['method'],
                    url=f"{self.base_url}{endpoint['url']}",
                    headers=headers,
                    json=endpoint.get('data'),
                    timeout=10
                )
                
                if response.status_code == 401:
                    response_data = response.json()
                    if 'Token已被撤销' in response_data.get('message', '') or 'Token已失效' in response_data.get('message', ''):
                        print(f"     ✅ {endpoint['name']}: Token正确被拒绝 - {response_data.get('message')}")
                    else:
                        print(f"     ⚠️  {endpoint['name']}: Token被拒绝，但原因不是撤销 - {response_data.get('message')}")
                elif response.status_code == 200:
                    print(f"     ❌ {endpoint['name']}: Token仍然有效！这是问题所在")
                    all_failed = False
                else:
                    response_data = response.json()
                    print(f"     ⚠️  {endpoint['name']}: 意外状态码 {response.status_code} - {response_data.get('message')}")
            
            if all_failed:
                self.print_result(True, "所有接口都正确拒绝了已撤销的token")
                return True
            else:
                self.print_result(False, "某些接口仍然接受已撤销的token")
                return False
                
        except Exception as e:
            self.print_result(False, f"Token失效测试异常: {e}")
            return False
    
    def run_complete_test(self):
        """运行完整的登出功能测试"""
        print("🧪 开始登出功能完整测试...")
        print("=" * 80)
        
        test_results = []
        
        # 1. 测试服务器连接
        result1 = self.test_server_connection()
        test_results.append(("服务器连接", result1))
        
        if not result1:
            print("\n❌ 服务器连接失败，终止测试")
            return False
        
        # 2. 注册并登录
        result2 = self.register_and_login()
        test_results.append(("注册登录", result2))
        
        if not result2:
            print("\n❌ 注册登录失败，终止测试")
            return False
        
        # 3. 测试登出前token有效性
        result3 = self.test_token_before_logout()
        test_results.append(("登出前token验证", result3))
        
        # 4. 执行登出
        result4 = self.test_logout()
        test_results.append(("登出操作", result4))
        
        # 5. 测试登出后token失效性
        result5 = self.test_token_after_logout()
        test_results.append(("登出后token验证", result5))
        
        # 显示测试总结
        print("\n" + "=" * 80)
        print("🏁 测试结果总结:")
        print("=" * 80)
        
        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{status}: {test_name}")
        
        all_passed = all(result for _, result in test_results)
        
        if all_passed:
            print(f"\n🎉 所有测试通过！登出功能工作正常！")
            print("✅ Token在登出后正确失效")
            print("✅ 已撤销的token无法访问需要认证的接口")
        else:
            print(f"\n⚠️  部分测试失败，登出功能可能存在问题")
            failed_tests = [name for name, result in test_results if not result]
            print(f"失败的测试: {', '.join(failed_tests)}")
        
        return all_passed

def main():
    """主函数"""
    tester = LogoutTester()
    tester.run_complete_test()

if __name__ == '__main__':
    main() 