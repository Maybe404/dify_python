import re
from email_validator import validate_email, EmailNotValidError

def validate_password(password):
    """
    验证密码强度
    要求：大于等于12位，包含大小写字母、数字和特殊字符
    """
    if len(password) < 12:
        return False, "密码长度必须大于等于12个字符"
    
    if not re.search(r'[A-Z]', password):
        return False, "密码必须包含大写字母"
    
    if not re.search(r'[a-z]', password):
        return False, "密码必须包含小写字母"
    
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?~`]', password):
        return False, "密码必须包含特殊字符"
    
    return True, "密码验证通过"

def validate_username(username):
    """
    验证用户名
    要求：3-20个字符，只能包含字母、数字和下划线
    """
    if len(username) < 3 or len(username) > 20:
        return False, "用户名长度必须在3-20个字符之间"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "用户名只能包含字母、数字和下划线"
    
    return True, "用户名验证通过"

def validate_email_format(email):
    """
    验证邮箱格式
    """
    try:
        validate_email(email)
        return True, "邮箱格式正确"
    except EmailNotValidError as e:
        return False, f"邮箱格式错误: {str(e)}"

def validate_registration_data(data):
    """
    验证注册数据
    """
    errors = {}
    
    # 验证用户名（可选）
    if 'username' in data and data['username']:
        is_valid, message = validate_username(data['username'])
        if not is_valid:
            errors['username'] = message
    
    # 验证邮箱（必填）
    if 'email' not in data or not data['email']:
        errors['email'] = "邮箱不能为空"
    else:
        is_valid, message = validate_email_format(data['email'])
        if not is_valid:
            errors['email'] = message
    
    # 验证密码
    if 'password' not in data or not data['password']:
        errors['password'] = "密码不能为空"
    else:
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            errors['password'] = message
    
    return len(errors) == 0, errors 