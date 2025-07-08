#!/usr/bin/env python3
"""
前端登出功能测试脚本
测试前端页面的登出行为是否正确
"""

import sys
import os
import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import threading
import subprocess

class FrontendLogoutTester:
    """前端登出功能测试器"""
    
    def __init__(self):
        self.driver = None
        self.server_process = None
        self.base_url = "http://localhost:5000"
        self.frontend_url = "file://" + os.path.abspath("web_test/index.html")
        
    def start_server(self):
        """启动后端服务器"""
        print("🚀 启动后端服务器...")
        try:
            # 启动Flask应用
            self.server_process = subprocess.Popen(
                [sys.executable, "run.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            
            # 等待服务器启动
            time.sleep(3)
            
            # 检查服务器是否启动成功
            try:
                response = requests.get(f"{self.base_url}/api/auth/verify-token", timeout=5)
                print("✅ 后端服务器启动成功")
                return True
            except:
                print("❌ 后端服务器启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动服务器异常: {e}")
            return False
    
    def setup_browser(self):
        """设置浏览器"""
        print("🌐 设置浏览器...")
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # 尝试启动Chrome浏览器
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ 浏览器设置成功")
            return True
            
        except Exception as e:
            print(f"❌ 浏览器设置失败: {e}")
            print("ℹ️  请确保已安装Chrome浏览器和ChromeDriver")
            return False
    
    def test_frontend_logout(self):
        """测试前端登出功能"""
        print("🧪 开始前端登出功能测试...")
        
        try:
            # 打开前端页面
            print("\n1. 打开前端测试页面...")
            self.driver.get(self.frontend_url)
            
            # 等待页面加载
            wait = WebDriverWait(self.driver, 10)
            
            # 生成测试用户数据
            print("\n2. 生成测试用户数据...")
            generate_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '生成测试用户数据')]")))
            generate_btn.click()
            time.sleep(1)
            
            # 注册用户
            print("\n3. 注册测试用户...")
            register_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '注册')]")
            register_btn.click()
            time.sleep(2)
            
            # 登录用户
            print("\n4. 登录测试用户...")
            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '登录')]")
            login_btn.click()
            time.sleep(2)
            
            # 检查登录状态
            print("\n5. 检查登录状态...")
            login_status = self.driver.find_element(By.ID, "login-status")
            if "已登录" in login_status.text:
                print("✅ 用户成功登录")
            else:
                print("❌ 用户登录失败")
                return False
            
            # 检查用户信息是否显示
            try:
                user_info = self.driver.find_element(By.ID, "user-info")
                if user_info.is_displayed():
                    print("✅ 用户信息正确显示")
                else:
                    print("❌ 用户信息未显示")
                    return False
            except:
                print("❌ 找不到用户信息元素")
                return False
            
            # 执行登出
            print("\n6. 执行登出操作...")
            logout_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '登出')]")
            logout_btn.click()
            time.sleep(2)
            
            # 检查登出后的状态
            print("\n7. 检查登出后状态...")
            
            # 检查登录状态是否变为未登录
            login_status = self.driver.find_element(By.ID, "login-status")
            if "未登录" in login_status.text:
                print("✅ 登录状态正确更新为'未登录'")
            else:
                print(f"❌ 登录状态未正确更新: {login_status.text}")
                return False
            
            # 检查用户信息是否隐藏
            user_info = self.driver.find_element(By.ID, "user-info")
            if not user_info.is_displayed():
                print("✅ 用户信息正确隐藏")
            else:
                print("❌ 用户信息未正确隐藏")
                return False
            
            # 尝试访问需要认证的功能
            print("\n8. 测试需要认证的功能是否被正确阻止...")
            
            # 尝试获取用户信息
            profile_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '获取用户信息')]")
            profile_btn.click()
            time.sleep(1)
            
            # 检查是否显示错误信息
            profile_result = self.driver.find_element(By.ID, "profile-result")
            if "请先登录" in profile_result.text or "error" in profile_result.get_attribute("class"):
                print("✅ 获取用户信息正确被阻止")
            else:
                print("❌ 获取用户信息未被正确阻止")
                return False
            
            print("\n🎉 前端登出功能测试全部通过！")
            return True
            
        except Exception as e:
            print(f"❌ 前端测试异常: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        print("\n🧹 清理资源...")
        
        if self.driver:
            self.driver.quit()
            print("✅ 浏览器已关闭")
        
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ 服务器已停止")
    
    def run_test(self):
        """运行完整测试"""
        print("🚀 开始前端登出功能完整测试...")
        print("=" * 80)
        
        success = False
        
        try:
            # 1. 启动服务器
            if not self.start_server():
                return False
            
            # 2. 设置浏览器
            if not self.setup_browser():
                return False
            
            # 3. 测试前端登出功能
            success = self.test_frontend_logout()
            
        except KeyboardInterrupt:
            print("\n⚠️  测试被用户中断")
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
        finally:
            self.cleanup()
        
        if success:
            print("\n🎉 前端登出功能测试成功！")
            print("✅ 登出后用户状态正确更新")
            print("✅ 登出后用户信息正确隐藏")
            print("✅ 登出后需要认证的功能正确被阻止")
        else:
            print("\n⚠️  前端登出功能测试失败")
            print("💡 建议：检查前端JavaScript代码中的登出逻辑")
        
        return success

def main():
    """主函数"""
    
    # 检查是否有必要的依赖
    try:
        from selenium import webdriver
    except ImportError:
        print("❌ 缺少selenium依赖")
        print("📦 请安装: pip install selenium")
        return False
    
    tester = FrontendLogoutTester()
    return tester.run_test()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 