#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
显示Excel导出文件的存储路径信息
"""

import os
import sys
import time
from pathlib import Path

def show_excel_export_paths():
    """显示Excel导出文件的存储路径"""
    
    print("=== Excel导出文件存储路径信息 ===\n")
    
    # 1. 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(project_root)  # 上一级目录
    print(f"[DIR] 项目根目录: {project_root}")
    
    # 2. 导出基础目录
    export_base_dir = os.path.join(project_root, 'data', 'exports')
    print(f"[DIR] 导出基础目录: {export_base_dir}")
    print(f"      目录是否存在: {'是' if os.path.exists(export_base_dir) else '否'}")
    
    # 3. 模拟用户导出目录
    sample_user_id = "668ea441-82ea-45ce-8bc1-e1bb29c5a5d2"
    user_export_dir = os.path.join(export_base_dir, sample_user_id)
    print(f"[DIR] 用户导出目录: {user_export_dir}")
    print(f"      目录是否存在: {'是' if os.path.exists(user_export_dir) else '否'}")
    
    # 4. 显示现有的导出文件
    if os.path.exists(user_export_dir):
        print(f"\n[FILES] 用户导出目录下的文件:")
        files = os.listdir(user_export_dir)
        if files:
            for file in sorted(files):
                file_path = os.path.join(user_export_dir, file)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    mod_time = os.path.getmtime(file_path)
                    mod_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
                    
                    if file.endswith('.xlsx'):
                        icon = "[EXCEL]"
                        file_type = "Excel文件"
                    elif file.endswith('.pdf'):
                        icon = "[PDF]"
                        file_type = "PDF文件"
                    else:
                        icon = "[FILE]"
                        file_type = "其他文件"
                    
                    print(f"        {icon} {file}")
                    print(f"              类型: {file_type}")
                    print(f"              大小: {file_size:,} 字节")
                    print(f"              修改时间: {mod_time_str}")
                    print()
        else:
            print("        目录为空")
    
    # 5. 模拟Excel文件命名格式
    print("\n[FORMAT] Excel导出文件命名格式:")
    sample_task_id = "cbbb8eb9-c3dc-41e9-9a78-5bc0f01d0363"
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    excel_filename = f"task_results_{sample_task_id}_{timestamp}.xlsx"
    excel_full_path = os.path.join(user_export_dir, excel_filename)
    
    print(f"         文件名格式: task_results_{{任务ID}}_{{时间戳}}.xlsx")
    print(f"         示例文件名: {excel_filename}")
    print(f"         完整路径: {excel_full_path}")
    
    # 6. 路径构建逻辑说明
    print(f"\n[LOGIC] 路径构建逻辑:")
    print(f"        1. 获取app目录: current_app.root_path")
    print(f"        2. 构建导出目录: app目录 + '../data/exports/' + 用户ID")
    print(f"        3. 生成文件名: task_results_{{任务ID}}_{{时间戳}}.xlsx")
    print(f"        4. 完整路径: 导出目录 + 文件名")
    
    # 7. 实际导出时会发生什么
    print(f"\n[PROCESS] Excel导出流程:")
    print(f"          1. 创建用户专属目录: data/exports/{{用户ID}}/")
    print(f"          2. 生成Excel文件并保存到该目录")
    print(f"          3. 通过send_file()直接返回文件给用户下载")
    print(f"          4. 文件会保留在服务器上，可供后续访问")
    
    # 8. 查看现有的Excel文件
    excel_files = []
    if os.path.exists(export_base_dir):
        for root, dirs, files in os.walk(export_base_dir):
            for file in files:
                if file.endswith('.xlsx'):
                    excel_files.append(os.path.join(root, file))
    
    if excel_files:
        print(f"\n[EXCEL] 现有的Excel文件:")
        for excel_file in excel_files:
            rel_path = os.path.relpath(excel_file, project_root)
            file_size = os.path.getsize(excel_file)
            mod_time = os.path.getmtime(excel_file)
            mod_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
            print(f"        [EXCEL] {rel_path}")
            print(f"                大小: {file_size:,} 字节")
            print(f"                修改时间: {mod_time_str}")
    else:
        print(f"\n[EXCEL] 目前没有Excel文件，只有PDF文件")

def show_directory_structure():
    """显示相关目录结构"""
    print("\n" + "="*60)
    print("[TREE] 相关目录结构")
    print("="*60)
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 显示data目录结构
    data_dir = os.path.join(project_root, 'data')
    if os.path.exists(data_dir):
        print("data/")
        for item in sorted(os.listdir(data_dir)):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path):
                print(f"├── {item}/")
                if item == 'exports':
                    # 显示exports子目录
                    try:
                        for subitem in sorted(os.listdir(item_path)):
                            subitem_path = os.path.join(item_path, subitem)
                            if os.path.isdir(subitem_path):
                                print(f"│   ├── {subitem}/")
                                # 显示用户目录下的文件数量
                                try:
                                    files = [f for f in os.listdir(subitem_path) if os.path.isfile(os.path.join(subitem_path, f))]
                                    excel_count = len([f for f in files if f.endswith('.xlsx')])
                                    pdf_count = len([f for f in files if f.endswith('.pdf')])
                                    if excel_count > 0 or pdf_count > 0:
                                        print(f"│   │   ├── Excel文件: {excel_count} 个")
                                        print(f"│   │   └── PDF文件: {pdf_count} 个")
                                except:
                                    pass
                    except:
                        pass

if __name__ == "__main__":
    show_excel_export_paths()
    show_directory_structure() 