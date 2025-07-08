import os
import uuid
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import requests
import json

class FileService:
    """文件服务 - 处理文件上传、存储和Dify集成"""
    
    # 允许的文件类型
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
        'ppt', 'pptx', 'xls', 'xlsx', 'csv', 'md', 'json', 'xml'
    }
    
    # 最大文件大小 (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    @staticmethod
    def get_valid_extension(filename):
        """获取有效的文件扩展名，处理边缘情况"""
        if not filename or not isinstance(filename, str):
            return ''
        
        # 清理文件名
        filename = filename.strip()
        if not filename or filename == '.' or filename == '..':
            return ''
        
        # 获取扩展名
        name, ext = os.path.splitext(filename)
        
        # 检查扩展名是否有效
        if not ext or ext == '.' or len(ext) < 2:
            return ''
        
        # 移除点并转换为小写
        ext_clean = ext[1:].lower()
        
        # 验证扩展名是否在允许列表中
        if ext_clean not in FileService.ALLOWED_EXTENSIONS:
            return ''
        
        return f".{ext_clean}"  # 返回小写的扩展名（包含点）
    
    @staticmethod
    def get_data_directory():
        """获取数据存储目录"""
        from flask import current_app
        try:
            # 优先使用配置中的上传目录
            return current_app.config['Config'].get_upload_directory()
        except (RuntimeError, KeyError):
            # 如果没有应用上下文或配置，使用默认路径
            from app.config.config import Config
            return Config.get_upload_directory()
    
    @staticmethod
    def generate_storage_path(user_id, original_filename):
        """生成文件存储路径 - 按时间日期用户ID分类存储"""
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        day = now.strftime('%d')
        
        # 创建目录结构: data/2024/01/15/user_id/
        directory = os.path.join(
            FileService.get_data_directory(),
            year, month, day, user_id
        )
        
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # 获取有效的文件扩展名
        file_extension = FileService.get_valid_extension(original_filename)
        if not file_extension:
            # 如果没有有效扩展名，默认为.txt
            file_extension = '.txt'
            try:
                current_app.logger.warning(f"文件 {original_filename} 没有有效扩展名，默认使用 .txt")
            except RuntimeError:
                # 没有应用上下文时不记录日志
                pass
        
        stored_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        return os.path.join(directory, stored_filename), stored_filename
    
    @staticmethod
    def allowed_file(filename):
        """检查文件类型是否允许"""
        if not filename or not isinstance(filename, str):
            return False
        
        filename = filename.strip()
        if not filename or filename == '.' or filename == '..':
            return False
        
        # 使用新的扩展名获取方法
        extension = FileService.get_valid_extension(filename)
        return bool(extension)
    
    @staticmethod
    def validate_file(file):
        """验证文件"""
        errors = []
        
        if not file:
            errors.append("未选择文件")
            return False, errors
        
        if not file.filename:
            errors.append("文件名为空")
            return False, errors
        
        # 更严格的文件名验证
        filename = file.filename.strip()
        if not filename or filename == '.' or filename == '..':
            errors.append("文件名无效")
        
        if not FileService.allowed_file(filename):
            errors.append(f"不支持的文件类型。支持的类型: {', '.join(FileService.ALLOWED_EXTENSIONS)}")
        
        # 检查文件大小（如果可以获取到）
        if hasattr(file, 'content_length') and file.content_length:
            if file.content_length > FileService.MAX_FILE_SIZE:
                errors.append(f"文件大小超过限制（最大 {FileService.MAX_FILE_SIZE // (1024*1024)}MB）")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def save_file(file, user_id):
        """保存文件到本地"""
        try:
            # 验证文件
            is_valid, errors = FileService.validate_file(file)
            if not is_valid:
                return False, None, errors[0]
            
            # 生成存储路径
            file_path, stored_filename = FileService.generate_storage_path(user_id, file.filename)
            
            # 保存文件
            file.save(file_path)
            
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            file_extension = FileService.get_valid_extension(file.filename)
            
            # 如果没有有效扩展名，使用默认扩展名
            if not file_extension:
                file_extension = '.txt'
                try:
                    current_app.logger.warning(f"文件 {file.filename} 没有有效扩展名，使用默认扩展名 .txt")
                except RuntimeError:
                    # 没有应用上下文时不记录日志
                    pass
            
            # 处理文件名：确保中文文件名能正确处理
            original_filename = file.filename
            if not original_filename or len(original_filename.strip()) == 0:
                # 如果文件名为空，使用基于扩展名的默认名称
                original_filename = f"file{file_extension}"
            
            file_info = {
                'original_filename': original_filename,  # 保持原始文件名，不使用secure_filename避免中文问题
                'stored_filename': stored_filename,
                'file_path': file_path,
                'file_size': file_size,
                'file_type': file.content_type or 'application/octet-stream',
                'file_extension': file_extension
            }
            
            current_app.logger.info(f"文件保存成功 - 用户: {user_id} - 文件: {file.filename} - 大小: {file_size}字节")
            
            return True, file_info, None
            
        except Exception as e:
            current_app.logger.error(f"文件保存失败 - 用户: {user_id} - 错误: {str(e)}", exc_info=True)
            return False, None, f"文件保存失败: {str(e)}"
    
    @staticmethod
    def upload_to_dify(file_path, filename, api_key, user_id, api_url=None):
        """上传文件到Dify"""
        try:
            if not api_url:
                api_url = os.getenv('DIFY_FILE_UPLOAD_URL', 'http://10.100.100.93/v1/files/upload')
            
            # 验证文件名和扩展名
            if not filename or not isinstance(filename, str):
                raise ValueError("文件名无效")
            
            # 智能处理文件名和扩展名
            valid_extension = FileService.get_valid_extension(filename)
            
            # 如果没有有效扩展名，检查是否整个文件名就是一个扩展名
            if not valid_extension:
                # 检查是否整个文件名就是一个扩展名（如'pdf', 'txt'等）
                if filename.lower() in FileService.ALLOWED_EXTENSIONS:
                    valid_extension = f".{filename.lower()}"
                    filename = f"document{valid_extension}"
                    try:
                        current_app.logger.warning(f"上传到Dify时修正文件名（仅扩展名）: {filename}")
                    except RuntimeError:
                        pass
                else:
                    valid_extension = '.txt'
                    filename = f"file{valid_extension}"
                    try:
                        current_app.logger.warning(f"上传到Dify时使用默认文件名: {filename}")
                    except RuntimeError:
                        pass
            else:
                # 检查文件名是否只是扩展名（secure_filename造成的问题）
                name_without_ext = os.path.splitext(filename)[0]
                if not name_without_ext or name_without_ext.strip() == '':
                    # 如果文件名只是扩展名，生成一个安全的文件名
                    filename = f"document{valid_extension}"
                    try:
                        current_app.logger.warning(f"上传到Dify时修正文件名（原文件名无效）: {filename}")
                    except RuntimeError:
                        pass
                else:
                    # 确保文件名是安全的，对于中文文件名生成英文替代
                    import re
                    safe_name = re.sub(r'[^\w\-_.]', '_', name_without_ext)
                    if not safe_name or safe_name == '_':
                        safe_name = 'document'
                    filename = f"{safe_name}{valid_extension}"
            
            # 准备请求头
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            current_app.logger.info(f"开始上传文件到Dify - 文件: {filename} - 用户: {user_id} - URL: {api_url}")
            
            # 按照Dify API要求的格式上传
            with open(file_path, 'rb') as f:
                files = {
                    'file': (filename, f, 'application/octet-stream')
                }
                data = {
                    'user': user_id  # 使用实际用户ID
                }
                
                response = requests.post(
                    api_url, 
                    headers=headers, 
                    files=files, 
                    data=data,
                    timeout=60
                )
                
                response.raise_for_status()
                
                result = response.json()
                current_app.logger.info(f"文件上传到Dify成功 - 文件: {filename} - Dify文件ID: {result.get('id', 'unknown')}")
                return True, result, None
                    
        except requests.exceptions.RequestException as e:
            error_msg = f"Dify上传请求失败: {str(e)}"
            current_app.logger.error(error_msg, exc_info=True)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"上传到Dify时发生错误: {str(e)}"
            current_app.logger.error(error_msg, exc_info=True)
            return False, None, error_msg
    
    @staticmethod
    def delete_local_file(file_path):
        """删除本地文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                current_app.logger.info(f"本地文件删除成功: {file_path}")
                return True
            else:
                current_app.logger.warning(f"要删除的文件不存在: {file_path}")
                return False
        except Exception as e:
            current_app.logger.error(f"删除本地文件失败: {file_path} - 错误: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def get_file_info(file_path):
        """获取文件信息"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'exists': True
            }
        except Exception as e:
            current_app.logger.error(f"获取文件信息失败: {file_path} - 错误: {str(e)}")
            return None
    
    @staticmethod
    def get_supported_types():
        """获取支持的文件类型"""
        return list(FileService.ALLOWED_EXTENSIONS) 