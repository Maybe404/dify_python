from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app.models.user import User
from app.utils.security import validate_registration_data
from sqlalchemy.exc import IntegrityError
import time
import json

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

# 用于存储已撤销的token（生产环境建议使用Redis）
revoked_tokens = set()

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    start_time = time.time()
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # 记录请求开始
    current_app.logger.info(f"[请求开始] 用户注册 - IP: {client_ip} - User-Agent: {user_agent[:100]}")
    
    try:
        data = request.get_json()
        
        # 记录请求数据（隐藏敏感信息）
        safe_data = {k: v if k != 'password' else '***' for k, v in (data or {}).items()}
        current_app.logger.info(f"[请求数据] 注册请求数据: {json.dumps(safe_data, ensure_ascii=False)}")
        
        if not data:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.warning(f"[请求失败] 注册失败 - 无效JSON数据 - IP: {client_ip} - 耗时: {elapsed_time}ms")
            return jsonify({
                'success': False,
                'message': '请提供有效的JSON数据'
            }), 400
        
        username = data.get('username', '')
        email = data.get('email', '')
        
        # 验证数据
        is_valid, errors = validate_registration_data(data)
        if not is_valid:
            # 构建包含具体错误信息的message
            error_details = []
            for field, error_msg in errors.items():
                error_details.append(f"{field}: {error_msg}")
            detailed_message = f"数据验证失败: {'; '.join(error_details)}"
            
            current_app.logger.warning(f"注册失败 - 数据验证失败 - 用户名: {username} - IP: {client_ip} - 错误: {errors}")
            return jsonify({
                'success': False,
                'message': detailed_message,
                'errors': errors
            }), 400
        
        # 检查用户名是否已存在（如果提供了用户名）
        if username and User.find_by_username(username):
            current_app.logger.warning(f"注册失败 - 用户名已存在 - 用户名: {username} - IP: {client_ip}")
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 409
        
        # 检查邮箱是否已存在
        if User.find_by_email(email):
            current_app.logger.warning(f"注册失败 - 邮箱已被注册 - 邮箱: {email} - IP: {client_ip}")
            return jsonify({
                'success': False,
                'message': '邮箱已被注册'
            }), 409
        
        # 创建新用户
        user = User(
            username=username if username else None,
            email=email
        )
        user.password = data['password']  # 自动加密
        
        try:
            user.save()
            
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            response_data = {
                'success': True,
                'message': '注册成功',
                'data': {
                    'user': user.to_dict()
                }
            }
            
            # 记录成功响应
            current_app.logger.info(f"[请求成功] 用户注册成功 - 用户ID: {user.id} - 用户名: {username} - 邮箱: {email} - IP: {client_ip} - 耗时: {elapsed_time}ms")
            current_app.logger.info(f"[响应数据] 注册成功响应: {json.dumps(response_data, ensure_ascii=False, default=str)}")
            
            return jsonify(response_data), 201
            
        except IntegrityError as e:
            current_app.logger.error(f"注册失败 - 数据库完整性错误 - 用户名: {username} - 邮箱: {email} - IP: {client_ip} - 错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': '用户名或邮箱已存在'
            }), 409
            
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"注册失败 - 系统错误 - IP: {client_ip} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    start_time = time.time()
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # 记录请求开始
    current_app.logger.info(f"[请求开始] 用户登录 - IP: {client_ip} - User-Agent: {user_agent[:100]}")
    
    try:
        data = request.get_json()
        
        # 记录请求数据（隐藏密码）
        safe_data = {k: v if k != 'password' else '***' for k, v in (data or {}).items()}
        current_app.logger.info(f"[请求数据] 登录请求数据: {json.dumps(safe_data, ensure_ascii=False)}")
        
        if not data:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.warning(f"[请求失败] 登录失败 - 无效JSON数据 - IP: {client_ip} - 耗时: {elapsed_time}ms")
            return jsonify({
                'success': False,
                'message': '请提供有效的JSON数据'
            }), 400
        
        # 获取登录凭证和密码
        credential = data.get('credential', '').strip()  # 可以是用户名或邮箱
        password = data.get('password', '')
        
        if not credential or not password:
            current_app.logger.warning(f"登录失败 - 缺少凭证或密码 - 凭证: {credential} - IP: {client_ip}")
            return jsonify({
                'success': False,
                'message': '请提供用户名/邮箱和密码'
            }), 400
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.find_by_username(credential) or User.find_by_email(credential)
        
        if not user:
            current_app.logger.warning(f"登录失败 - 用户不存在 - 凭证: {credential} - IP: {client_ip}")
            return jsonify({
                'success': False,
                'message': '用户名/邮箱或密码错误'
            }), 200
        
        # 检查用户是否被禁用
        if not user.is_active:
            current_app.logger.warning(f"登录失败 - 账户已被禁用 - 用户ID: {user.id} - 用户名: {user.username} - IP: {client_ip}")
            return jsonify({
                'success': False,
                'message': '账户已被禁用'
            }), 200
        
        # 验证密码
        if not user.check_password(password):
            current_app.logger.warning(f"登录失败 - 密码错误 - 用户ID: {user.id} - 用户名: {user.username} - IP: {client_ip}")
            return jsonify({
                'success': False,
                'message': '用户名/邮箱或密码错误'
            }), 200
        
        # 更新最后登录时间
        user.update_last_login()
        
        # 创建访问令牌
        access_token = create_access_token(identity=user.id)
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '登录成功',
            'data': {
                'user': user.to_dict(),
                'access_token': access_token
            }
        }
        
        # 记录成功响应（隐藏token）
        import copy
        safe_response = copy.deepcopy(response_data)
        if 'data' in safe_response and 'access_token' in safe_response['data']:
            safe_response['data']['access_token'] = f"{access_token[:20]}...{access_token[-10:]}"
        
        current_app.logger.info(f"[请求成功] 用户登录成功 - 用户ID: {user.id} - 用户名: {user.username} - IP: {client_ip} - 耗时: {elapsed_time}ms")
        current_app.logger.info(f"[响应数据] 登录成功响应: {json.dumps(safe_response, ensure_ascii=False, default=str)}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"登录失败 - 系统错误 - IP: {client_ip} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    start_time = time.time()
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # 记录请求开始
    current_app.logger.info(f"[请求开始] 用户登出 - IP: {client_ip} - User-Agent: {user_agent[:100]}")
    
    try:
        # 获取当前用户信息
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        current_app.logger.info(f"[请求数据] 登出用户: {user.username if user else 'Unknown'} - 用户ID: {current_user_id}")
        
        # 获取当前JWT的jti（JWT ID）
        jti = get_jwt()['jti']
        
        # 将token添加到撤销列表
        revoked_tokens.add(jti)
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '登出成功'
        }
        
        current_app.logger.info(f"[请求成功] 用户登出成功 - 用户ID: {current_user_id} - 用户名: {user.username if user else 'Unknown'} - IP: {client_ip} - 耗时: {elapsed_time}ms")
        current_app.logger.info(f"[响应数据] 登出成功响应: {json.dumps(response_data, ensure_ascii=False)}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"登出失败 - 系统错误 - IP: {client_ip} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'登出失败: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    start_time = time.time()
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # 记录请求开始
    current_app.logger.info(f"[请求开始] 获取用户信息 - IP: {client_ip} - User-Agent: {user_agent[:100]}")
    
    try:
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        current_app.logger.info(f"[请求数据] 请求用户信息 - 用户ID: {current_user_id}")
        
        # 注意：token撤销检查现在由全局中间件处理，这里无需手动检查
        
        # 查找用户
        user = User.find_by_id(current_user_id)
        if not user:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.warning(f"[请求失败] 获取用户信息失败 - 用户不存在 - 用户ID: {current_user_id} - IP: {client_ip} - 耗时: {elapsed_time}ms")
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 200
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '获取用户信息成功',
            'data': {
                'user': user.to_dict()
            }
        }
        
        current_app.logger.info(f"[请求成功] 获取用户信息成功 - 用户ID: {current_user_id} - 用户名: {user.username} - IP: {client_ip} - 耗时: {elapsed_time}ms")
        current_app.logger.debug(f"[响应数据] 用户信息响应: {json.dumps(response_data, ensure_ascii=False, default=str)}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"获取用户信息失败 - 系统错误 - IP: {client_ip} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

@auth_bp.route('/verify-token', methods=['POST'])
@jwt_required()
def verify_token():
    """验证Token有效性"""
    start_time = time.time()
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # 记录请求开始
    current_app.logger.info(f"[请求开始] Token验证 - IP: {client_ip} - User-Agent: {user_agent[:100]}")
    
    try:
        # 记录Authorization header (隐藏敏感部分)
        auth_header = request.headers.get('Authorization', '')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token_preview = auth_header[:20] + '...' + auth_header[-10:] if len(auth_header) > 30 else auth_header
            else:
                token_preview = auth_header[:50] + '...' if len(auth_header) > 50 else auth_header
            current_app.logger.info(f"[请求数据] Authorization头: {token_preview}")
        else:
            current_app.logger.warning(f"[请求数据] 缺少Authorization头")
        
        # 注意：token撤销检查现在由全局中间件处理，这里无需手动检查
        
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.warning(f"[请求失败] Token验证失败 - 用户不存在 - 用户ID: {current_user_id} - IP: {client_ip} - 耗时: {elapsed_time}ms")
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 200
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': 'Token有效',
            'data': {
                'user_id': current_user_id,
                'username': user.username
            }
        }
        
        current_app.logger.info(f"[请求成功] Token验证成功 - 用户ID: {current_user_id} - 用户名: {user.username} - IP: {client_ip} - 耗时: {elapsed_time}ms")
        current_app.logger.info(f"[响应数据] Token验证响应: {json.dumps(response_data, ensure_ascii=False)}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"Token验证失败 - 系统错误 - IP: {client_ip} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Token验证失败: {str(e)}'
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """忘记密码 - 生成重置令牌"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供有效的JSON数据'
            }), 400
        
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({
                'success': False,
                'message': '请提供邮箱地址'
            }), 400
        
        # 查找用户
        user = User.find_by_email(email)
        
        if not user:
            # 为了安全考虑，即使用户不存在也返回成功消息
            return jsonify({
                'success': True,
                'message': '如果该邮箱已注册，您将收到密码重置链接'
            }), 200
        
        # 检查用户是否被禁用
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': '账户已被禁用，无法重置密码'
            }), 403
        
        # 生成重置令牌（1小时有效期）
        reset_token = user.generate_reset_token(expires_in=3600)
        
        return jsonify({
            'success': True,
            'message': '密码重置令牌已生成',
            'data': {
                'reset_token': reset_token,
                'expires_in': 3600,
                'note': '请在1小时内使用此令牌重置密码'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成重置令牌失败: {str(e)}'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供有效的JSON数据'
            }), 400
        
        reset_token = data.get('reset_token', '').strip()
        new_password = data.get('new_password', '')
        
        if not reset_token or not new_password:
            return jsonify({
                'success': False,
                'message': '请提供重置令牌和新密码'
            }), 400
        
        # 验证新密码强度
        from app.utils.security import validate_password
        is_valid, error_message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': f'密码不符合要求: {error_message}'
            }), 400
        
        # 查找用户
        user = User.find_by_reset_token(reset_token)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '无效的重置令牌'
            }), 400
        
        # 重置密码
        if user.reset_password(new_password, reset_token):
            return jsonify({
                'success': True,
                'message': '密码重置成功，请使用新密码登录'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '重置令牌已过期或无效'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'密码重置失败: {str(e)}'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码（需要登录）"""
    try:
        # 注意：token撤销检查现在由全局中间件处理，这里无需手动检查
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供有效的JSON数据'
            }), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'message': '请提供当前密码和新密码'
            }), 400
        
        # 验证新密码强度
        from app.utils.security import validate_password
        is_valid, error_message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': f'新密码不符合要求: {error_message}'
            }), 400
        
        # 获取当前用户
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 200
        
        # 验证当前密码
        if not user.check_password(current_password):
            return jsonify({
                'success': False,
                'message': '当前密码错误'
            }), 200
        
        # 检查新密码是否与当前密码相同
        if user.check_password(new_password):
            return jsonify({
                'success': False,
                'message': '新密码不能与当前密码相同'
            }), 400
        
        # 更新密码
        user.password = new_password
        user.save()
        
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'密码修改失败: {str(e)}'
        }), 500 