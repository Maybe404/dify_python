#!/usr/bin/env python3
"""
测试密码验证
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.security import validate_password, validate_registration_data

def test_password_validation():
    """测试密码验证"""
    test_passwords = [
        'TestPassword123!@',     # 16位，包含所有要素
        'TestPassword123!',      # 15位，长度不足
        'TestPassword123!@#',    # 17位，符合要求
        'TestPass123!@##',       # 16位，包含所有要素
        'TestPassword123!@#$%',  # 20位，符合要求
        'testpassword123!@',     # 16位，没有大写字母
        'TESTPASSWORD123!@',     # 16位，没有小写字母
        'TestPassword!@##',      # 16位，没有数字
        'TestPassword123AB',     # 16位，没有符号
        'VeryLongTestPassword123!@#$%^&*', # 32位，符合要求
    ]
    
    print("🔐 测试密码验证规则...")
    print("=" * 50)
    
    for password in test_passwords:
        is_valid, message = validate_password(password)
        status = "✅" if is_valid else "❌"
        print(f"{status} '{password}' (长度:{len(password)}) - {message}")

def test_registration_data():
    """测试注册数据验证"""
    print("\n📝 测试注册数据验证...")
    print("=" * 50)
    
    test_data = {
        'username': 'testuser123',
        'email': 'test@example.com',
        'password': 'TestPass123!@##'  # 16位密码
    }
    
    print(f"测试数据: {test_data}")
    is_valid, errors = validate_registration_data(test_data)
    
    if is_valid:
        print("✅ 注册数据验证通过")
    else:
        print("❌ 注册数据验证失败:")
        for field, error in errors.items():
            print(f"   {field}: {error}")

if __name__ == '__main__':
    test_password_validation()
    test_registration_data() 