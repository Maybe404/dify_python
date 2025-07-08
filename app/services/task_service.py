import json
import requests
from datetime import datetime
from flask import current_app
from app.models.task import Task, TaskFile, TaskResult
from app.services.file_service import FileService
from app.services.standard_config_service import StandardConfigService
import time
import threading

class TaskService:
    """任务服务 - 管理任务创建、状态更新和处理逻辑"""
    
    @staticmethod
    def _extract_json_from_text(text):
        """从文本中提取JSON内容，处理可能的markdown格式"""
        if not text or not isinstance(text, str):
            return text
        
        # 移除可能的markdown代码块标记
        text = text.strip()
        
        # 处理 ```json ... ``` 格式
        if text.startswith('```json'):
            # 查找结束标记
            end_marker = text.rfind('```')
            if end_marker > 6:  # 确保不是开始的```json
                text = text[7:end_marker].strip()  # 移除```json和结束的```
        elif text.startswith('```'):
            # 处理一般的代码块
            lines = text.split('\n')
            if len(lines) > 2 and lines[-1].strip() == '```':
                text = '\n'.join(lines[1:-1])
        
        # 验证是否为有效JSON
        try:
            import json
            json.loads(text)
            return text
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，返回原文本
            return text
    
    @staticmethod
    def create_task(user_id, task_type, title=None, description=None):
        """创建新任务"""
        try:
            # 验证任务类型
            if not StandardConfigService.validate_standard_type(task_type):
                raise ValueError(f"无效的任务类型: {task_type}")
            
            # 如果没有提供标题，使用默认标题
            if not title:
                type_name = StandardConfigService.STANDARD_TYPE_CONFIG[task_type]['name']
                title = f"{type_name}任务 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # 创建任务
            task = Task(
                user_id=user_id,
                task_type=task_type,
                title=title,
                description=description or f"自动创建的{type_name}任务",
                status='pending'
            )
            
            task.save()
            
            current_app.logger.info(f"任务创建成功 - 用户: {user_id} - 任务ID: {task.id} - 类型: {task_type}")
            
            return task
            
        except Exception as e:
            current_app.logger.error(f"创建任务失败 - 用户: {user_id} - 错误: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def update_task_status(task_id, status, error_message=None):
        """更新任务状态"""
        try:
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            task.update_status(status)
            
            current_app.logger.info(f"任务状态更新 - 任务ID: {task_id} - 状态: {status}")
            
            return task
            
        except Exception as e:
            current_app.logger.error(f"更新任务状态失败 - 任务ID: {task_id} - 错误: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def upload_file_to_task(task_id, file, user_id):
        """上传文件到任务"""
        try:
            # 检查任务是否存在
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if task.user_id != user_id:
                raise ValueError("无权限访问此任务")
            
            # 更新任务状态为上传中
            task.update_status('uploading')
            
            # 1. 保存文件到本地
            success, file_info, error = FileService.save_file(file, user_id)
            if not success:
                task.update_status('failed')
                raise ValueError(f"文件保存失败: {error}")
            
            # 2. 创建文件记录
            task_file = TaskFile(
                task_id=task.id,
                user_id=user_id,
                original_filename=file_info['original_filename'],
                stored_filename=file_info['stored_filename'],
                file_path=file_info['file_path'],
                file_size=file_info['file_size'],
                file_type=file_info['file_type'],
                file_extension=file_info['file_extension'],
                upload_status='uploading'
            )
            
            task_file.save()
            
            # 3. 获取对应任务类型的Dify配置
            dify_config = StandardConfigService.get_config_for_standard_type(task.task_type)
            
            # 4. 上传到Dify
            dify_success, dify_result, dify_error = FileService.upload_to_dify(
                file_info['file_path'],
                file_info['original_filename'],
                dify_config['api_key'],
                user_id,
                dify_config['file_upload_url']
            )
            
            if dify_success:
                # 保存Dify返回信息
                task_file.set_dify_info(dify_result.get('id'), dify_result)
                task_file.update_status('uploaded')
                # 文件上传成功后，任务状态更新为uploaded，等待调用标准处理接口
                task.update_status('uploaded')
                
                current_app.logger.info(f"文件上传成功 - 任务: {task_id} - 文件: {file_info['original_filename']} - 状态更新为uploaded")
                
            else:
                task_file.update_status('failed', dify_error)
                task.update_status('failed')
                raise ValueError(f"Dify文件上传失败: {dify_error}")
            
            return task_file
            
        except Exception as e:
            current_app.logger.error(f"任务文件上传失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def process_dify_response(task_id, user_id, dify_response_data, conversation_id=None):
        """处理Dify返回的响应数据并存储"""
        try:
            # 检查任务是否存在
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if task.user_id != user_id:
                raise ValueError("无权限访问此任务")
            
            # 解析Dify响应数据
            if isinstance(dify_response_data, str):
                try:
                    dify_data = json.loads(dify_response_data)
                except:
                    dify_data = {'raw_response': dify_response_data}
            else:
                dify_data = dify_response_data
            
            # 提取answer字段，优先级：answer > outputs中的审查意见/输出内容
            answer_content = dify_data.get('answer')
            
            # 如果answer为空，尝试从outputs中提取
            if not answer_content:
                # 处理新的Dify响应格式，数据可能在data.outputs中
                outputs = None
                if 'data' in dify_data and 'outputs' in dify_data['data']:
                    outputs = dify_data['data']['outputs']
                elif 'outputs' in dify_data:
                    outputs = dify_data['outputs']
                
                if outputs:
                    # 尝试从outputs中提取内容
                    if '审查意见' in outputs:
                        answer_content = TaskService._extract_json_from_text(outputs['审查意见'])
                        current_app.logger.info(f"从outputs.审查意见中提取answer - 任务: {task_id}")
                    elif 'answer' in outputs:
                        answer_content = TaskService._extract_json_from_text(outputs['answer'])
                        current_app.logger.info(f"从outputs.answer中提取answer - 任务: {task_id}")
                    elif 'result' in outputs:
                        answer_content = TaskService._extract_json_from_text(outputs['result'])
                        current_app.logger.info(f"从outputs.result中提取answer - 任务: {task_id}")
                    elif 'content' in outputs:
                        answer_content = TaskService._extract_json_from_text(outputs['content'])
                        current_app.logger.info(f"从outputs.content中提取answer - 任务: {task_id}")
                    else:
                        # 如果有其他字段，取第一个字符串类型的值
                        for key, value in outputs.items():
                            if isinstance(value, str) and value.strip():
                                answer_content = TaskService._extract_json_from_text(value)
                                current_app.logger.info(f"从outputs.{key}中提取answer - 任务: {task_id}")
                                break
            
            if not answer_content:
                current_app.logger.warning(f"未能从Dify响应中提取到有效的answer内容 - 任务: {task_id}")
                current_app.logger.debug(f"Dify响应数据结构: {json.dumps(dify_data, ensure_ascii=False, indent=2)}")
            
            # 创建任务结果记录
            task_result = TaskResult(
                task_id=task_id,
                user_id=user_id,
                message_id=dify_data.get('message_id'),
                conversation_id=dify_data.get('conversation_id') or conversation_id,
                mode=dify_data.get('mode'),
                answer=answer_content,
                result_metadata=json.dumps(dify_data.get('metadata', {}), ensure_ascii=False) if dify_data.get('metadata') else None,
                full_response=json.dumps(dify_data, ensure_ascii=False)
            )
            
            task_result.save()
            
            # 更新任务状态为已完成
            task.update_status('completed')
            
            current_app.logger.info(f"Dify响应处理成功 - 任务: {task_id} - 结果ID: {task_result.id}")
            
            return task_result
            
        except Exception as e:
            current_app.logger.error(f"处理Dify响应失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            # 更新任务状态为失败
            if task_id:
                try:
                    task = Task.find_by_id(task_id)
                    if task:
                        task.update_status('failed')
                except:
                    pass
            raise e
    
    @staticmethod
    def send_dify_request(task_id, user_id, query, files=None, conversation_id=None):
        """发送流式请求到Dify并处理响应"""
        try:
            # 检查任务是否存在
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if task.user_id != user_id:
                raise ValueError("无权限访问此任务")
            
            # 获取对应任务类型的Dify配置
            dify_config = StandardConfigService.get_config_for_standard_type(task.task_type)
            
            # 准备请求数据
            request_data = {
                'inputs': {},
                'query': query,
                'response_mode': 'streaming',
                'conversation_id': conversation_id or '',
                'user': user_id
            }
            
            # 如果有文件，添加文件信息
            if files:
                request_data['files'] = [
                    {
                        'type': 'document',
                        'transfer_method': 'remote_url',
                        'upload_file_id': file.dify_file_id
                    }
                    for file in files if file.dify_file_id
                ]
            
            current_app.logger.info(f"发送Dify流式请求 - 任务: {task_id} - URL: {dify_config['api_url']}")
            
            # 发送请求到Dify
            response = requests.post(
                dify_config['api_url'],
                headers=dify_config['headers'],
                json=request_data,
                timeout=60,
                stream=True
            )
            
            response.raise_for_status()
            
            return response
            
        except Exception as e:
            current_app.logger.error(f"发送Dify流式请求失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def send_dify_request_blocking(task_id, user_id, query, files=None, conversation_id=None):
        """发送阻塞式请求到Dify并返回完整响应"""
        try:
            # 检查任务是否存在
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if task.user_id != user_id:
                raise ValueError("无权限访问此任务")
            
            # 获取对应任务类型的Dify配置
            dify_config = StandardConfigService.get_config_for_standard_type(task.task_type)
            
            # 检查文件要求
            has_valid_files = files and len(files) > 0 and any(file.dify_file_id for file in files)
            
            # 准备请求数据（非流式）
            request_data = {
                'inputs': {},
                'query': query,
                'response_mode': 'blocking',  # 使用阻塞模式
                'conversation_id': conversation_id or '',
                'user': str(user_id)  # 确保user是字符串
            }
            
            # 如果有文件，添加文件信息
            if has_valid_files:
                valid_files = [file for file in files if file.dify_file_id]
                request_data['files'] = [
                    {
                        'type': 'document',
                        'transfer_method': 'remote_url',
                        'upload_file_id': file.dify_file_id
                    }
                    for file in valid_files
                ]
                current_app.logger.info(f"添加文件到请求 - 任务: {task_id} - 文件数量: {len(valid_files)}")
            else:
                current_app.logger.warning(f"任务无有效文件 - 任务: {task_id}")
            
            current_app.logger.info(f"发送Dify阻塞请求 - 任务: {task_id} - URL: {dify_config['api_url']}")
            current_app.logger.info(f"请求数据: {request_data}")
            current_app.logger.info(f"请求头: {dify_config['headers']}")
            
            # 发送请求到Dify（不使用stream）
            response = requests.post(
                dify_config['api_url'],
                headers=dify_config['headers'],
                json=request_data,
                timeout=120  # 阻塞请求可能需要更长时间
            )
            
            # 记录响应状态和详情
            current_app.logger.info(f"Dify响应状态码: {response.status_code} - 任务: {task_id}")
            
            if response.status_code != 200:
                current_app.logger.error(f"Dify API错误 - 状态码: {response.status_code} - 响应: {response.text}")
                # 尝试解析错误详情
                try:
                    error_data = response.json()
                    current_app.logger.error(f"Dify错误详情: {error_data}")
                    
                    # 特殊处理文件要求错误
                    if error_data.get('message') == 'files is required in input form':
                        raise ValueError("此任务类型要求上传文件后才能进行处理。请先上传相关文档文件。")
                    elif 'Invalid upload file id format' in error_data.get('message', ''):
                        raise ValueError("文件上传有问题，请重新上传文件后再试。")
                        
                except ValueError:
                    raise  # 重新抛出我们自定义的错误
                except:
                    pass
            
            response.raise_for_status()
            result = response.json()
            
            # 构建标准化响应数据
            standardized_response = {
                'task_id': task_id,
                'message_id': result.get('message_id'),
                'conversation_id': result.get('conversation_id'),
                'mode': result.get('mode', 'blocking'),
                'answer': result.get('answer', ''),
                'metadata': result.get('metadata', {}),
                'created_at': result.get('created_at'),
                'full_response': result
            }
            
            # 保存到数据库
            task_result = TaskService.process_dify_response(
                task_id, 
                user_id, 
                standardized_response,
                result.get('conversation_id')
            )
            
            current_app.logger.info(f"Dify阻塞请求处理成功 - 任务: {task_id} - 结果ID: {task_result.id}")
            
            return standardized_response
            
        except Exception as e:
            current_app.logger.error(f"发送Dify阻塞请求失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            # 更新任务状态为失败
            try:
                task = Task.find_by_id(task_id)
                if task:
                    task.update_status('failed')
            except:
                pass
            raise e
    
    @staticmethod
    def get_task_files(task_id, user_id):
        """获取任务的文件列表"""
        try:
            # 检查任务是否存在
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if task.user_id != user_id:
                raise ValueError("无权限访问此任务")
            
            files = TaskFile.find_by_task_id(task_id)
            return files
            
        except Exception as e:
            current_app.logger.error(f"获取任务文件失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def get_task_results(task_id, user_id):
        """获取任务的结果列表"""
        try:
            # 检查任务是否存在
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if task.user_id != user_id:
                raise ValueError("无权限访问此任务")
            
            results = TaskResult.find_by_user_and_task(user_id, task_id)
            return results
            
        except Exception as e:
            current_app.logger.error(f"获取任务结果失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def delete_task(task_id, user_id):
        """删除任务及其相关数据"""
        try:
            # 检查任务是否存在
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if task.user_id != user_id:
                raise ValueError("无权限删除此任务")
            
            # 删除本地文件
            files = TaskFile.find_by_task_id(task_id)
            for file in files:
                try:
                    FileService.delete_local_file(file.file_path)
                except:
                    pass  # 忽略文件删除错误
            
            # 删除任务（级联删除相关记录）
            task.delete()
            
            current_app.logger.info(f"任务删除成功 - 任务: {task_id}")
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"删除任务失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def send_dify_request_with_input_files(task_id, user_id, query, input_files, conversation_id=None, inputs=None):
        """使用直接传递的文件信息发送阻塞式请求到Dify"""
        try:
            # 检查任务是否存在
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if task.user_id != user_id:
                raise ValueError("无权限访问此任务")
            
            # 获取对应任务类型的Dify配置
            dify_config = StandardConfigService.get_config_for_standard_type(task.task_type)
            
            # 准备请求数据，直接使用前端传递的结构
            request_data = {
                'inputs': inputs or {},
                'query': query,
                'response_mode': 'blocking',
                'conversation_id': conversation_id or '',
                'user': str(user_id)
            }
            
            # 确保files在正确的位置
            if input_files:
                # 直接使用前端传递的文件信息，但要确保格式正确
                formatted_files = []
                for file_info in input_files:
                    formatted_file = {
                        'type': file_info.get('type', 'document'),
                        'transfer_method': file_info.get('transfer_method', 'local_file'),  # 默认使用local_file
                        'upload_file_id': file_info.get('upload_file_id')
                    }
                    formatted_files.append(formatted_file)
                
                # 确保使用inputs.files格式（根据测试结果，这个Dify应用要求这种格式）
                request_data['inputs']['files'] = formatted_files
                current_app.logger.info(f"使用inputs.files格式 - 任务: {task_id} - 文件数量: {len(formatted_files)}")
            
            current_app.logger.info(f"发送Dify直传文件请求 - 任务: {task_id} - URL: {dify_config['api_url']}")
            current_app.logger.info(f"请求数据: {request_data}")
            current_app.logger.info(f"请求头: {dify_config['headers']}")
            
            # 发送请求到Dify
            response = requests.post(
                dify_config['api_url'],
                headers=dify_config['headers'],
                json=request_data,
                timeout=120
            )
            
            # 记录响应状态和详情
            current_app.logger.info(f"Dify响应状态码: {response.status_code} - 任务: {task_id}")
            
            if response.status_code != 200:
                current_app.logger.error(f"Dify API错误 - 状态码: {response.status_code} - 响应: {response.text}")
                # 尝试解析错误详情
                try:
                    error_data = response.json()
                    current_app.logger.error(f"Dify错误详情: {error_data}")
                    
                    # 特殊处理文件要求错误
                    if error_data.get('message') == 'files is required in input form':
                        raise ValueError("此任务类型要求上传文件后才能进行处理。请检查files参数格式。")
                    elif 'Invalid upload file id format' in error_data.get('message', ''):
                        raise ValueError("文件ID格式不正确，请检查upload_file_id参数。")
                        
                except ValueError:
                    raise  # 重新抛出我们自定义的错误
                except:
                    pass
            
            response.raise_for_status()
            result = response.json()
            
            # 构建标准化响应数据
            standardized_response = {
                'task_id': task_id,
                'message_id': result.get('message_id'),
                'conversation_id': result.get('conversation_id'),
                'mode': result.get('mode', 'blocking'),
                'answer': result.get('answer', ''),
                'metadata': result.get('metadata', {}),
                'created_at': result.get('created_at'),
                'full_response': result
            }
            
            # 保存到数据库
            task_result = TaskService.process_dify_response(
                task_id, 
                user_id, 
                standardized_response,
                result.get('conversation_id')
            )
            
            current_app.logger.info(f"Dify直传文件请求处理成功 - 任务: {task_id} - 结果ID: {task_result.id}")
            
            return standardized_response
            
        except Exception as e:
            current_app.logger.error(f"发送Dify直传文件请求失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            # 更新任务状态为失败
            try:
                task = Task.find_by_id(task_id)
                if task:
                    task.update_status('failed')
            except:
                pass
            raise e
    
    @staticmethod
    def send_dify_request_direct(task_id, user_id, request_data):
        """直接转发前端参数到Dify API，不做任何转换（同步版本，1小时超时）"""
        try:
            # 检查任务是否存在
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if task.user_id != user_id:
                raise ValueError("无权限访问此任务")
            
            # 获取对应任务类型的Dify配置
            dify_config = StandardConfigService.get_config_for_standard_type(task.task_type)
            
            current_app.logger.info(f"直接转发请求到Dify - 任务: {task_id} - URL: {dify_config['api_url']}")
            current_app.logger.info(f"转发的请求数据: {request_data}")
            current_app.logger.info(f"请求头: {dify_config['headers']}")
            
            # 直接转发前端请求数据到Dify，设置1小时超时，无重试
            response = requests.post(
                dify_config['api_url'],
                headers=dify_config['headers'],
                json=request_data,
                timeout=(30, 3600)  # 连接超时30秒，读取超时1小时
            )
            
            # 记录响应状态
            current_app.logger.info(f"Dify响应状态码: {response.status_code} - 任务: {task_id}")
            
            if response.status_code != 200:
                current_app.logger.error(f"Dify API错误 - 状态码: {response.status_code} - 响应: {response.text}")
                # 解析错误详情
                try:
                    error_data = response.json()
                    current_app.logger.error(f"Dify错误详情: {error_data}")
                    if response.status_code == 400:
                        raise ValueError(f"Dify API 参数错误: {error_data.get('message', '未知错误')}")
                    elif response.status_code == 401:
                        raise ValueError(f"Dify API 认证错误: {error_data.get('message', '认证失败')}")
                    elif response.status_code == 403:
                        raise ValueError(f"Dify API 权限错误: {error_data.get('message', '权限不足')}")
                    elif response.status_code == 500:
                        raise ValueError(f"Dify API 服务器错误: {error_data.get('message', '服务器内部错误')}")
                except ValueError:
                    raise
                except:
                    pass
            
            response.raise_for_status()
            result = response.json()
            
            # 构建响应数据（保持原始 Dify 响应）
            response_data = {
                'task_id': task_id,
                'dify_response': result  # 直接包含 Dify 的原始响应
            }
            
            # 保存到数据库
            task_result = TaskService.process_dify_response(
                task_id, 
                user_id, 
                result,  # 直接传递 Dify 的原始响应
                result.get('conversation_id')
            )
            
            current_app.logger.info(f"Dify直接转发请求处理成功 - 任务: {task_id} - 结果ID: {task_result.id}")
            
            return response_data
            
        except Exception as e:
            current_app.logger.error(f"Dify直接转发请求失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            # 更新任务状态为失败
            try:
                task = Task.find_by_id(task_id)
                if task:
                    task.update_status('failed')
            except:
                pass
            raise e
    
    @staticmethod
    def send_dify_request_direct_async(task_id, user_id, request_data):
        """异步执行 Dify API 请求的后台方法"""
        # 在主线程中获取应用实例
        app = current_app._get_current_object()
        
        def background_task():
            with app.app_context():  # 在后台线程中使用传递的应用实例
                try:
                    current_app.logger.info(f"开始后台执行 Dify API 请求 - 任务: {task_id}")
                    
                    # 更新任务状态为处理中 - 只有在调用标准处理接口时才更新为processing
                    task = Task.find_by_id(task_id)
                    if task:
                        task.update_status('processing')
                        current_app.logger.info(f"任务状态已更新为processing - 任务: {task_id}")
                    
                    # 调用同步版本的方法执行实际请求
                    TaskService.send_dify_request_direct(task_id, user_id, request_data)
                    
                    current_app.logger.info(f"后台 Dify API 请求执行成功 - 任务: {task_id}")
                    
                except Exception as e:
                    current_app.logger.error(f"后台 Dify API 请求执行失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
                    # 在异常情况下更新任务状态为失败
                    try:
                        task = Task.find_by_id(task_id)
                        if task:
                            task.update_status('failed')
                            current_app.logger.info(f"任务状态已更新为失败 - 任务: {task_id}")
                    except Exception as update_error:
                        current_app.logger.error(f"更新任务状态失败 - 任务: {task_id} - 错误: {str(update_error)}")
        
        try:
            # 启动后台线程
            thread = threading.Thread(target=background_task)
            thread.daemon = True  # 设置为守护线程
            thread.start()
            
            return True
            
        except Exception as e:
            # 如果启动后台线程失败，立即更新任务状态为失败
            current_app.logger.error(f"启动后台任务失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            try:
                task = Task.find_by_id(task_id)
                if task:
                    task.update_status('failed')
                    current_app.logger.info(f"任务状态已更新为失败（启动失败）- 任务: {task_id}")
            except Exception as update_error:
                current_app.logger.error(f"更新任务状态失败（启动失败）- 任务: {task_id} - 错误: {str(update_error)}")
            
            return False
    
    @staticmethod
    def get_task_results_paginated(task_id, user_id, page=1, per_page=20, sort_by='sn', sort_order='asc'):
        """获取任务结果的分页数据 - 专门用于需要分页展示的任务类型"""
        try:
            # 检查任务是否存在
            task = Task.find_by_id(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if task.user_id != user_id:
                raise ValueError("无权限访问此任务")
            
            # 检查任务类型是否支持分页
            pagination_supported_types = ['standard_review', 'standard_recommendation', 'standard_compliance']
            if task.task_type not in pagination_supported_types:
                raise ValueError(f"任务类型 '{task.get_task_type_display()}' 不支持分页查询，请使用任务详情接口获取完整结果")
            
            # 检查任务是否已完成
            if task.status != 'completed':
                raise ValueError(f"任务状态为 '{task.get_status_display()}'，只有已完成的任务才能进行分页查询")
            
            # 获取任务结果
            results = TaskResult.find_by_user_and_task(user_id, task_id)
            if not results:
                return {
                    'items': [],
                    'pagination': {
                        'current_page': page,
                        'per_page': per_page,
                        'total_items': 0,
                        'total_pages': 0,
                        'has_next': False,
                        'has_prev': False
                    },
                    'task_info': {
                        'id': task.id,
                        'task_type': task.task_type,
                        'task_type_display': task.get_task_type_display(),
                        'status': task.status,
                        'status_display': task.get_status_display()
                    }
                }
            
            # 解析最新结果的answer字段（JSON格式）
            latest_result = results[0]  # 按创建时间倒序，第一个是最新的
            
            # 尝试从answer字段获取数据
            items_data = None
            data_source = "answer"
            
            if latest_result.answer:
                try:
                    import json
                    # 首先尝试直接解析为JSON数组
                    items_data = json.loads(latest_result.answer)
                    if isinstance(items_data, list):
                        current_app.logger.info(f"从answer字段解析到 {len(items_data)} 条数据 - 任务: {task_id}")
                    else:
                        items_data = None  # 不是列表格式，继续尝试其他方式
                except json.JSONDecodeError:
                    # 如果直接解析失败，尝试处理多个JSON对象的情况
                    try:
                        # 检查是否包含多个JSON对象（用户提供的格式）
                        raw_text = latest_result.answer
                        if '}\n```\n```json\n{' in raw_text or raw_text.count('```json') > 1:
                            # 分割多个JSON块
                            json_blocks = []
                            
                            # 移除markdown标记并分割
                            text_lines = raw_text.split('\n')
                            current_json = ""
                            in_json_block = False
                            
                            for line in text_lines:
                                line = line.strip()
                                if line == '```json' or line == '```':
                                    if line == '```json':
                                        in_json_block = True
                                        current_json = ""
                                    elif line == '```' and in_json_block:
                                        in_json_block = False
                                        if current_json.strip():
                                            try:
                                                json_obj = json.loads(current_json)
                                                json_blocks.append(json_obj)
                                                current_app.logger.debug(f"成功解析JSON对象 - sn: {json_obj.get('sn', 'N/A')} - 任务: {task_id}")
                                            except json.JSONDecodeError as e:
                                                current_app.logger.warning(f"JSON对象解析失败 - 任务: {task_id} - 错误: {str(e)}")
                                        current_json = ""
                                elif in_json_block:
                                    current_json += line + "\n"
                            
                            # 如果还有剩余的JSON内容
                            if current_json.strip():
                                try:
                                    json_obj = json.loads(current_json)
                                    json_blocks.append(json_obj)
                                    current_app.logger.debug(f"成功解析剩余JSON对象 - sn: {json_obj.get('sn', 'N/A')} - 任务: {task_id}")
                                except json.JSONDecodeError as e:
                                    current_app.logger.warning(f"剩余JSON对象解析失败 - 任务: {task_id} - 错误: {str(e)}")
                            
                            if json_blocks:
                                items_data = json_blocks
                                current_app.logger.info(f"从answer字段解析到 {len(items_data)} 个JSON对象 - 任务: {task_id}")
                            else:
                                items_data = None
                        else:
                            # 使用_extract_json_from_text处理单个JSON的情况
                            clean_text = TaskService._extract_json_from_text(raw_text)
                            items_data = json.loads(clean_text)
                            if isinstance(items_data, list):
                                current_app.logger.info(f"从answer字段解析到 {len(items_data)} 条数据 - 任务: {task_id}")
                            else:
                                items_data = None
                    except json.JSONDecodeError:
                        items_data = None  # JSON解析失败，继续尝试其他方式
            
            # 如果answer字段为空或解析失败，尝试从full_response中的outputs提取
            if not items_data:
                if latest_result.full_response:
                    try:
                        import json
                        full_data = json.loads(latest_result.full_response)
                        
                        # 尝试从不同位置提取数据
                        outputs = None
                        if 'data' in full_data and 'outputs' in full_data['data']:
                            outputs = full_data['data']['outputs']
                            data_source = "full_response.data.outputs"
                        elif 'outputs' in full_data:
                            outputs = full_data['outputs']
                            data_source = "full_response.outputs"
                        
                        if outputs:
                            # 尝试从不同字段提取
                            for field_name in ['审查意见', 'answer', 'result', 'content']:
                                if field_name in outputs:
                                    try:
                                        if isinstance(outputs[field_name], str):
                                            # 使用新的提取方法处理可能的markdown格式
                                            clean_json = TaskService._extract_json_from_text(outputs[field_name])
                                            items_data = json.loads(clean_json)
                                        else:
                                            items_data = outputs[field_name]
                                        
                                        if isinstance(items_data, list):
                                            current_app.logger.info(f"从{data_source}.{field_name}字段解析到 {len(items_data)} 条数据 - 任务: {task_id}")
                                            break
                                        else:
                                            items_data = None
                                    except (json.JSONDecodeError, TypeError):
                                        continue
                    except json.JSONDecodeError:
                        pass
            
            if not items_data:
                raise ValueError("任务结果数据为空或无法解析")
            
            if not isinstance(items_data, list):
                raise ValueError("任务结果数据格式不正确，应为列表格式")
            
            current_app.logger.info(f"解析到 {len(items_data)} 条结果数据 - 任务: {task_id}")
            
            # 根据任务类型验证数据格式
            task_type = task.task_type
            required_fields_map = {
                'standard_review': ['sn', 'issueLocation', 'originalText', 'issueDescription', 'recommendedModification'],
                'standard_recommendation': ['sn', 'projectName', 'originalText', 'referenceStandard'],
                'standard_compliance': ['sn', 'projectName', 'originalText', 'isCompliant', 'suggestedRewrite', 'referenceStandard']
            }
            
            required_fields = required_fields_map.get(task_type, ['sn'])  # 默认只要求sn字段
            
            for i, item in enumerate(items_data):
                if not isinstance(item, dict):
                    current_app.logger.warning(f"第 {i+1} 条数据格式不正确 - 任务: {task_id}")
                    continue
                
                # 检查必要字段
                missing_fields = [field for field in required_fields if field not in item]
                if missing_fields:
                    current_app.logger.warning(f"第 {i+1} 条数据缺少字段: {missing_fields} - 任务: {task_id} - 任务类型: {task_type}")
            
            # 排序处理
            if sort_by == 'sn':
                # 按序号排序
                reverse = (sort_order.lower() == 'desc')
                try:
                    items_data.sort(key=lambda x: int(x.get('sn', 0)), reverse=reverse)
                except (ValueError, TypeError):
                    # 如果sn不是数字，按字符串排序
                    items_data.sort(key=lambda x: str(x.get('sn', '')), reverse=reverse)
            
            # 计算分页信息
            total_items = len(items_data)
            total_pages = (total_items + per_page - 1) // per_page  # 向上取整
            
            # 验证页码
            if page > total_pages and total_pages > 0:
                page = total_pages
            
            # 计算分页范围
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            
            # 获取当前页数据
            current_page_items = items_data[start_index:end_index]
            
            # 构建分页信息
            pagination_info = {
                'current_page': page,
                'per_page': per_page,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
            
            # 构建返回数据
            result = {
                'items': current_page_items,
                'pagination': pagination_info,
                'task_info': {
                    'id': task.id,
                    'task_type': task.task_type,
                    'task_type_display': task.get_task_type_display(),
                    'status': task.status,
                    'status_display': task.get_status_display(),
                    'title': task.title,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'updated_at': task.updated_at.isoformat() if task.updated_at else None
                }
            }
            
            current_app.logger.info(f"分页查询成功 - 任务: {task_id} - 页码: {page}/{total_pages} - 当前页数量: {len(current_page_items)}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"获取分页结果失败 - 任务: {task_id} - 错误: {str(e)}", exc_info=True)
            raise e
    
 