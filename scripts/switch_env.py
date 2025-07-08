#!/usr/bin/env python3
"""
环境切换脚本
快速切换开发环境和生产环境配置
"""

import os
import shutil
import argparse
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 环境配置模板
ENV_TEMPLATES = {
    'development': {
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': 'True',
        'description': '开发环境 - 启用调试模式，详细错误信息，自动重载'
    },
    'production': {
        'FLASK_ENV': 'production', 
        'FLASK_DEBUG': 'False',
        'description': '生产环境 - 关闭调试模式，优化性能，隐藏错误详情'
    },
    'testing': {
        'FLASK_ENV': 'testing',
        'FLASK_DEBUG': 'True', 
        'description': '测试环境 - 启用测试模式，使用测试数据库'
    }
}

def read_env_file(file_path):
    """读取环境变量文件"""
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # 处理值中的注释
                    if '#' in value:
                        value = value.split('#')[0].strip()
                    env_vars[key.strip()] = value.strip()
    return env_vars

def write_env_file(file_path, env_vars):
    """写入环境变量文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("# Flask应用配置\n")
        for key, value in env_vars.items():
            if key.startswith('FLASK_'):
                f.write(f"{key}={value}\n")
        
        f.write("\n# JWT令牌配置\n") 
        for key, value in env_vars.items():
            if key.startswith('JWT_'):
                f.write(f"{key}={value}\n")
                
        f.write("\n# 数据库配置\n")
        for key, value in env_vars.items():
            if key.startswith('DB_') or key == 'DATABASE_URL':
                f.write(f"{key}={value}\n")
                
        f.write("\n# 服务器配置\n")
        for key, value in env_vars.items():
            if key in ['HOST', 'PORT']:
                f.write(f"{key}={value}\n")
                
        f.write("\n# 其他配置\n")
        for key, value in env_vars.items():
            if not any(key.startswith(prefix) for prefix in ['FLASK_', 'JWT_', 'DB_']) and key not in ['HOST', 'PORT', 'DATABASE_URL']:
                f.write(f"{key}={value}\n")

def switch_environment(target_env):
    """切换环境"""
    if target_env not in ENV_TEMPLATES:
        print(f"❌ 不支持的环境: {target_env}")
        print(f"支持的环境: {', '.join(ENV_TEMPLATES.keys())}")
        return False
    
    env_file = PROJECT_ROOT / '.env'
    backup_file = PROJECT_ROOT / f'.env.backup.{target_env}'
    
    # 备份当前配置
    if env_file.exists():
        shutil.copy2(env_file, backup_file)
        print(f"📦 已备份当前配置到: {backup_file}")
    
    # 读取当前配置
    current_env = read_env_file(env_file)
    
    # 应用目标环境的配置
    template = ENV_TEMPLATES[target_env]
    current_env.update(template)
    
    # 移除description字段（这个不是环境变量）
    current_env.pop('description', None)
    
    # 写入新配置
    write_env_file(env_file, current_env)
    
    print(f"✅ 环境已切换到: {target_env}")
    print(f"📝 {ENV_TEMPLATES[target_env]['description']}")
    return True

def show_current_environment():
    """显示当前环境"""
    env_file = PROJECT_ROOT / '.env'
    
    if not env_file.exists():
        print("❌ .env文件不存在")
        return
    
    current_env = read_env_file(env_file)
    flask_env = current_env.get('FLASK_ENV', '未知')
    flask_debug = current_env.get('FLASK_DEBUG', '未知')
    
    print(f"📊 当前环境状态:")
    print(f"   FLASK_ENV: {flask_env}")
    print(f"   FLASK_DEBUG: {flask_debug}")
    
    # 判断当前环境类型
    for env_name, template in ENV_TEMPLATES.items():
        if (current_env.get('FLASK_ENV') == template['FLASK_ENV'] and 
            current_env.get('FLASK_DEBUG') == template['FLASK_DEBUG']):
            print(f"   环境类型: {env_name}")
            print(f"   描述: {template['description']}")
            break
    else:
        print("   环境类型: 自定义")

def list_environments():
    """列出所有可用环境"""
    print("🌍 可用环境:")
    for env_name, template in ENV_TEMPLATES.items():
        print(f"  {env_name}:")
        print(f"    FLASK_ENV: {template['FLASK_ENV']}")
        print(f"    FLASK_DEBUG: {template['FLASK_DEBUG']}")
        print(f"    描述: {template['description']}")
        print()

def main():
    parser = argparse.ArgumentParser(description='环境切换脚本')
    parser.add_argument('environment', nargs='?', choices=list(ENV_TEMPLATES.keys()),
                       help='目标环境 (development/production/testing)')
    parser.add_argument('--current', '-c', action='store_true',
                       help='显示当前环境')
    parser.add_argument('--list', '-l', action='store_true', 
                       help='列出所有可用环境')
    
    args = parser.parse_args()
    
    print("🔄 环境切换工具")
    print("=" * 40)
    
    if args.current:
        show_current_environment()
    elif args.list:
        list_environments()
    elif args.environment:
        if switch_environment(args.environment):
            print("\n💡 建议:")
            print("   1. 重启Flask服务器使配置生效")
            print("   2. 运行 python check_config.py 验证配置")
            if args.environment == 'production':
                print("   3. 确认生产环境数据库和安全配置")
    else:
        show_current_environment()
        print("\n使用方法:")
        print("  python scripts/switch_env.py development  # 切换到开发环境")
        print("  python scripts/switch_env.py production   # 切换到生产环境")
        print("  python scripts/switch_env.py --current    # 显示当前环境")
        print("  python scripts/switch_env.py --list       # 列出所有环境")

if __name__ == '__main__':
    main() 