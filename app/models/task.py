from app import db
from datetime import datetime
import uuid
import json

class Task(db.Model):
    """任务模型 - 管理六种标准处理任务"""
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='任务唯一标识符（UUID格式）')
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True, comment='发起任务的用户ID')
    task_type = db.Column(db.Enum('standard_interpretation', 'standard_recommendation', 'standard_comparison', 
                                 'standard_international', 'standard_compliance', 'standard_review'), 
                         nullable=False, index=True, comment='任务类型')
    title = db.Column(db.String(200), nullable=False, comment='任务标题')
    description = db.Column(db.Text, nullable=True, comment='任务描述')
    
    # 任务状态: pending(待处理), uploading(上传中), uploaded(上传完成), processing(处理中), completed(已完成), failed(失败)
    status = db.Column(db.Enum('pending', 'uploading', 'uploaded', 'processing', 'completed', 'failed'), 
                      default='pending', nullable=False, index=True, comment='任务状态')
    
    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    
    # 关联关系
    files = db.relationship('TaskFile', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    results = db.relationship('TaskResult', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='tasks')
    
    def to_dict(self, include_relations=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'task_type': self.task_type,
            'task_type_display': self.get_task_type_display(),
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'status_display': self.get_status_display(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            data['files'] = [file.to_dict() for file in self.files]
            data['results'] = [result.to_dict() for result in self.results]
            data['user'] = self.user.to_dict() if self.user else None
            
        return data
    
    def update_status(self, status):
        """更新任务状态"""
        self.status = status
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def save(self):
        """保存任务到数据库"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """从数据库删除任务"""
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def find_by_id(task_id):
        """根据ID查找任务"""
        return Task.query.get(task_id)
    
    @staticmethod
    def find_by_user_id(user_id, status=None, task_type=None, page=1, per_page=20):
        """根据用户ID查找任务，支持状态和类型筛选（支持多状态查询）"""
        query = Task.query.filter_by(user_id=user_id)
        if status:
            # 支持多状态查询，用逗号分隔
            if isinstance(status, str) and ',' in status:
                status_list = [s.strip() for s in status.split(',') if s.strip()]
                query = query.filter(Task.status.in_(status_list))
            else:
                query = query.filter_by(status=status)
        if task_type:
            query = query.filter_by(task_type=task_type)
        return query.order_by(Task.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def get_task_type_display(self):
        """获取任务类型的中文显示名称"""
        type_mapping = {
            'standard_interpretation': '标准解读',
            'standard_recommendation': '标准推荐', 
            'standard_comparison': '标准对比',
            'standard_international': '标准国际化辅助',
            'standard_compliance': '标准符合性检查',
            'standard_review': '标准审查'
        }
        return type_mapping.get(self.task_type, self.task_type)
    
    def get_status_display(self):
        """获取状态的中文显示名称"""
        status_mapping = {
            'pending': '待处理',
            'uploading': '上传中',
            'uploaded': '上传完成',
            'processing': '处理中',
            'completed': '已完成',
            'failed': '失败'
        }
        return status_mapping.get(self.status, self.status)
    
    @staticmethod
    def get_task_type_choices():
        """获取所有任务类型选项"""
        return [
            ('standard_interpretation', '标准解读'),
            ('standard_recommendation', '标准推荐'),
            ('standard_comparison', '标准对比'), 
            ('standard_international', '标准国际化辅助'),
            ('standard_compliance', '标准符合性检查'),
            ('standard_review', '标准审查')
        ]
    
    def __repr__(self):
        return f'<Task {self.title} ({self.status})>'


class TaskFile(db.Model):
    """任务文件模型 - 管理上传到任务的文件"""
    
    __tablename__ = 'task_files'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='文件唯一标识符')
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False, index=True, comment='任务ID')
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    
    # 本地文件信息
    original_filename = db.Column(db.String(255), nullable=False, comment='原始文件名')
    stored_filename = db.Column(db.String(255), nullable=False, comment='存储文件名')
    file_path = db.Column(db.String(500), nullable=False, comment='本地存储路径')
    file_size = db.Column(db.BigInteger, nullable=False, comment='文件大小（字节）')
    file_type = db.Column(db.String(100), nullable=False, comment='文件类型/MIME类型')
    file_extension = db.Column(db.String(20), nullable=True, comment='文件扩展名')
    
    # Dify相关信息
    dify_file_id = db.Column(db.String(100), nullable=True, index=True, comment='Dify返回的文件ID')
    dify_response_data = db.Column(db.Text, nullable=True, comment='Dify返回的完整信息（JSON格式）')
    
    # 状态信息
    upload_status = db.Column(db.Enum('pending', 'uploading', 'uploaded', 'failed'), 
                             default='pending', nullable=False, index=True, comment='上传状态')
    upload_error = db.Column(db.Text, nullable=True, comment='上传错误信息')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    
    # 关联关系
    user = db.relationship('User', backref='task_files')
    
    def to_dict(self, include_relations=False):
        """转换为字典格式"""
        # 生成文件下载URL
        download_url = f"/api/tasks/{self.task_id}/files/{self.id}/download"
        
        data = {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'download_url': download_url,  # 添加下载URL
            'file_size': self.file_size,
            'file_type': self.file_type,
            'file_extension': self.file_extension,
            'dify_file_id': self.dify_file_id,
            'upload_status': self.upload_status,
            'upload_error': self.upload_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 解析Dify响应数据
        if self.dify_response_data:
            try:
                data['dify_response'] = json.loads(self.dify_response_data)
            except:
                data['dify_response'] = None
        else:
            data['dify_response'] = None
            
        if include_relations:
            data['task'] = self.task.to_dict() if self.task else None
            
        return data
    
    def update_status(self, status, error=None):
        """更新上传状态"""
        self.upload_status = status
        if error:
            self.upload_error = error
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def set_dify_info(self, dify_file_id, dify_response):
        """设置Dify相关信息"""
        self.dify_file_id = dify_file_id
        if isinstance(dify_response, dict):
            self.dify_response_data = json.dumps(dify_response, ensure_ascii=False)
        else:
            self.dify_response_data = str(dify_response)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def save(self):
        """保存文件到数据库"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """从数据库删除文件记录"""
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def find_by_id(file_id):
        """根据ID查找文件"""
        return TaskFile.query.get(file_id)
    
    @staticmethod
    def find_by_task_id(task_id):
        """根据任务ID查找文件"""
        return TaskFile.query.filter_by(task_id=task_id).all()
    
    def __repr__(self):
        return f'<TaskFile {self.original_filename} ({self.upload_status})>'


class TaskResult(db.Model):
    """任务结果模型 - 存储Dify返回的处理结果"""
    
    __tablename__ = 'task_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='结果唯一标识符')
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False, index=True, comment='任务ID')
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    
    # Dify返回的信息
    message_id = db.Column(db.String(100), nullable=True, comment='Dify消息ID')
    conversation_id = db.Column(db.String(100), nullable=True, comment='Dify会话ID')
    mode = db.Column(db.String(50), nullable=True, comment='Dify模式')
    answer = db.Column(db.Text, nullable=True, comment='Dify返回的答案')
    result_metadata = db.Column(db.Text, nullable=True, comment='Dify返回的元数据（JSON格式）')
    
    # 完整的Dify响应
    full_response = db.Column(db.Text, nullable=True, comment='Dify返回的完整响应（JSON格式）')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    
    # 关联关系
    user = db.relationship('User', backref='task_results')
    
    def to_dict(self, include_relations=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'message_id': self.message_id,
            'conversation_id': self.conversation_id,
            'mode': self.mode,
            'answer': self.answer,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # 解析元数据
        if self.result_metadata:
            try:
                data['metadata'] = json.loads(self.result_metadata)
            except:
                data['metadata'] = None
        else:
            data['metadata'] = None
        
        # 解析完整响应
        if self.full_response:
            try:
                data['full_response'] = json.loads(self.full_response)
            except:
                data['full_response'] = None
        else:
            data['full_response'] = None
            
        if include_relations:
            data['task'] = self.task.to_dict() if self.task else None
            
        return data
    
    def save(self):
        """保存结果到数据库"""
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def find_by_task_id(task_id):
        """根据任务ID查找结果"""
        return TaskResult.query.filter_by(task_id=task_id).order_by(TaskResult.created_at.desc()).all()
    
    @staticmethod
    def find_by_user_and_task(user_id, task_id):
        """根据用户ID和任务ID查找结果"""
        return TaskResult.query.filter_by(user_id=user_id, task_id=task_id).order_by(TaskResult.created_at.desc()).all()
    
    def __repr__(self):
        return f'<TaskResult {self.task_id} ({self.created_at})>' 