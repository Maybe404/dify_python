from flask import Blueprint, request, jsonify, current_app, Response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.task import Task, TaskFile, TaskResult
from app.services.task_service import TaskService
from app.services.standard_config_service import StandardConfigService
from app.services.document_service import DocumentService
import json
import time
import os

# 创建任务管理蓝图
tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """文件上传接口 - 上传文件到指定任务类型"""
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    current_app.logger.info(f"[文件上传请求] 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        # 获取任务类型 - 从表单数据中获取
        task_type = request.form.get('task_type')
        if not task_type:
            return jsonify({
                'success': False,
                'message': '请提供任务类型'
            }), 400
        
        # 验证任务类型
        if not StandardConfigService.validate_standard_type(task_type):
            valid_types = [t['key'] for t in StandardConfigService.get_all_standard_types()]
            return jsonify({
                'success': False,
                'message': f'无效的任务类型。支持的类型: {", ".join(valid_types)}'
            }), 400
        
        # 获取上传的文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '未找到上传的文件'
            }), 400
        
        file = request.files['file']
        
        # 1. 创建任务
        task = TaskService.create_task(user.id, task_type)
        
        # 2. 上传文件到任务
        task_file = TaskService.upload_file_to_task(task.id, file, user.id)
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '文件上传成功',
            'data': {
                'task': task.to_dict(),
                'file': task_file.to_dict()
            }
        }
        
        current_app.logger.info(f"[文件上传成功] 任务ID: {task.id} - 文件: {task_file.original_filename} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
        
        return jsonify(response_data), 201
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"文件上传失败 - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'文件上传失败: {str(e)}'
        }), 500

@tasks_bp.route('/upload-multiple', methods=['POST'])
@jwt_required()
def upload_multiple_files():
    """多文件上传接口 - 专门为标准对比等需要多个文件的任务类型"""
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    current_app.logger.info(f"[多文件上传请求] 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        # 获取任务类型
        task_type = request.form.get('task_type')
        if not task_type:
            return jsonify({
                'success': False,
                'message': '请提供任务类型'
            }), 400
        
        # 验证任务类型
        if not StandardConfigService.validate_standard_type(task_type):
            valid_types = [t['key'] for t in StandardConfigService.get_all_standard_types()]
            return jsonify({
                'success': False,
                'message': f'无效的任务类型。支持的类型: {", ".join(valid_types)}'
            }), 400
        
        # 获取上传的文件列表
        uploaded_files = []
        file_keys = ['file1', 'file2']  # 支持最多两个文件
        
        for file_key in file_keys:
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:  # 确保文件存在且有文件名
                    uploaded_files.append(file)
        
        if len(uploaded_files) == 0:
            return jsonify({
                'success': False,
                'message': '至少需要上传一个文件'
            }), 400
        
        # 对于标准对比，检查是否上传了两个文件
        if task_type == 'standard_comparison' and len(uploaded_files) != 2:
            return jsonify({
                'success': False,
                'message': '标准对比任务需要上传两个文件'
            }), 400
        
        # 1. 创建单个任务
        task = TaskService.create_task(user.id, task_type)
        current_app.logger.info(f"创建任务成功 - 任务ID: {task.id} - 类型: {task_type}")
        
        # 2. 依次上传所有文件到同一个任务
        task_files = []
        failed_files = []
        
        for i, file in enumerate(uploaded_files):
            try:
                current_app.logger.info(f"开始上传文件 {i+1}/{len(uploaded_files)} - 文件名: {file.filename}")
                task_file = TaskService.upload_file_to_task(task.id, file, user.id)
                task_files.append(task_file)
                current_app.logger.info(f"文件上传成功 - 文件ID: {task_file.id} - Dify文件ID: {task_file.dify_file_id}")
            except Exception as file_error:
                current_app.logger.error(f"文件上传失败 - 文件: {file.filename} - 错误: {str(file_error)}")
                failed_files.append({
                    'filename': file.filename,
                    'error': str(file_error)
                })
        
        # 检查上传结果
        if len(failed_files) > 0:
            # 如果有文件上传失败，标记任务为失败
            task.update_status('failed')
            return jsonify({
                'success': False,
                'message': '部分文件上传失败',
                'data': {
                    'task': task.to_dict(),
                    'successful_files': [f.to_dict() for f in task_files],
                    'failed_files': failed_files
                }
            }), 400
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '多文件上传成功',
            'data': {
                'task': task.to_dict(),
                'files': [f.to_dict() for f in task_files],
                'total_files': len(task_files)
            }
        }
        
        current_app.logger.info(f"[多文件上传成功] 任务ID: {task.id} - 文件数: {len(task_files)} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
        
        return jsonify(response_data), 201
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"多文件上传失败 - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'多文件上传失败: {str(e)}'
        }), 500

