from flask import Blueprint, request, Response, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import time
from app.models.user import User
from app.services.dify_app_service import DifyAppService

# 创建Dify V2 API转发蓝图 - 支持应用场景参数
dify_v2_bp = Blueprint('dify_v2', __name__)

# 新增：为向后兼容，添加旧的路由到新的 V2 接口
@dify_v2_bp.route('/chat-simple', methods=['POST'])
@jwt_required()
def chat_simple_legacy():
    """
    Dify聊天接口 - 向后兼容路由
    自动转发到 multilingual_qa 场景
    """
    current_app.logger.warning("[Dify兼容路由] 使用了旧路由 /api/dify/v2/chat-simple，建议使用场景路由")
    return chat_simple_v2('multilingual_qa')

@dify_v2_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations_legacy():
    """
    获取会话列表接口 - 向后兼容路由
    自动转发到 multilingual_qa 场景
    """
    current_app.logger.warning("[Dify兼容路由] 使用了旧路由 /api/dify/v2/conversations，建议使用场景路由")
    return get_conversations_v2('multilingual_qa')

@dify_v2_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages_legacy():
    """
    获取消息历史接口 - 向后兼容路由
    自动转发到 multilingual_qa 场景
    """
    current_app.logger.warning("[Dify兼容路由] 使用了旧路由 /api/dify/v2/messages，建议使用场景路由")
    return get_messages_v2('multilingual_qa')

@dify_v2_bp.route('/config', methods=['GET'])
@jwt_required()
def get_config_legacy():
    """
    获取配置信息接口 - 向后兼容路由
    返回所有场景的配置信息
    """
    current_app.logger.warning("[Dify兼容路由] 使用了旧路由 /api/dify/v2/config，建议使用   场景路由")
    return get_scenarios()

@dify_v2_bp.route('/<scenario>/chat-simple', methods=['POST'])
@jwt_required()
def chat_simple_v2(scenario):
    """
    Dify聊天接口 V2 - 支持应用场景参数
    
    URL示例:
    - POST /api/dify/v2/multilingual_qa/chat-simple  (多语言问答)
    - POST /api/dify/v2/standard_query/chat-simple   (标准查询)
    """
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 验证应用场景
    valid_scenarios = [s['key'] for s in DifyAppService.get_all_scenarios()]
    if scenario not in valid_scenarios:
        current_app.logger.error(f"不支持的应用场景: {scenario}，支持的场景: {valid_scenarios}")
        return jsonify({
            'success': False,
            'message': f'不支持的应用场景: {scenario}',
            'valid_scenarios': valid_scenarios
        }), 400
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user:
        current_app.logger.warning(f"Dify V2聊天请求失败 - 用户不存在 - 用户ID: {current_user_id} - IP: {client_ip}")
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 200
    
    if not user.is_active:
        current_app.logger.warning(f"Dify V2聊天请求失败 - 用户已被禁用 - 用户ID: {current_user_id} - IP: {client_ip}")
        return jsonify({
            'success': False,
            'message': '账户已被禁用'
        }), 403
    
    current_app.logger.info(f"[Dify V2聊天请求] 场景: {scenario} - 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供有效的JSON数据'
            }), 400
        
        # 准备用户信息
        user_info = {
            'id': user.id,
            'username': user.username or user.email,
            'email': user.email
        }
        
        # 使用DifyAppService转发请求
        success, response, status_code = DifyAppService.forward_request(
            scenario=scenario,
            api_type='chat',
            request_method='POST',
            json_data=data,
            user_info=user_info,
            stream=True
        )
        
        if not success:
            current_app.logger.error(f"[Dify V2 API失败] 场景: {scenario} - 状态码: {status_code} - 响应: {response}")
            return jsonify({
                'success': False,
                'message': f'Dify API请求失败: {status_code}',
                'details': response
            }), status_code
        
        def generate():
            try:
                # 直接转发Dify原始响应，不做任何处理
                for chunk in response.iter_content(chunk_size=8192, decode_unicode=False):
                    if chunk:
                        yield chunk
            except Exception as e:
                current_app.logger.error(f"[Dify V2流式错误] 场景: {scenario} - 用户: {user.username or user.email} - 错误: {str(e)}")
                # 只记录错误，不注入到响应流中
            finally:
                elapsed_time = round((time.time() - start_time) * 1000, 2)
                current_app.logger.info(f"[Dify V2请求完成] 场景: {scenario} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
        
        return Response(
            generate(),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            }
        )
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"[Dify V2系统错误] 场景: {scenario} - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'系统错误: {str(e)}'
        }), 500

