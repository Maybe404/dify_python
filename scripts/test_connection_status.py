#!/usr/bin/env python3
"""
连接状态测试脚本
测试新添加的健康检查接口是否正常工作
"""

import requests
import json
import time

def test_health_endpoints():
    """测试健康检查接口"""
    base_url = "http://localhost:5000/api"
    
    endpoints = [
        {'name': '健康检查', 'path': '/health', 'method': 'GET'},
        {'name': 'Ping检查', 'path': '/ping', 'method': 'GET'},
        {'name': '状态检查', 'path': '/status', 'method': 'GET'}
    ]
    
    print("🔍 测试健康检查接口...\n")
    
    for endpoint in endpoints:
        print(f"📡 测试 {endpoint['name']} ({endpoint['method']} {endpoint['path']})")
        
        try:
            url = base_url + endpoint['path']
            response = requests.get(url, timeout=5)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功 - {data.get('message', 'N/A')}")
                print(f"   响应时间: {response.elapsed.total_seconds():.3f}秒")
                
                # 打印完整响应数据
                print(f"   完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"   ❌ 失败 - 状态码: {response.status_code}")
                print(f"   响应内容: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 连接失败 - 服务器可能未启动")
        except requests.exceptions.Timeout:
            print(f"   ❌ 请求超时")
        except Exception as e:
            print(f"   ❌ 异常 - {str(e)}")
        
        print()

def test_old_connection_method():
    """测试旧的连接检测方法（用于对比）"""
    print("🔍 测试旧的连接检测方法...\n")
    
    try:
        url = "http://localhost:5000/api/auth/verify-token"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer invalid-token'
        }
        
        print(f"📡 测试 POST {url}")
        response = requests.post(url, headers=headers, timeout=5)
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 401:
            print(f"   ✅ 旧方法仍然有效 - 收到预期的401响应")
        else:
            print(f"   ⚠️  旧方法响应异常 - 状态码: {response.status_code}")
            
        print(f"   响应内容: {response.text}")
        
    except Exception as e:
        print(f"   ❌ 旧方法测试失败 - {str(e)}")
    
    print()

def test_server_availability():
    """简单的服务器可用性测试"""
    print("🔍 测试服务器基本可用性...\n")
    
    try:
        # 测试根路径
        response = requests.get("http://localhost:5000", timeout=5)
        print(f"📡 根路径状态码: {response.status_code}")
        
        if response.status_code == 404:
            print("   ✅ 服务器运行正常（404是预期的，因为没有根路由）")
        else:
            print(f"   ⚠️  意外响应: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到服务器，请确保服务器已启动")
        return False
    except Exception as e:
        print(f"   ❌ 测试异常: {str(e)}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 连接状态功能测试")
    print("=" * 60)
    print()
    
    # 1. 基本服务器可用性测试
    if not test_server_availability():
        print("❌ 服务器不可用，测试终止")
        return
    
    print()
    
    # 2. 健康检查接口测试
    test_health_endpoints()
    
    # 3. 旧连接检测方法测试
    test_old_connection_method()
    
    print("=" * 60)
    print("🎯 测试建议:")
    print("1. 如果健康检查接口都返回200，说明新的连接检测方法正常")
    print("2. 前端应该使用 /api/health 接口来检测连接状态")
    print("3. 如果所有接口都失败，请检查服务器是否已启动")
    print("=" * 60)

if __name__ == "__main__":
    main() 