@tasks_bp.route('/standard-processing', methods=['POST'])
@jwt_required()
def standard_processing():
    """标准处理接口 - 异步执行，立即返回状态"""
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    current_app.logger.info(f"[标准处理请求] 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供有效的JSON数据'
            }), 400
        
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({
                'success': False,
                'message': '请提供任务ID'
            }), 400
        
        # 检查任务是否存在且有权限访问
        task = Task.find_by_id(task_id)
        if not task:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 200
        
        if task.user_id != user.id:
            return jsonify({
                'success': False,
                'message': '无权限访问此任务'
            }), 403
        
        # 移除 task_id 参数，其他参数直接转发给 Dify
        dify_request_data = {k: v for k, v in data.items() if k != 'task_id'}
        
        # 启动异步任务执行
        try:
            success = TaskService.send_dify_request_direct_async(task_id, user.id, dify_request_data)
        except Exception as e:
            # 如果启动异步任务失败，记录错误并返回失败响应
            current_app.logger.error(f"启动异步任务异常 - 任务: {task_id} - 用户: {user.username or user.email} - 错误: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'message': '请求发送失败，无法启动后台任务'
            }), 500
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        
        if success:
            # 立即返回成功响应，任务在后台继续执行
            response_data = {
                'success': True,
                'message': '请求发送成功，任务正在后台处理中，请在任务中心查看进度',
                'task_id': task_id,
                'status': 'processing'
            }
            
            current_app.logger.info(f"[标准处理任务启动成功] 任务: {task_id} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
            
            return jsonify(response_data), 200
        else:
            # 后台任务启动失败
            current_app.logger.warning(f"[标准处理任务启动失败] 任务: {task_id} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
            return jsonify({
                'success': False,
                'message': '请求发送失败，无法启动后台任务'
            }), 500
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"标准处理请求失败 - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': '请求发送失败'
        }), 500

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """获取任务列表 - 任务中心列表页"""
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    current_app.logger.info(f"[获取任务列表] 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        # 获取查询参数
        status = request.args.get('status')
        task_type = request.args.get('task_type')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # 最大100条
        
        # 支持多状态查询，状态参数可以是逗号分隔的字符串
        # 例如: ?status=processing,completed,failed
        current_app.logger.info(f"查询参数 - status: {status}, task_type: {task_type}, page: {page}, per_page: {per_page}")
        
        # 查询任务
        pagination = Task.find_by_user_id(user.id, status, task_type, page, per_page)
        
        tasks_data = []
        for task in pagination.items:
            task_dict = task.to_dict()
            # 添加文件信息
            files = TaskFile.find_by_task_id(task.id)
            task_dict['files'] = [f.to_dict() for f in files]
            task_dict['file_count'] = len(files)
            tasks_data.append(task_dict)
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '获取任务列表成功',
            'data': {
                'tasks': tasks_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        }
        
        current_app.logger.info(f"[获取任务列表成功] 用户: {user.username or user.email} - 任务数: {len(tasks_data)} - 耗时: {elapsed_time}ms")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"获取任务列表失败 - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取任务列表失败: {str(e)}'
        }), 500

@tasks_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task_detail(task_id):
    """获取任务详情 - 任务详情页"""
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    current_app.logger.info(f"[获取任务详情] 任务: {task_id} - 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        # 获取任务
        task = Task.find_by_id(task_id)
        if not task:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 200
        
        if task.user_id != user.id:
            return jsonify({
                'success': False,
                'message': '无权限访问此任务'
            }), 403
        
        # 获取任务文件
        files = TaskService.get_task_files(task_id, user.id)
        
        # 获取任务结果
        results = TaskService.get_task_results(task_id, user.id)
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '获取任务详情成功',
            'data': {
                'task': task.to_dict(),
                'files': [f.to_dict() for f in files],
                'results': [r.to_dict() for r in results]
            }
        }
        
        current_app.logger.info(f"[获取任务详情成功] 任务: {task_id} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"获取任务详情失败 - 任务: {task_id} - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取任务详情失败: {str(e)}'
        }), 500

