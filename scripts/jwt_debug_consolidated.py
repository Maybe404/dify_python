#!/usr/bin/env python3
"""
整合的JWT调试和测试脚本
合并了根目录下所有JWT相关的调试功能
- Token格式调试
- Token内容分析  
- 完整用户流程测试
- 密码验证测试
"""

import sys
import os
import requests
import json
import time
import base64

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.utils.security import validate_password, validate_registration_data
from flask_jwt_extended import create_access_token, decode_token

class JWTDebugger:
    """JWT调试器类"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        
    def decode_token_manually(self, token):
        """手动解码JWT token"""
        print(f"\n🔍 手动解码Token分析:")
        print(f"Token长度: {len(token)}")
        
        parts = token.split('.')
        print(f"Token段数: {len(parts)}")
        
        if len(parts) != 3:
            print("❌ Token格式错误：不是标准的JWT格式（应该有3段）")
            return False
        
        try:
            # 解码Header
            header_part = parts[0]
            header_part += '=' * (4 - len(header_part) % 4)
            header_decoded = base64.urlsafe_b64decode(header_part)
            header_json = json.loads(header_decoded.decode('utf-8'))
            print(f"✅ Header解码成功: {json.dumps(header_json, indent=2)}")
            
            # 解码Payload
            payload_part = parts[1]
            payload_part += '=' * (4 - len(payload_part) % 4)
            payload_decoded = base64.urlsafe_b64decode(payload_part)
            payload_json = json.loads(payload_decoded.decode('utf-8'))
            print(f"✅ Payload解码成功: {json.dumps(payload_json, indent=2)}")
            
            # 检查过期时间
            if 'exp' in payload_json:
                exp_timestamp = payload_json['exp']
                current_timestamp = time.time()
                print(f"Token过期时间: {exp_timestamp}")
                print(f"当前时间戳: {current_timestamp}")
                if current_timestamp > exp_timestamp:
                    print("❌ Token已过期")
                    return False
                else:
                    print("✅ Token未过期")
            
            return True
            
        except Exception as e:
            print(f"❌ Token解码失败: {e}")
            return False
    
    def inspect_actual_token(self):
        """检查实际返回的token内容"""
        print("🔍 检查实际返回的Token...")
        
        timestamp = int(time.time())
        register_data = {
            'username': f'user{timestamp}'[-20:],
            'email': f'inspect{timestamp}@gmail.com',
            'password': 'InspectToken123!'
        }
        
        try:
            # 注册
            register_response = requests.post(f'{self.base_url}/api/auth/register', 
                                            json=register_data, timeout=10)
            if register_response.status_code != 201:
                print(f"❌ 注册失败: {register_response.json()}")
                return None
            
            # 登录
            login_data = {
                'credential': register_data['email'],
                'password': register_data['password']
            }
            
            login_response = requests.post(f'{self.base_url}/api/auth/login', 
                                         json=login_data, timeout=10)
            if login_response.status_code != 200:
                print(f"❌ 登录失败: {login_response.json()}")
                return None
            
            login_result = login_response.json()
            
            if 'data' in login_result and 'access_token' in login_result['data']:
                token = login_result['data']['access_token']
                print(f"\n🎯 Token详细信息:")
                print(f"Token长度: {len(token)}")
                print(f"Token类型: {type(token)}")
                print(f"Token字节表示: {repr(token)}")
                
                # 分析Token结构
                if '.' in token:
                    parts = token.split('.')
                    print(f"按'.'分割的段数: {len(parts)}")
                    for i, part in enumerate(parts):
                        print(f"  段{i+1}: 长度:{len(part)}")
                
                return token
            else:
                print("❌ 登录响应中没有access_token字段")
                return None
                
        except Exception as e:
            print(f"❌ 检查异常: {e}")
            return None
    
    def test_complete_flow(self):
        """测试完整的注册、登录、验证流程"""
        print("🧪 测试完整的用户流程...")
        
        timestamp = int(time.time())
        register_data = {
            'username': f'testuser{timestamp}',
            'email': f'test{timestamp}@gmail.com',
            'password': 'TestPassword123!'
        }
        
        try:
            # 1. 注册
            print("1. 注册新用户...")
            register_response = requests.post(f'{self.base_url}/api/auth/register', 
                                            json=register_data, timeout=10)
            print(f"   注册状态码: {register_response.status_code}")
            
            if register_response.status_code == 201:
                print("✅ 注册成功")
                
                # 2. 登录
                print("\n2. 用户登录...")
                login_data = {
                    'credential': register_data['email'],
                    'password': register_data['password']
                }
                
                login_response = requests.post(f'{self.base_url}/api/auth/login', 
                                             json=login_data, timeout=10)
                print(f"   登录状态码: {login_response.status_code}")
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    print("✅ 登录成功")
                    
                    if 'data' in login_result and 'access_token' in login_result['data']:
                        token = login_result['data']['access_token']
                        print(f"   获得Token: {token[:50]}...")
                        
                        # 3. 验证Token
                        print("\n3. 验证Token...")
                        verify_response = requests.post(f'{self.base_url}/api/auth/verify-token',
                                                      headers={'Authorization': f'Bearer {token}'},
                                                      timeout=10)
                        print(f"   验证状态码: {verify_response.status_code}")
                        verify_result = verify_response.json()
                        
                        if verify_result.get('success'):
                            print("\n🎉 所有测试通过！")
                            return token
                        else:
                            print(f"\n❌ Token验证失败: {verify_result.get('message')}")
                            return None
        
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到服务器，请确保应用正在运行")
            return None
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return None
    
    def test_password_validation(self):
        """测试密码验证"""
        test_passwords = [
            'TestPassword123!@',     # 16位，包含所有要素
            'TestPassword123!',      # 15位，长度不足
            'TestPassword123!@#',    # 17位，符合要求
            'testpassword123!@',     # 16位，没有大写字母
            'TESTPASSWORD123!@',     # 16位，没有小写字母
            'TestPassword!@##',      # 16位，没有数字
            'TestPassword123AB',     # 16位，没有符号
            'VeryLongTestPassword123!@#$%', # 28位，符合要求
        ]
        
        print("🔐 测试密码验证规则...")
        print("=" * 50)
        
        for password in test_passwords:
            is_valid, message = validate_password(password)
            status = "✅" if is_valid else "❌"
            print(f"{status} '{password}' (长度:{len(password)}) - {message}")
    
    def test_jwt_generation(self):
        """测试JWT token生成"""
        print("🔧 JWT Token生成测试")
        print("=" * 50)
        
        app = create_app()
        
        with app.app_context():
            # 检查JWT配置
            print("📋 JWT配置检查:")
            print(f"JWT_SECRET_KEY: {app.config.get('JWT_SECRET_KEY', 'NOT SET')[:20]}...")
            print(f"JWT_ALGORITHM: {app.config.get('JWT_ALGORITHM', 'NOT SET')}")
            print(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 'NOT SET')}")
            
            try:
                # 尝试生成token
                test_user_id = "test-user-123"
                print(f"\n🔑 尝试生成token (user_id: {test_user_id})")
                
                token = create_access_token(identity=test_user_id)
                print(f"✅ Token生成成功")
                print(f"Token长度: {len(token)}")
                print(f"Token段数: {len(token.split('.'))}")
                
                # 测试flask-jwt-extended的验证
                try:
                    decoded = decode_token(token)
                    print(f"\n✅ Flask-JWT-Extended验证成功")
                    print(f"解码结果: {json.dumps(decoded, indent=2, default=str)}")
                except Exception as e:
                    print(f"❌ Flask-JWT-Extended验证失败: {e}")
                
                return token
                
            except Exception as e:
                print(f"❌ Token生成失败: {e}")
                return None

def main():
    """主函数 - 运行所有调试测试"""
    print("🚀 开始JWT调试和测试...")
    print("=" * 60)
    
    debugger = JWTDebugger()
    
    # 菜单选择
    print("\n请选择要执行的测试:")
    print("1. 完整用户流程测试")
    print("2. Token内容检查")
    print("3. Token格式调试")
    print("4. 密码验证测试")
    print("5. JWT生成测试")
    print("6. 运行所有测试")
    
    choice = input("\n请输入选择 (1-6): ").strip()
    
    if choice == '1':
        token = debugger.test_complete_flow()
        if token:
            debugger.decode_token_manually(token)
    elif choice == '2':
        token = debugger.inspect_actual_token()
        if token:
            debugger.decode_token_manually(token)
    elif choice == '3':
        # 使用现有admin用户测试
        print("使用现有admin用户测试...")
        try:
            login_response = requests.post(f'{debugger.base_url}/api/auth/login', 
                                         json={
                                             'credential': 'admin@example.com',
                                             'password': 'Admin123456'
                                         })
            if login_response.status_code == 200:
                login_data = login_response.json()
                if 'data' in login_data and 'access_token' in login_data['data']:
                    token = login_data['data']['access_token']
                    debugger.decode_token_manually(token)
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    elif choice == '4':
        debugger.test_password_validation()
    elif choice == '5':
        debugger.test_jwt_generation()
    elif choice == '6':
        print("\n🔄 运行所有测试...")
        debugger.test_password_validation()
        token = debugger.test_jwt_generation()
        if token:
            debugger.decode_token_manually(token)
        token = debugger.test_complete_flow()
        if token:
            debugger.decode_token_manually(token)
    else:
        print("❌ 无效选择")

if __name__ == '__main__':
    main() 