@dify_v2_bp.route('/<scenario>/conversations', methods=['GET'])
@jwt_required()
def get_conversations_v2(scenario):
    """
    获取会话列表接口 V2 - 支持应用场景参数
    
    URL示例:
    - GET /api/dify/v2/multilingual_qa/conversations  (多语言问答)
    - GET /api/dify/v2/standard_query/conversations   (标准查询)
    """
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 验证应用场景
    if scenario not in [s['key'] for s in DifyAppService.get_all_scenarios()]:
        return jsonify({
            'success': False,
            'message': f'不支持的应用场景: {scenario}'
        }), 400
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user:
        current_app.logger.warning(f"Dify V2会话列表请求失败 - 用户不存在 - 用户ID: {current_user_id} - IP: {client_ip}")
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 200
    
    if not user.is_active:
        current_app.logger.warning(f"Dify V2会话列表请求失败 - 用户已被禁用 - 用户ID: {current_user_id} - IP: {client_ip}")
        return jsonify({
            'success': False,
            'message': '账户已被禁用'
        }), 403
    
    current_app.logger.info(f"[Dify V2会话列表请求] 场景: {scenario} - 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        # 获取查询参数
        query_params = request.args.to_dict()
        
        # 验证参数
        is_valid, errors, cleaned_params = DifyAppService.validate_scenario_params(scenario, 'conversations', query_params)
        
        if not is_valid:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.warning(
                f"[Dify V2会话列表参数错误] 场景: {scenario} - 用户: {user.username or user.email} - "
                f"错误: {errors} - 耗时: {elapsed_time}ms"
            )
            return jsonify({
                'success': False,
                'message': f'参数验证失败: {"; ".join(errors)}',
                'errors': errors
            }), 400
        
        # 准备用户信息
        user_info = {
            'id': user.id,
            'username': user.username or user.email,
            'email': user.email
        }
        
        # 转发请求到Dify API
        success, data, status_code = DifyAppService.forward_request(
            scenario=scenario,
            api_type='conversations',
            request_method='GET',
            query_params=cleaned_params,
            user_info=user_info
        )
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        
        if success:
            current_app.logger.info(
                f"[Dify V2会话列表成功] 场景: {scenario} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms"
            )
            # 直接返回Dify的原始响应，不包装额外的success字段
            return jsonify(data), status_code
        else:
            current_app.logger.error(
                f"[Dify V2会话列表失败] 场景: {scenario} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms"
            )
            # 对于API错误，也直接返回Dify的原始错误响应
            return jsonify(data), status_code
            
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(
            f"[Dify V2会话列表系统错误] 场景: {scenario} - 用户: {user.username or user.email} - "
            f"错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True
        )
        return jsonify({
            'success': False,
            'message': f'系统错误: {str(e)}'
        }), 500

@dify_v2_bp.route('/<scenario>/messages', methods=['GET'])
@jwt_required()
def get_messages_v2(scenario):
    """
    获取会话历史消息接口 V2 - 支持应用场景参数
    
    URL示例:
    - GET /api/dify/v2/multilingual_qa/messages  (多语言问答)
    - GET /api/dify/v2/standard_query/messages   (标准查询)
    """
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 验证应用场景
    if scenario not in [s['key'] for s in DifyAppService.get_all_scenarios()]:
        return jsonify({
            'success': False,
            'message': f'不支持的应用场景: {scenario}'
        }), 400
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user:
        current_app.logger.warning(f"Dify V2消息历史请求失败 - 用户不存在 - 用户ID: {current_user_id} - IP: {client_ip}")
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 200
    
    if not user.is_active:
        current_app.logger.warning(f"Dify V2消息历史请求失败 - 用户已被禁用 - 用户ID: {current_user_id} - IP: {client_ip}")
        return jsonify({
            'success': False,
            'message': '账户已被禁用'
        }), 403
    
    current_app.logger.info(f"[Dify V2消息历史请求] 场景: {scenario} - 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        # 获取查询参数
        query_params = request.args.to_dict()
        
        # 验证参数
        is_valid, errors, cleaned_params = DifyAppService.validate_scenario_params(scenario, 'messages', query_params)
        
        if not is_valid:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.warning(
                f"[Dify V2消息历史参数错误] 场景: {scenario} - 用户: {user.username or user.email} - "
                f"错误: {errors} - 耗时: {elapsed_time}ms"
            )
            return jsonify({
                'success': False,
                'message': f'参数验证失败: {"; ".join(errors)}',
                'errors': errors
            }), 400
        
        # 准备用户信息
        user_info = {
            'id': user.id,
            'username': user.username or user.email,
            'email': user.email
        }
        
        # 转发请求到Dify API
        success, data, status_code = DifyAppService.forward_request(
            scenario=scenario,
            api_type='messages',
            request_method='GET',
            query_params=cleaned_params,
            user_info=user_info
        )
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        
        if success:
            current_app.logger.info(
                f"[Dify V2消息历史成功] 场景: {scenario} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms"
            )
            # 直接返回Dify的原始响应，不包装额外的success字段
            return jsonify(data), status_code
        else:
            current_app.logger.error(
                f"[Dify V2消息历史失败] 场景: {scenario} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms"
            )
            # 对于API错误，也直接返回Dify的原始错误响应
            return jsonify(data), status_code
            
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(
            f"[Dify V2消息历史系统错误] 场景: {scenario} - 用户: {user.username or user.email} - "
            f"错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True
        )
        return jsonify({
            'success': False,
            'message': f'系统错误: {str(e)}'
        }), 500

@dify_v2_bp.route('/scenarios', methods=['GET'])
@jwt_required()
def get_scenarios():
    """
    获取所有支持的应用场景列表
    
    返回所有可用的应用场景，供前端选择使用
    """
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 200
    
    current_app.logger.info(f"[获取应用场景列表] 用户: {user.username or user.email}")
    
    try:
        scenarios = DifyAppService.get_all_scenarios()
        
        # 为每个场景添加配置状态
        for scenario in scenarios:
            status = DifyAppService.get_scenario_status(scenario['key'])
            scenario['status'] = status
        
        return jsonify({
            'success': True,
            'message': '获取应用场景列表成功',
            'data': {
                'scenarios': scenarios,
                'total': len(scenarios)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"[获取应用场景列表错误] 用户: {user.username or user.email} - 错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'系统错误: {str(e)}'
        }), 500

@dify_v2_bp.route('/<scenario>/config', methods=['GET'])
@jwt_required()
def get_scenario_config(scenario):
    """
    获取指定应用场景的配置信息
    
    URL示例:
    - GET /api/dify/v2/multilingual_qa/config  (多语言问答)
    - GET /api/dify/v2/standard_query/config   (标准查询)
    """
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 200
    
    # 验证应用场景
    if scenario not in [s['key'] for s in DifyAppService.get_all_scenarios()]:
        return jsonify({
            'success': False,
            'message': f'不支持的应用场景: {scenario}'
        }), 400
    
    current_app.logger.info(f"[获取场景配置] 场景: {scenario} - 用户: {user.username or user.email}")
    
    try:
        status = DifyAppService.get_scenario_status(scenario)
        
        return jsonify({
            'success': True,
            'message': '获取配置成功',
            'data': {
                'scenario_info': status,
                'endpoints': {
                    'chat_simple': f'/api/dify/v2/{scenario}/chat-simple',
                    'conversations': f'/api/dify/v2/{scenario}/conversations',
                    'messages': f'/api/dify/v2/{scenario}/messages',
                    'config': f'/api/dify/v2/{scenario}/config',
                    'rename_conversation': f'/api/dify/v2/{scenario}/conversations/{{conversation_id}}/name',
                    'delete_conversation': f'/api/dify/v2/{scenario}/conversations/{{conversation_id}}'
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"[获取场景配置错误] 场景: {scenario} - 用户: {user.username or user.email} - 错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'系统错误: {str(e)}'
        }), 500

@dify_v2_bp.route('/<scenario>/conversations/<conversation_id>/name', methods=['POST'])
@jwt_required()
def rename_conversation_v2(scenario, conversation_id):
    """
    会话重命名接口 V2 - 支持应用场景参数
    
    URL示例:
    - POST /api/dify/v2/multilingual_qa/conversations/{conversation_id}/name  (多语言问答)
    - POST /api/dify/v2/standard_query/conversations/{conversation_id}/name   (标准查询)
    """
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 验证应用场景
    if scenario not in [s['key'] for s in DifyAppService.get_all_scenarios()]:
        return jsonify({
            'success': False,
            'message': f'不支持的应用场景: {scenario}'
        }), 400
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user:
        current_app.logger.warning(f"Dify V2会话重命名请求失败 - 用户不存在 - 用户ID: {current_user_id} - IP: {client_ip}")
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 200
    
    if not user.is_active:
        current_app.logger.warning(f"Dify V2会话重命名请求失败 - 用户已被禁用 - 用户ID: {current_user_id} - IP: {client_ip}")
        return jsonify({
            'success': False,
            'message': '账户已被禁用'
        }), 403
    
    current_app.logger.info(f"[Dify V2会话重命名请求] 场景: {scenario} - 会话ID: {conversation_id} - 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供有效的JSON数据'
            }), 400
        
        # 准备用户信息
        user_info = {
            'id': user.id,
            'username': user.username or user.email,
            'email': user.email
        }
        
        # 构建完整的API URL（包含conversation_id/name）
        base_config = DifyAppService.get_app_config(scenario, 'conversation_ops')
        api_url = f"{base_config['api_url']}/{conversation_id}/name"
        
        # 直接发送POST请求到Dify API
        import requests
        headers = base_config['headers']
        response = requests.post(api_url, json=data, headers=headers, timeout=60)
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        
        if response.ok:
            try:
                response_data = response.json()
                current_app.logger.info(
                    f"[Dify V2会话重命名成功] 场景: {scenario} - 会话ID: {conversation_id} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms"
                )
                current_app.logger.info(f"[Dify V2会话重命名响应] 原始数据: {response_data}")
                # 直接返回Dify的原始响应，不包装额外的success字段
                return jsonify(response_data), response.status_code
            except Exception as json_error:
                current_app.logger.warning(
                    f"[Dify V2会话重命名响应解析失败] JSON解析错误: {str(json_error)} - "
                    f"响应文本: {response.text[:200]} - Content-Type: {response.headers.get('content-type', 'unknown')}"
                )
                # 重命名操作如果无法解析JSON，仍然返回错误
                return jsonify({'error': f'响应解析失败: {str(json_error)}', 'detail': response.text[:200]}), 500
        else:
            current_app.logger.error(
                f"[Dify V2会话重命名失败] 场景: {scenario} - 会话ID: {conversation_id} - 用户: {user.username or user.email} - 状态码: {response.status_code} - 耗时: {elapsed_time}ms"
            )
            # 对于API错误，也直接返回Dify的原始错误响应
            try:
                error_detail = response.json()
                return jsonify(error_detail), response.status_code
            except:
                return jsonify({'error': f'API返回错误: {response.status_code}', 'detail': response.text[:200]}), response.status_code
            
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(
            f"[Dify V2会话重命名系统错误] 场景: {scenario} - 会话ID: {conversation_id} - 用户: {user.username or user.email} - "
            f"错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True
        )
        return jsonify({
            'success': False,
            'message': f'系统错误: {str(e)}'
        }), 500

@dify_v2_bp.route('/<scenario>/conversations/<conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation_v2(scenario, conversation_id):
    """
    删除会话接口 V2 - 支持应用场景参数
    
    URL示例:
    - DELETE /api/dify/v2/multilingual_qa/conversations/{conversation_id}  (多语言问答)
    - DELETE /api/dify/v2/standard_query/conversations/{conversation_id}   (标准查询)
    """
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 验证应用场景
    if scenario not in [s['key'] for s in DifyAppService.get_all_scenarios()]:
        return jsonify({
            'success': False,
            'message': f'不支持的应用场景: {scenario}'
        }), 400
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user:
        current_app.logger.warning(f"Dify V2删除会话请求失败 - 用户不存在 - 用户ID: {current_user_id} - IP: {client_ip}")
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 200
    
    if not user.is_active:
        current_app.logger.warning(f"Dify V2删除会话请求失败 - 用户已被禁用 - 用户ID: {current_user_id} - IP: {client_ip}")
        return jsonify({
            'success': False,
            'message': '账户已被禁用'
        }), 403
    
    current_app.logger.info(f"[Dify V2删除会话请求] 场景: {scenario} - 会话ID: {conversation_id} - 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        # 获取JSON数据（根据Dify API要求）
        data = request.get_json()
        
        # 准备用户信息
        user_info = {
            'id': user.id,
            'username': user.username or user.email,
            'email': user.email
        }
        
        # 构建完整的API URL（包含conversation_id）
        base_config = DifyAppService.get_app_config(scenario, 'conversation_ops')
        api_url = f"{base_config['api_url']}/{conversation_id}"
        
        # 直接发送DELETE请求到Dify API
        import requests
        headers = base_config['headers']
        kwargs = {'headers': headers, 'timeout': 60}
        if data:
            kwargs['json'] = data
        
        response = requests.delete(api_url, **kwargs)
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        
        if response.ok:
            current_app.logger.info(
                f"[Dify V2删除会话成功] 场景: {scenario} - 会话ID: {conversation_id} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms"
            )
            
            # 解析Dify响应并转换为统一格式
            try:
                response_data = response.json()
                current_app.logger.info(f"[Dify V2删除会话响应] 原始数据: {response_data}")
                
                # 检查Dify返回的成功响应格式
                if response_data.get('result') == 'success':
                    # 转换为系统统一的成功响应格式
                    unified_response = {
                        "success": "true",
                        "message": "删除成功"
                    }
                    current_app.logger.info(f"[Dify V2删除会话] 转换为统一响应格式: {unified_response}")
                    return jsonify(unified_response), 200
                else:
                    # 如果Dify返回其他格式，直接转发
                    return jsonify(response_data), response.status_code
                    
            except Exception as json_error:
                # 如果无法解析JSON，检查响应内容
                response_text = response.text
                current_app.logger.warning(
                    f"[Dify V2删除会话响应解析失败] JSON解析错误: {str(json_error)} - "
                    f"响应文本: {response_text[:200]} - Content-Type: {response.headers.get('content-type', 'unknown')}"
                )
                
                # 如果响应为空或只有空白字符，返回统一成功响应
                if not response_text or not response_text.strip():
                    current_app.logger.info("[Dify V2删除会话] 响应为空，返回统一成功响应")
                    return jsonify({"success": "true", "message": "删除成功"}), 200
                else:
                    # 如果有响应内容但无法解析为JSON，仍返回成功（因为status_code是ok的）
                    current_app.logger.info("[Dify V2删除会话] 响应无法解析但状态正常，返回统一成功响应")
                    return jsonify({"success": "true", "message": "删除成功"}), 200
        else:
            current_app.logger.error(
                f"[Dify V2删除会话失败] 场景: {scenario} - 会话ID: {conversation_id} - 用户: {user.username or user.email} - 状态码: {response.status_code} - 耗时: {elapsed_time}ms"
            )
            # 对于API错误，也直接返回Dify的原始错误响应
            try:
                error_detail = response.json()
                return jsonify(error_detail), response.status_code
            except:
                return jsonify({'error': f'API返回错误: {response.status_code}', 'detail': response.text[:200]}), response.status_code
            
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(
            f"[Dify V2删除会话系统错误] 场景: {scenario} - 会话ID: {conversation_id} - 用户: {user.username or user.email} - "
            f"错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True
        )
        return jsonify({
            'success': False,
            'message': f'系统错误: {str(e)}'
        }), 500 