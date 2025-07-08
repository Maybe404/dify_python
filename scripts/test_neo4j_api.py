#!/usr/bin/env python3
"""
Neo4j API接口测试脚本
用于测试Neo4j图数据库接口的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Neo4jAPITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        
    def login(self, credential="admin", password="admin123456"):
        """用户登录获取token"""
        print("🔐 正在登录获取访问令牌...")
        
        login_data = {
            "credential": credential,
            "password": password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['data']['access_token']
                print(f"✅ 登录成功！用户: {data['data']['user']['username']}")
                return True
            else:
                print(f"❌ 登录失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 登录请求失败: {str(e)}")
            return False
    
    def get_headers(self):
        """获取带有认证的请求头"""
        if not self.token:
            raise Exception("请先登录获取token")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_neo4j_health(self):
        """测试Neo4j健康检查"""
        print("\n🩺 测试Neo4j健康检查...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/neo4j/health",
                headers=self.get_headers()
            )
            
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if response.status_code == 200 and data.get('success'):
                print("✅ Neo4j健康检查通过")
                return True
            else:
                print("❌ Neo4j健康检查失败")
                return False
                
        except Exception as e:
            print(f"❌ 健康检查请求失败: {str(e)}")
            return False
    
    def test_get_related_data(self, standard_name="ISO27001"):
        """测试获取标准关联数据"""
        print(f"\n🔍 测试获取标准关联数据 (标准: {standard_name})...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/neo4j/related-data",
                params={"standard_name": standard_name},
                headers=self.get_headers()
            )
            
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if response.status_code == 200 and data.get('success'):
                graph_data = data['data']['graph_data']
                print(f"✅ 查询成功！节点数: {len(graph_data['nodes'])}, 边数: {len(graph_data['edges'])}")
                return True
            else:
                print("❌ 查询失败")
                return False
                
        except Exception as e:
            print(f"❌ 查询请求失败: {str(e)}")
            return False
    
    def test_missing_parameter(self):
        """测试缺少参数的情况"""
        print("\n⚠️  测试缺少standard_name参数...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/neo4j/related-data",
                headers=self.get_headers()
            )
            
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if response.status_code == 400:
                print("✅ 正确返回400错误（缺少参数）")
                return True
            else:
                print("❌ 应该返回400错误")
                return False
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            return False
    
    def test_without_token(self):
        """测试没有token的情况"""
        print("\n🚫 测试没有认证token的访问...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/neo4j/related-data",
                params={"standard_name": "ISO27001"}
            )
            
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if response.status_code == 401:
                print("✅ 正确返回401错误（未认证）")
                return True
            else:
                print("❌ 应该返回401错误")
                return False
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Neo4j API接口测试")
        print("=" * 50)
        
        # 测试结果统计
        tests = [
            ("用户登录", lambda: self.login()),
            ("Neo4j健康检查", lambda: self.test_neo4j_health()),
            ("获取标准关联数据", lambda: self.test_get_related_data()),
            ("缺少参数测试", lambda: self.test_missing_parameter()),
            ("无认证访问测试", lambda: self.test_without_token())
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                print("-" * 30)
            except Exception as e:
                print(f"❌ 测试 {test_name} 异常: {str(e)}")
                print("-" * 30)
        
        # 输出测试结果
        print(f"\n📊 测试结果统计:")
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {total - passed}")
        print(f"成功率: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  部分测试失败，请检查相关配置")
        
        return passed == total

def main():
    """主函数"""
    print("Neo4j API接口测试工具")
    print("确保以下服务正在运行:")
    print("1. Flask应用服务器 (http://localhost:5000)")
    print("2. Neo4j数据库服务器")
    print("3. MySQL数据库服务器")
    print()
    
    # 检查环境变量
    required_env_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请在.env文件中配置Neo4j连接信息")
        return False
    
    print("✅ 环境变量检查通过")
    print(f"Neo4j URI: {os.getenv('NEO4J_URI')}")
    print(f"Neo4j 用户: {os.getenv('NEO4J_USER')}")
    print()
    
    # 运行测试
    tester = Neo4jAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 