@tasks_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """删除任务"""
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    current_app.logger.info(f"[删除任务] 任务: {task_id} - 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        # 删除任务
        TaskService.delete_task(task_id, user.id)
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '任务删除成功'
        }
        
        current_app.logger.info(f"[删除任务成功] 任务: {task_id} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"删除任务失败 - 任务: {task_id} - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'删除任务失败: {str(e)}'
        }), 500

@tasks_bp.route('/types', methods=['GET'])
@jwt_required()
def get_task_types():
    """获取支持的任务类型"""
    start_time = time.time()
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    try:
        task_types = StandardConfigService.get_all_standard_types()
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '获取任务类型成功',
            'data': {
                'task_types': task_types
            }
        }
        
        current_app.logger.info(f"[获取任务类型成功] 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"获取任务类型失败 - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取任务类型失败: {str(e)}'
        }), 500

@tasks_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_task_dashboard():
    """获取任务仪表板数据"""
    start_time = time.time()
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    try:
        from sqlalchemy import func
        from app import db
        
        # 统计各状态的任务数量
        status_stats = dict(
            db.session.query(Task.status, func.count(Task.id))
            .filter_by(user_id=user.id)
            .group_by(Task.status)
            .all()
        )
        
        # 统计各类型的任务数量
        type_stats = dict(
            db.session.query(Task.task_type, func.count(Task.id))
            .filter_by(user_id=user.id)
            .group_by(Task.task_type)
            .all()
        )
        
        # 总任务数
        total_tasks = sum(status_stats.values())
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '获取仪表板数据成功',
            'data': {
                'total_tasks': total_tasks,
                'status_stats': status_stats,
                'type_stats': type_stats
            }
        }
        
        current_app.logger.info(f"[获取仪表板数据成功] 用户: {user.username or user.email} - 总任务: {total_tasks} - 耗时: {elapsed_time}ms")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"获取仪表板数据失败 - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取仪表板数据失败: {str(e)}'
        }), 500

@tasks_bp.route('/<task_id>/files/<file_id>/preview', methods=['GET'])
@jwt_required()
def preview_file(task_id, file_id):
    """预览任务文件"""
    start_time = time.time()
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    try:
        # 获取文件
        task_file = TaskFile.find_by_id(file_id)
        if not task_file:
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 200
        
        if task_file.task_id != task_id or task_file.user_id != user.id:
            return jsonify({
                'success': False,
                'message': '无权限访问此文件'
            }), 403
        
        # 获取预览内容
        preview_data = DocumentService.get_file_preview(task_file.file_path)
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        response_data = {
            'success': True,
            'message': '文件预览成功',
            'data': {
                'file_info': task_file.to_dict(),
                'preview': preview_data
            }
        }
        
        current_app.logger.info(f"[文件预览成功] 文件: {file_id} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"文件预览失败 - 文件: {file_id} - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'文件预览失败: {str(e)}'
        }), 500

