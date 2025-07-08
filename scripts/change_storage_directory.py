#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件存储目录更换工具
用于更换项目的文件存储目录，包括上传文件、导出文件等
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("📁 文件存储目录更换工具")
    print("=" * 60)

def get_current_config():
    """获取当前配置"""
    from app.config.config import Config
    
    return {
        'data_root': Config.get_data_directory(),
        'upload_dir': Config.get_upload_directory(),
        'export_dir': Config.get_export_directory(),
        'temp_dir': Config.get_temp_directory()
    }

def show_current_config():
    """显示当前配置"""
    print("\n📋 当前文件存储配置:")
    print("-" * 40)
    
    try:
        config = get_current_config()
        print(f"数据根目录: {config['data_root']}")
        print(f"上传文件目录: {config['upload_dir']}")
        print(f"导出文件目录: {config['export_dir']}")
        print(f"临时文件目录: {config['temp_dir']}")
        
        # 显示目录状态
        print("\n📊 目录状态:")
        for name, path in config.items():
            exists = os.path.exists(path)
            status = "✅ 存在" if exists else "❌ 不存在"
            if exists:
                try:
                    files = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
                    dirs = len([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
                    size_info = f" ({files} 文件, {dirs} 目录)"
                except:
                    size_info = ""
                status += size_info
            print(f"  {name.replace('_', ' ').title()}: {status}")
            
    except Exception as e:
        print(f"❌ 获取配置失败: {str(e)}")

def update_env_file(new_config):
    """更新.env文件"""
    env_file = os.path.join(project_root, '.env')
    env_example_file = os.path.join(project_root, 'env_example.txt')
    
    # 如果.env不存在，从示例文件复制
    if not os.path.exists(env_file):
        if os.path.exists(env_example_file):
            shutil.copy2(env_example_file, env_file)
            print(f"✅ 已从 {env_example_file} 创建 .env 文件")
        else:
            print("❌ 未找到 .env 文件或 env_example.txt 文件")
            return False
    
    # 读取现有配置
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新配置
    updated_lines = []
    config_keys = {
        'DATA_ROOT_DIR': new_config.get('data_root', ''),
        'UPLOAD_FILES_DIR': new_config.get('upload_dir', ''),
        'EXPORT_FILES_DIR': new_config.get('export_dir', ''),
        'TEMP_FILES_DIR': new_config.get('temp_dir', '')
    }
    
    for line in lines:
        line_updated = False
        for key, value in config_keys.items():
            if line.startswith(f"{key}="):
                updated_lines.append(f"{key}={value}\n")
                line_updated = True
                break
        
        if not line_updated:
            updated_lines.append(line)
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print(f"✅ 已更新 .env 文件")
    return True

def migrate_files(old_path, new_path, dry_run=False):
    """迁移文件"""
    if not os.path.exists(old_path):
        print(f"⚠️ 源目录不存在: {old_path}")
        return True
    
    if old_path == new_path:
        print(f"ℹ️ 路径未变化，跳过迁移: {old_path}")
        return True
    
    if os.path.exists(new_path):
        print(f"⚠️ 目标目录已存在: {new_path}")
        response = input("是否合并到现有目录？(y/N): ").lower()
        if response != 'y':
            return False
    
    try:
        if dry_run:
            print(f"[模拟] 迁移: {old_path} -> {new_path}")
            return True
        
        # 创建目标目录
        os.makedirs(new_path, exist_ok=True)
        
        # 移动文件
        for item in os.listdir(old_path):
            src = os.path.join(old_path, item)
            dst = os.path.join(new_path, item)
            
            if os.path.isdir(src):
                if os.path.exists(dst):
                    # 如果目标目录存在，递归合并
                    migrate_files(src, dst, dry_run)
                else:
                    shutil.move(src, dst)
            else:
                if os.path.exists(dst):
                    print(f"⚠️ 文件已存在，跳过: {dst}")
                else:
                    shutil.move(src, dst)
        
        # 如果源目录为空，删除它
        try:
            os.rmdir(old_path)
            print(f"✅ 已删除空目录: {old_path}")
        except OSError:
            print(f"ℹ️ 源目录不为空，保留: {old_path}")
        
        print(f"✅ 迁移完成: {old_path} -> {new_path}")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        return False

def interactive_mode():
    """交互式模式"""
    print("\n🔧 交互式配置模式")
    print("请输入新的存储路径（留空保持当前配置）:")
    
    current_config = get_current_config()
    new_config = {}
    
    # 数据根目录
    current_root = current_config['data_root']
    new_root = input(f"数据根目录 (当前: {current_root}): ").strip()
    if new_root:
        new_config['data_root'] = new_root
    
    # 上传目录
    current_upload = current_config['upload_dir']
    new_upload = input(f"上传文件目录 (当前: {current_upload}): ").strip()
    if new_upload:
        new_config['upload_dir'] = new_upload
    
    # 导出目录
    current_export = current_config['export_dir']
    new_export = input(f"导出文件目录 (当前: {current_export}): ").strip()
    if new_export:
        new_config['export_dir'] = new_export
    
    # 临时目录
    current_temp = current_config['temp_dir']
    new_temp = input(f"临时文件目录 (当前: {current_temp}): ").strip()
    if new_temp:
        new_config['temp_dir'] = new_temp
    
    if not new_config:
        print("ℹ️ 未指定任何新路径，退出")
        return
    
    print(f"\n📝 配置变更预览:")
    for key, value in new_config.items():
        old_value = current_config[key]
        print(f"  {key.replace('_', ' ').title()}: {old_value} -> {value}")
    
    # 确认变更
    confirm = input("\n确认应用这些变更？(y/N): ").lower()
    if confirm != 'y':
        print("❌ 已取消")
        return
    
    # 询问是否迁移文件
    migrate = input("是否迁移现有文件到新目录？(y/N): ").lower()
    migrate_files_flag = migrate == 'y'
    
    # 应用变更
    apply_changes(current_config, new_config, migrate_files_flag)

def apply_changes(current_config, new_config, migrate_files_flag=False, dry_run=False):
    """应用配置变更"""
    print(f"\n🚀 {'模拟' if dry_run else '应用'}配置变更...")
    
    # 更新环境变量文件
    if not dry_run:
        if not update_env_file(new_config):
            print("❌ 更新配置文件失败")
            return False
    
    # 迁移文件
    if migrate_files_flag:
        print("\n📦 开始文件迁移...")
        for key, new_path in new_config.items():
            old_path = current_config[key]
            if not migrate_files(old_path, new_path, dry_run):
                print(f"❌ 迁移失败: {key}")
                return False
    
    if not dry_run:
        print("\n✅ 配置变更完成！")
        print("⚠️ 请重启应用以使新配置生效")
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='文件存储目录更换工具')
    parser.add_argument('--data-root', help='新的数据根目录')
    parser.add_argument('--upload-dir', help='新的上传文件目录')
    parser.add_argument('--export-dir', help='新的导出文件目录')
    parser.add_argument('--temp-dir', help='新的临时文件目录')
    parser.add_argument('--migrate', action='store_true', help='迁移现有文件')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行，不实际执行')
    parser.add_argument('--show-config', action='store_true', help='仅显示当前配置')
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.show_config:
        show_current_config()
        return
    
    # 如果没有参数，进入交互模式
    if not any([args.data_root, args.upload_dir, args.export_dir, args.temp_dir]):
        show_current_config()
        interactive_mode()
        return
    
    # 命令行模式
    current_config = get_current_config()
    new_config = {}
    
    if args.data_root:
        new_config['data_root'] = args.data_root
    if args.upload_dir:
        new_config['upload_dir'] = args.upload_dir
    if args.export_dir:
        new_config['export_dir'] = args.export_dir
    if args.temp_dir:
        new_config['temp_dir'] = args.temp_dir
    
    if new_config:
        apply_changes(current_config, new_config, args.migrate, args.dry_run)
    else:
        show_current_config()

if __name__ == "__main__":
    main() 