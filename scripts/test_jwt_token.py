#!/usr/bin/env python3
"""
JWT Token 诊断脚本
用于测试和诊断JWT token相关问题
"""

import os
import sys
import json
import base64
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 添加父目录到路径，以便可以导入app模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def decode_jwt_token(token):
    """解码JWT token的header和payload部分"""
    try:
        # JWT token由三部分组成：header.payload.signature
        parts = token.split('.')
        
        if len(parts) != 3:
            return False, f"JWT token格式错误：应该有3部分，实际有{len(parts)}部分"
        
        header_encoded, payload_encoded, signature = parts
        
        # 解码header
        try:
            # 添加padding如果需要
            header_encoded += '=' * (4 - len(header_encoded) % 4)
            header_decoded = base64.urlsafe_b64decode(header_encoded)
            header_json = json.loads(header_decoded.decode('utf-8'))
            print(f"✅ Header解码成功: {json.dumps(header_json, indent=2)}")
        except Exception as e:
            return False, f"Header解码失败: {e}"
        
        # 解码payload
        try:
            # 添加padding如果需要
            payload_encoded += '=' * (4 - len(payload_encoded) % 4)
            payload_decoded = base64.urlsafe_b64decode(payload_encoded)
            payload_json = json.loads(payload_decoded.decode('utf-8'))
            print(f"✅ Payload解码成功: {json.dumps(payload_json, indent=2)}")
            
            # 检查过期时间
            if 'exp' in payload_json:
                exp_time = datetime.fromtimestamp(payload_json['exp'])
                now = datetime.now()
                if exp_time < now:
                    print(f"⚠️  Token已过期: {exp_time} < {now}")
                else:
                    print(f"✅ Token未过期: {exp_time} > {now}")
            
        except Exception as e:
            return False, f"Payload解码失败: {e}"
        
        return True, "Token解码成功"
        
    except Exception as e:
        return False, f"Token解析失败: {e}"

def test_jwt_endpoints():
    """测试JWT相关的API端点"""
    base_url = "http://localhost:5000/api/auth"
    
    print("\n🧪 测试JWT相关端点")
    print("=" * 50)
    
    # 测试1: 无token的verify-token请求
    print("\n📋 测试1: 无Authorization header")
    try:
        response = requests.post(f"{base_url}/verify-token", 
                               headers={'Content-Type': 'application/json'})
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试2: 空token
    print("\n📋 测试2: 空Authorization header")
    try:
        response = requests.post(f"{base_url}/verify-token", 
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': 'Bearer '
                               })
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试3: 无效token格式
    print("\n📋 测试3: 无效token格式")
    try:
        response = requests.post(f"{base_url}/verify-token", 
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': 'Bearer invalid-token'
                               })
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试4: 畸形JWT格式
    print("\n📋 测试4: 畸形JWT格式")
    malformed_tokens = [
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",  # 只有header
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.",  # header后有点但无payload
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..",  # header后有两个点
        "Bearer {invalid:json}",  # 无效JSON
    ]
    
    for i, token in enumerate(malformed_tokens, 1):
        print(f"\n  子测试4.{i}: {token[:50]}...")
        try:
            response = requests.post(f"{base_url}/verify-token", 
                                   headers={
                                       'Content-Type': 'application/json',
                                       'Authorization': token
                                   })
            print(f"  状态码: {response.status_code}")
            try:
                print(f"  响应: {response.json()}")
            except:
                print(f"  响应文本: {response.text}")
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")

def test_token_generation():
    """测试token生成"""
    print("\n🔑 测试Token生成")
    print("=" * 50)
    
    base_url = "http://localhost:5000/api/auth"
    
    # 尝试注册一个测试用户
    test_email = f"test_{int(datetime.now().timestamp())}@example.com"
    test_password = "TestPass1234@#$"  # 16位强密码
    
    print(f"📝 注册测试用户: {test_email}")
    try:
        register_response = requests.post(f"{base_url}/register", 
                                        json={
                                            'email': test_email,
                                            'password': test_password
                                        })
        print(f"注册状态码: {register_response.status_code}")
        register_data = register_response.json()
        print(f"注册响应: {json.dumps(register_data, ensure_ascii=False, indent=2)}")
        
        if not register_data.get('success'):
            print("❌ 注册失败，跳过token测试")
            return
        
    except Exception as e:
        print(f"❌ 注册失败: {e}")
        return
    
    # 尝试登录获取token
    print(f"\n🔐 登录获取token")
    try:
        login_response = requests.post(f"{base_url}/login", 
                                     json={
                                         'credential': test_email,
                                         'password': test_password
                                     })
        print(f"登录状态码: {login_response.status_code}")
        login_data = login_response.json()
        
        if login_data.get('success') and 'data' in login_data and 'access_token' in login_data['data']:
            token = login_data['data']['access_token']
            print(f"✅ 获取到token: {token[:50]}...")
            
            # 解码并分析token
            print(f"\n🔍 分析token内容:")
            success, message = decode_jwt_token(token)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
            
            # 使用获取的token测试verify-token端点
            print(f"\n🧪 使用真实token测试verify-token端点")
            try:
                verify_response = requests.post(f"{base_url}/verify-token", 
                                              headers={
                                                  'Content-Type': 'application/json',
                                                  'Authorization': f'Bearer {token}'
                                              })
                print(f"验证状态码: {verify_response.status_code}")
                verify_data = verify_response.json()
                print(f"验证响应: {json.dumps(verify_data, ensure_ascii=False, indent=2)}")
                
            except Exception as e:
                print(f"❌ Token验证失败: {e}")
        else:
            print(f"❌ 登录失败: {json.dumps(login_data, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ 登录失败: {e}")

def main():
    """主函数"""
    print("🔍 JWT Token 诊断工具")
    print("=" * 60)
    
    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:5000/api/auth/verify-token", timeout=5)
        print("✅ 服务器正在运行")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器 (http://localhost:5000)")
        print("请确保应用正在运行: python run.py")
        return
    except Exception as e:
        print(f"⚠️  服务器响应异常: {e}")
    
    # 运行测试
    test_jwt_endpoints()
    test_token_generation()
    
    print("\n" + "=" * 60)
    print("🎯 诊断建议:")
    print("1. 如果看到'Invalid header string'错误，通常是JWT格式问题")
    print("2. 确保Authorization header格式为: Bearer <token>")
    print("3. 检查token是否完整（包含三个点分隔的部分）")
    print("4. 验证JWT_SECRET_KEY配置是否正确")
    print("5. 查看服务器日志获取更详细的错误信息")

if __name__ == '__main__':
    main() 