@tasks_bp.route('/<task_id>/results/<result_id>/export', methods=['GET'])
@jwt_required()
def export_result(task_id, result_id):
    """生成并导出任务结果为PDF文件"""
    start_time = time.time()
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    try:
        # 获取任务结果
        task_result = TaskResult.query.get(result_id)
        if not task_result:
            return jsonify({
                'success': False,
                'message': '任务结果不存在'
            }), 200
        
        if task_result.task_id != task_id or task_result.user_id != user.id:
            return jsonify({
                'success': False,
                'message': '无权限访问此结果'
            }), 403
        
        # 创建导出目录（使用配置化路径）
        from app.config.config import Config
        export_base_dir = Config.get_export_directory()
        export_dir = os.path.join(export_base_dir, user.id)
        
        current_app.logger.info(f"[PDF导出] 导出基础目录: {export_base_dir}")
        current_app.logger.info(f"[PDF导出] 用户导出目录: {export_dir}")
        
        os.makedirs(export_dir, exist_ok=True)
        
        # 生成PDF文件路径
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        output_filename = f"task_result_{task_id}_{timestamp}.pdf"
        output_path = os.path.join(export_dir, output_filename)
        
        current_app.logger.info(f"[PDF导出] 目标文件路径: {output_path}")
        current_app.logger.info(f"[PDF导出] 目录是否存在: {os.path.exists(export_dir)}")
        
        # 导出PDF
        success, pdf_path, error = DocumentService.export_task_result_to_pdf(task_result, output_path)
        
        if success:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.info(f"[PDF导出成功] 结果: {result_id} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
            
            # 直接返回文件，不再返回JSON响应
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/pdf'
            )
        else:
            return jsonify({
                'success': False,
                'message': f'PDF导出失败: {error}'
            }), 500
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"PDF导出失败 - 结果: {result_id} - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'PDF导出失败: {str(e)}'
        }), 500

@tasks_bp.route('/<task_id>/results/<result_id>/export-markdown', methods=['GET'])
@jwt_required()
def export_result_markdown(task_id, result_id):
    """生成并导出任务结果为Markdown格式文件"""
    start_time = time.time()
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    try:
        # 获取任务结果
        task_result = TaskResult.query.get(result_id)
        if not task_result:
            return jsonify({
                'success': False,
                'message': '任务结果不存在'
            }), 200
        
        if task_result.task_id != task_id or task_result.user_id != user.id:
            return jsonify({
                'success': False,
                'message': '无权限访问此结果'
            }), 403
        
        # 获取导出格式参数
        format_type = request.args.get('format', 'preview')  # preview | raw
        if format_type not in ['preview', 'raw']:
            format_type = 'preview'
        
        # 创建导出目录（使用配置化路径）
        from app.config.config import Config
        export_base_dir = Config.get_export_directory()
        export_dir = os.path.join(export_base_dir, user.id)
        os.makedirs(export_dir, exist_ok=True)
        
        # 生成文件路径
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        file_ext = '.md' if format_type == 'raw' else '.html'
        output_filename = f"task_result_{task_id}_{format_type}_{timestamp}{file_ext}"
        output_path = os.path.join(export_dir, output_filename)
        
        current_app.logger.info(f"[Markdown导出] 结果: {result_id} - 格式: {format_type} - 用户: {user.username or user.email}")
        
        # 导出Markdown
        success, file_path, error = DocumentService.export_task_result_to_markdown(
            task_result, output_path, format_type
        )
        
        if success:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.info(f"[Markdown导出成功] 结果: {result_id} - 格式: {format_type} - 用户: {user.username or user.email} - 耗时: {elapsed_time}ms")
            
            # 根据格式设置相应的MIME类型
            if format_type == 'raw':
                mimetype = 'text/markdown'
            else:
                mimetype = 'text/html'
            
            # 直接返回文件
            return send_file(
                file_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype=mimetype
            )
        else:
            return jsonify({
                'success': False,
                'message': f'Markdown导出失败: {error}'
            }), 500
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"Markdown导出失败 - 结果: {result_id} - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Markdown导出失败: {str(e)}'
        }), 500

@tasks_bp.route('/<task_id>/files/<file_id>/download', methods=['GET'])
def download_file(task_id, file_id):
    """下载任务文件 - 无需JWT认证的公共下载接口"""
    start_time = time.time()
    
    try:
        # 获取文件 - 不验证用户身份，允许公共访问
        task_file = TaskFile.find_by_id(file_id)
        if not task_file:
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 200
        
        # 只验证任务ID和文件ID的匹配，不验证用户权限
        if task_file.task_id != task_id:
            return jsonify({
                'success': False,
                'message': '文件不属于该任务'
            }), 403
        
        # 检查文件是否存在
        if not os.path.exists(task_file.file_path):
            return jsonify({
                'success': False,
                'message': '文件不存在或已被删除'
            }), 404
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.info(f"[文件下载] 文件: {file_id} - 任务: {task_id} - 公共访问 - 耗时: {elapsed_time}ms")
        
        # 直接返回文件
        return send_file(
            task_file.file_path,
            as_attachment=True,
            download_name=task_file.original_filename,
            mimetype=task_file.file_type
        )
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"文件下载失败 - 文件: {file_id} - 任务: {task_id} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'文件下载失败: {str(e)}'
        }), 500

