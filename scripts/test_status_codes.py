#!/usr/bin/env python3
"""
状态码测试脚本
验证API接口状态码是否符合新的规范
"""

import requests
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = "http://localhost:5000/api"

def test_login_status_codes():
    """测试登录接口的状态码"""
    print("🧪 测试登录接口状态码...")
    
    # 测试用户不存在
    print("  📝 测试用户不存在...")
    response = requests.post(f"{API_BASE_URL}/auth/login", json={
        "credential": "nonexistent_user",
        "password": "wrongpassword"
    })
    
    print(f"     状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if not data.get('success'):
            print(f"     ✅ 正确：用户不存在返回200，success=false")
            print(f"     消息: {data.get('message')}")
        else:
            print(f"     ❌ 错误：用户不存在但success=true")
    else:
        print(f"     ❌ 错误：用户不存在应该返回200，实际返回{response.status_code}")
    
    # 测试密码错误（需要先有用户）
    print("  📝 测试密码错误...")
    # 假设有用户testuser，测试密码错误
    response = requests.post(f"{API_BASE_URL}/auth/login", json={
        "credential": "testuser",
        "password": "wrongpassword"
    })
    
    print(f"     状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if not data.get('success'):
            print(f"     ✅ 正确：密码错误返回200，success=false")
            print(f"     消息: {data.get('message')}")
        else:
            print(f"     ❌ 错误：密码错误但success=true")
    else:
        print(f"     ❌ 错误：密码错误应该返回200，实际返回{response.status_code}")

def test_profile_status_codes():
    """测试用户信息接口的状态码"""
    print("\n🧪 测试用户信息接口状态码...")
    
    # 测试无效token
    print("  📝 测试无效token...")
    response = requests.get(f"{API_BASE_URL}/auth/profile", headers={
        "Authorization": "Bearer invalid_token"
    })
    
    print(f"     状态码: {response.status_code}")
    if response.status_code == 422:
        print(f"     ✅ 正确：无效token返回422")
    elif response.status_code == 401:
        print(f"     ✅ 正确：无效token返回401")
    else:
        print(f"     ❌ 错误：无效token应该返回401/422，实际返回{response.status_code}")

def test_task_status_codes():
    """测试任务接口的状态码"""
    print("\n🧪 测试任务接口状态码...")
    
    # 测试任务不存在
    print("  📝 测试任务不存在...")
    response = requests.get(f"{API_BASE_URL}/tasks/nonexistent-task-id", headers={
        "Authorization": "Bearer invalid_token"  # 会被JWT中间件拦截
    })
    
    print(f"     状态码: {response.status_code}")
    if response.status_code == 401 or response.status_code == 422:
        print(f"     ✅ 正确：无token时返回401/422（被JWT中间件拦截）")
    else:
        print(f"     ❌ 意外：预期401/422，实际返回{response.status_code}")

def test_health_status_codes():
    """测试健康检查接口"""
    print("\n🧪 测试健康检查接口...")
    
    # 测试健康检查
    print("  📝 测试健康检查...")
    response = requests.get(f"{API_BASE_URL}/health")
    
    print(f"     状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"     ✅ 正确：健康检查返回200")
    else:
        print(f"     ❌ 错误：健康检查应该返回200，实际返回{response.status_code}")

def test_parameter_validation():
    """测试参数验证的状态码"""
    print("\n🧪 测试参数验证状态码...")
    
    # 测试缺少参数
    print("  📝 测试缺少参数...")
    response = requests.post(f"{API_BASE_URL}/auth/login", json={})
    
    print(f"     状态码: {response.status_code}")
    if response.status_code == 400:
        print(f"     ✅ 正确：缺少参数返回400")
    else:
        print(f"     ❌ 错误：缺少参数应该返回400，实际返回{response.status_code}")
    
    # 测试无效JSON
    print("  📝 测试无效JSON...")
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", 
                               data="invalid json",
                               headers={"Content-Type": "application/json"})
        
        print(f"     状态码: {response.status_code}")
        if response.status_code == 400:
            print(f"     ✅ 正确：无效JSON返回400")
        else:
            print(f"     ❌ 错误：无效JSON应该返回400，实际返回{response.status_code}")
    except Exception as e:
        print(f"     ❌ 请求异常: {e}")

def main():
    """主函数"""
    print("🚀 开始测试API状态码规范...")
    print("=" * 50)
    
    try:
        # 测试服务器连接
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"✅ 服务器连接正常 (状态码: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务已启动")
        print("   运行命令: python run.py")
        return
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return
    
    print("=" * 50)
    
    # 运行各项测试
    test_health_status_codes()
    test_parameter_validation()
    test_login_status_codes()
    test_profile_status_codes()
    test_task_status_codes()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")
    print("\n📋 状态码规范总结：")
    print("   ✅ 200: 业务逻辑成功/失败（如密码错误、用户不存在）")
    print("   ✅ 201: 资源创建成功")
    print("   ✅ 400: 参数错误、格式错误")
    print("   ✅ 401: JWT token认证失败")
    print("   ✅ 403: 已认证但无权限")
    print("   ✅ 409: 资源冲突")
    print("   ✅ 422: 请求格式正确但语义错误")
    print("   ✅ 500: 服务器内部错误")

if __name__ == "__main__":
    main() 