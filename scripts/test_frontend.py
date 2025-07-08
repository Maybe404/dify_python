#!/usr/bin/env python3
"""
前端连接测试脚本
模拟前端API调用，检查后端接口是否正常
"""

import requests
import json
import time
from datetime import datetime

API_BASE_URL = 'http://localhost:5000/api'

def test_api_endpoint(method, endpoint, data=None, headers=None, expected_status=None):
    """测试API端点"""
    url = f"{API_BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    try:
        print(f"\n🔗 测试: {method} {endpoint}")
        print(f"   URL: {url}")
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'OPTIONS':
            response = requests.options(url, headers=headers)
        else:
            print(f"   ❌ 不支持的方法: {method}")
            return False
        
        print(f"   状态码: {response.status_code}")
        print(f"   状态文本: {response.reason}")
        
        # 检查CORS头
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        if any(cors_headers.values()):
            print(f"   CORS头: {cors_headers}")
        
        # 尝试解析JSON响应
        try:
            response_data = response.json()
            print(f"   响应: {json.dumps(response_data, ensure_ascii=False, indent=2)[:200]}...")
        except:
            print(f"   响应文本: {response.text[:100]}...")
        
        # 检查期望状态码
        if expected_status:
            if response.status_code == expected_status:
                print(f"   ✅ 状态码符合预期 ({expected_status})")
                return True
            else:
                print(f"   ⚠️  状态码不符合预期 (期望: {expected_status}, 实际: {response.status_code})")
                return False
        else:
            if 200 <= response.status_code < 300:
                print(f"   ✅ 请求成功")
                return True
            else:
                print(f"   ⚠️  请求失败")
                return response.status_code in [401, 404, 422]  # 这些状态码在某些情况下是预期的
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 连接失败: 无法连接到服务器")
        print(f"   💡 请检查:")
        print(f"      - 后端服务是否已启动 (python run.py)")
        print(f"      - 端口5000是否被占用")
        print(f"      - 防火墙设置")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ 连接超时")
        return False
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False

def run_frontend_tests():
    """运行前端连接测试"""
    print("🧪 前端API连接测试")
    print("=" * 50)
    print(f"API基础URL: {API_BASE_URL}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        {
            'name': '测试CORS预检请求',
            'method': 'OPTIONS',
            'endpoint': '/auth/verify-token',
            'expected_status': 200
        },
        {
            'name': '测试Token验证接口 (无Token)',
            'method': 'POST',
            'endpoint': '/auth/verify-token',
            'data': {},
            'expected_status': 422
        },
        {
            'name': '测试Token验证接口 (无效Token)',
            'method': 'POST',
            'endpoint': '/auth/verify-token',
            'data': {},
            'headers': {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer invalid-token'
            },
            'expected_status': 422
        },
        {
            'name': '测试注册接口 (无数据)',
            'method': 'POST',
            'endpoint': '/auth/register',
            'data': {},
            'expected_status': 400
        },
        {
            'name': '测试注册接口 (测试数据)',
            'method': 'POST',
            'endpoint': '/auth/register',
            'data': {
                'username': f'test_{int(time.time())}',
                'email': f'test_{int(time.time())}@example.com',
                'password': 'TestPass123'
            },
            'expected_status': 201
        },
        {
            'name': '测试登录接口 (错误凭证)',
            'method': 'POST',
            'endpoint': '/auth/login',
            'data': {
                'credential': 'nonexistent_user',
                'password': 'wrongpassword'
            },
            'expected_status': 404
        },
        {
            'name': '测试忘记密码接口 (无效邮箱)',
            'method': 'POST',
            'endpoint': '/auth/forgot-password',
            'data': {
                'email': 'nonexistent@example.com'
            },
            'expected_status': 200  # 为安全考虑，即使邮箱不存在也返回200
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for i, test in enumerate(tests, 1):
        print(f"\n📋 测试 {i}/{total}: {test['name']}")
        
        result = test_api_endpoint(
            method=test['method'],
            endpoint=test['endpoint'],
            data=test.get('data'),
            headers=test.get('headers'),
            expected_status=test.get('expected_status')
        )
        
        if result:
            passed += 1
        
        time.sleep(0.5)  # 避免请求过快
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！前端应该能正常连接到后端")
        print("\n💡 建议:")
        print("   1. 打开 web_test/debug.html 进行详细测试")
        print("   2. 打开 web_test/index.html 使用完整功能")
    elif passed >= total * 0.7:
        print("⚠️  大部分测试通过，可能存在少数问题")
        print("\n💡 建议:")
        print("   1. 检查失败的测试项")
        print("   2. 运行 python check_config.py 检查配置")
    else:
        print("❌ 多个测试失败，存在严重问题")
        print("\n💡 排查步骤:")
        print("   1. 确认后端服务已启动: python run.py")
        print("   2. 检查.env文件是否存在并配置正确")
        print("   3. 运行 python check_config.py 进行完整检查")
        print("   4. 查看后端服务日志输出")

if __name__ == '__main__':
    run_frontend_tests() 