@tasks_bp.route('/<task_id>/results/paginated', methods=['GET'])
@jwt_required()
def get_task_results_paginated(task_id):
    """获取任务结果的分页数据 - 专门用于需要分页展示的任务类型"""
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'sn')
    sort_order = request.args.get('sort_order', 'asc')
    
    # 验证分页参数
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:  # 限制每页最大100条
        per_page = 20
    
    current_app.logger.info(f"[获取分页结果] 任务: {task_id} - 用户: {user.username or user.email} (ID: {user.id}) - 页码: {page}/{per_page} - IP: {client_ip}")
    
    try:
        # 获取分页结果
        result = TaskService.get_task_results_paginated(
            task_id, user.id, page, per_page, sort_by, sort_order
        )
        
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        
        current_app.logger.info(f"[获取分页结果成功] 任务: {task_id} - 用户: {user.username or user.email} - 页码: {page} - 总数: {result['pagination']['total_items']} - 耗时: {elapsed_time}ms")
        
        return jsonify({
            'success': True,
            'message': '获取分页结果成功',
            'data': result
        }), 200
        
    except ValueError as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.warning(f"获取分页结果失败 - 任务: {task_id} - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"获取分页结果失败 - 任务: {task_id} - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取分页结果失败: {str(e)}'
        }), 500

@tasks_bp.route('/<task_id>/results/export-excel', methods=['GET'])
@jwt_required()
def export_task_results_to_excel(task_id):
    """导出任务分页结果为Excel文件"""
    start_time = time.time()
    client_ip = request.remote_addr
    
    # 获取当前用户信息
    current_user_id = get_jwt_identity()
    user = User.find_by_id(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'message': '用户验证失败'
        }), 403
    
    current_app.logger.info(f"[Excel导出请求] 任务: {task_id} - 用户: {user.username or user.email} (ID: {user.id}) - IP: {client_ip}")
    
    try:
        # 获取完整的任务结果数据（不分页，导出全部数据）
        result = TaskService.get_task_results_paginated(
            task_id, user.id, page=1, per_page=10000, sort_by='sn', sort_order='asc'
        )
        
        items_data = result.get('items', [])
        task_info = result.get('task_info', {})
        
        if not items_data:
            return jsonify({
                'success': False,
                'message': '没有可导出的数据'
            }), 400
        
        # 创建导出目录（使用配置化路径）
        from app.config.config import Config
        export_base_dir = Config.get_export_directory()
        export_dir = os.path.join(export_base_dir, user.id)
        os.makedirs(export_dir, exist_ok=True)
        
        # 生成Excel文件路径
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        output_filename = f"task_results_{task_id}_{timestamp}.xlsx"
        output_path = os.path.join(export_dir, output_filename)
        
        current_app.logger.info(f"[Excel导出] 目标文件路径: {output_path}")
        current_app.logger.info(f"[Excel导出] 准备导出 {len(items_data)} 条记录")
        
        # 导出Excel
        success, excel_path, error = DocumentService.export_task_results_to_excel(
            items_data, task_info, output_path
        )
        
        if success:
            elapsed_time = round((time.time() - start_time) * 1000, 2)
            current_app.logger.info(f"[Excel导出成功] 任务: {task_id} - 用户: {user.username or user.email} - 记录数: {len(items_data)} - 耗时: {elapsed_time}ms")
            
            # 直接返回文件
            return send_file(
                excel_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return jsonify({
                'success': False,
                'message': f'Excel导出失败: {error}'
            }), 500
        
    except ValueError as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.warning(f"Excel导出失败 - 任务: {task_id} - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
        
    except Exception as e:
        elapsed_time = round((time.time() - start_time) * 1000, 2)
        current_app.logger.error(f"Excel导出失败 - 任务: {task_id} - 用户: {user.username or user.email} - 错误: {str(e)} - 耗时: {elapsed_time}ms", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Excel导出失败: {str(e)}'
        }), 500

