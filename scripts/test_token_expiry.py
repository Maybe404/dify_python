#!/usr/bin/env python3
"""
Token过期时间测试脚本
验证JWT Token过期时间是否从1小时改为12小时
"""

import requests
import json
import jwt
from datetime import datetime, timezone
import time

def test_token_expiry():
    """测试Token过期时间"""
    
    base_url = "http://localhost:5000/api"
    
    print("🔍 Token过期时间测试")
    print("=" * 50)
    
    # 1. 注册测试用户
    timestamp = int(time.time())
    test_user = {
        'username': f'tokentest{timestamp}',
        'email': f'tokentest{timestamp}@gmail.com',
        'password': 'TestPassword123456!@#$'
    }
    
    print(f"📝 注册测试用户: {test_user['username']}")
    
    try:
        register_response = requests.post(
            f"{base_url}/auth/register",
            json=test_user,
            timeout=10
        )
        
        if register_response.status_code != 201:
            print(f"❌ 注册失败: {register_response.text}")
            return
        
        print("✅ 用户注册成功")
        
    except Exception as e:
        print(f"❌ 注册请求失败: {str(e)}")
        return
    
    # 2. 登录获取Token
    print(f"\n🔑 用户登录获取Token")
    
    try:
        login_response = requests.post(
            f"{base_url}/auth/login",
            json={
                'credential': test_user['username'],
                'password': test_user['password']
            },
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.text}")
            return
        
        login_data = login_response.json()
        access_token = login_data['data']['access_token']
        
        print("✅ 登录成功，Token获取成功")
        
    except Exception as e:
        print(f"❌ 登录请求失败: {str(e)}")
        return
    
    # 3. 解析Token获取过期时间
    print(f"\n📄 解析Token信息")
    
    try:
        # 解码Token（不验证签名，仅获取payload）
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        
        # 获取时间戳
        issued_at = decoded_token.get('iat')  # 签发时间
        expires_at = decoded_token.get('exp')  # 过期时间
        
        if issued_at and expires_at:
            # 转换为可读时间
            issued_time = datetime.fromtimestamp(issued_at, tz=timezone.utc)
            expire_time = datetime.fromtimestamp(expires_at, tz=timezone.utc)
            
            # 计算有效期
            duration_seconds = expires_at - issued_at
            duration_hours = duration_seconds / 3600
            
            print(f"   签发时间: {issued_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"   过期时间: {expire_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"   有效期: {duration_seconds}秒 ({duration_hours}小时)")
            
            # 验证是否为12小时
            if abs(duration_hours - 12) < 0.1:  # 允许小误差
                print("✅ Token过期时间正确设置为12小时")
            else:
                print(f"❌ Token过期时间不正确，期望12小时，实际{duration_hours}小时")
                
        else:
            print("❌ 无法获取Token时间信息")
            
        # 打印完整Token信息
        print(f"\n📋 完整Token信息:")
        print(json.dumps(decoded_token, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Token解析失败: {str(e)}")
        return
    
    # 4. 验证Token是否有效
    print(f"\n🔍 验证Token有效性")
    
    try:
        verify_response = requests.post(
            f"{base_url}/auth/verify-token",
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if verify_response.status_code == 200:
            print("✅ Token验证成功，当前有效")
            verify_data = verify_response.json()
            token_info = verify_data.get('data', {}).get('token_info', {})
            
            if token_info:
                exp = token_info.get('exp')
                if exp:
                    remaining_time = exp - time.time()
                    remaining_hours = remaining_time / 3600
                    print(f"   剩余有效期: {remaining_time:.0f}秒 ({remaining_hours:.2f}小时)")
        else:
            print(f"❌ Token验证失败: {verify_response.text}")
            
    except Exception as e:
        print(f"❌ Token验证请求失败: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 测试总结:")
    print("1. 如果显示'Token过期时间正确设置为12小时'，说明配置修改成功")
    print("2. 如果显示其他时间，请检查配置文件是否正确修改")
    print("3. JWT_ACCESS_TOKEN_EXPIRES应该设置为43200秒（12小时）")

def test_config_values():
    """测试配置值"""
    print("\n🔧 配置文件检查")
    print("=" * 30)
    
    try:
        # 检查环境变量配置示例
        with open('env_example.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'JWT_ACCESS_TOKEN_EXPIRES=43200' in content:
                print("✅ env_example.txt 配置正确")
            else:
                print("❌ env_example.txt 配置需要更新")
    except Exception as e:
        print(f"⚠️  无法读取env_example.txt: {str(e)}")
    
    try:
        # 检查应用配置
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from app.config.config import Config
        
        expires = Config.JWT_ACCESS_TOKEN_EXPIRES
        total_seconds = expires.total_seconds()
        hours = total_seconds / 3600
        
        print(f"   当前配置: {total_seconds}秒 ({hours}小时)")
        
        if abs(hours - 12) < 0.1:
            print("✅ app/config/config.py 配置正确")
        else:
            print("❌ app/config/config.py 配置需要更新")
            
    except Exception as e:
        print(f"⚠️  无法读取应用配置: {str(e)}")

if __name__ == "__main__":
    # 先检查配置文件
    test_config_values()
    
    # 然后测试实际Token
    test_token_expiry() 