#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Excel导出功能 - 修复后的验证
"""

import requests
import json
import time
import os
import sys

def test_excel_export():
    """测试Excel导出功能"""
    
    # API配置
    BASE_URL = "http://localhost:5000"
    
    # 测试用户登录信息
    test_user = {
        "email": "admintest@qq.com",
        "password": "admin123456"
    }
    
    print("=== Excel导出功能测试（修复后） ===\n")
    
    try:
        # 1. 登录获取token
        print("1. 正在登录...")
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"响应: {login_response.text}")
            return False
        
        login_data = login_response.json()
        if not login_data.get('success'):
            print(f"❌ 登录失败: {login_data.get('message')}")
            return False
        
        token = login_data['data']['access_token']
        user_info = login_data['data']['user']
        print(f"✅ 登录成功 - 用户: {user_info['username']} ({user_info['email']})")
        
        # 2. 获取任务列表
        print("\n2. 获取任务列表...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        tasks_response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
        
        if tasks_response.status_code != 200:
            print(f"❌ 获取任务列表失败: {tasks_response.status_code}")
            return False
        
        tasks_data = tasks_response.json()
        if not tasks_data.get('success'):
            print(f"❌ 获取任务列表失败: {tasks_data.get('message')}")
            return False
        
        tasks = tasks_data['data']['tasks']
        print(f"✅ 获取到 {len(tasks)} 个任务")
        
        if not tasks:
            print("❌ 没有可用的任务进行测试")
            return False
        
        # 3. 选择一个已完成的任务进行测试
        test_task = None
        for task in tasks:
            if task['status'] == 'completed':
                test_task = task
                break
        
        if not test_task:
            print("❌ 没有找到已完成的任务")
            return False
        
        task_id = test_task['id']
        print(f"✅ 选择任务: {task_id} ({test_task['task_type']})")
        
        # 4. 测试Excel导出
        print(f"\n3. 测试Excel导出 - 任务ID: {task_id}")
        start_time = time.time()
        
        export_response = requests.get(
            f"{BASE_URL}/api/tasks/{task_id}/results/export-excel",
            headers=headers,
            stream=True  # 用于下载文件
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"响应状态码: {export_response.status_code}")
        print(f"响应头: {dict(export_response.headers)}")
        print(f"请求耗时: {elapsed_time:.2f}秒")
        
        if export_response.status_code == 200:
            # 检查是否是Excel文件
            content_type = export_response.headers.get('Content-Type', '')
            content_disposition = export_response.headers.get('Content-Disposition', '')
            
            print(f"Content-Type: {content_type}")
            print(f"Content-Disposition: {content_disposition}")
            
            if 'spreadsheet' in content_type or 'excel' in content_type:
                # 保存文件
                filename = f"test_export_{task_id}_{int(time.time())}.xlsx"
                with open(filename, 'wb') as f:
                    for chunk in export_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(filename)
                print(f"✅ Excel导出成功!")
                print(f"   文件名: {filename}")
                print(f"   文件大小: {file_size} 字节")
                
                # 删除测试文件
                os.remove(filename)
                print(f"   测试文件已清理")
                
                return True
            else:
                print(f"❌ 返回的不是Excel文件，Content-Type: {content_type}")
                print(f"响应内容: {export_response.text[:500]}")
                return False
        else:
            print(f"❌ Excel导出失败: HTTP {export_response.status_code}")
            print(f"响应内容: {export_response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保Flask应用正在运行 (http://localhost:5000)")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_document_service():
    """检查DocumentService是否有export_task_results_to_excel方法"""
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.services.document_service import DocumentService
        
        if hasattr(DocumentService, 'export_task_results_to_excel'):
            print("✅ DocumentService.export_task_results_to_excel 方法存在")
            return True
        else:
            print("❌ DocumentService.export_task_results_to_excel 方法不存在")
            return False
    except Exception as e:
        print(f"❌ 检查DocumentService时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("检查DocumentService...")
    service_ok = check_document_service()
    
    if service_ok:
        print("\n" + "="*50)
        success = test_excel_export()
        
        print("\n" + "="*50)
        if success:
            print("🎉 Excel导出功能测试通过!")
        else:
            print("❌ Excel导出功能测试失败!")
    else:
        print("❌ DocumentService检查失败，请先确保服务正常") 