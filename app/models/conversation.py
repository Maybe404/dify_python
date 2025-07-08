from app import db
from datetime import datetime
import uuid
import json

class Conversation(db.Model):
    """对话模型 - 存储与Dify的对话记录"""
    
    __tablename__ = 'conversations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='对话记录唯一标识符（UUID格式）')
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False, index=True, comment='任务ID')
    file_id = db.Column(db.String(36), db.ForeignKey('task_files.id'), nullable=True, index=True, comment='关联文件ID')
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    
    # 对话信息
    user_message = db.Column(db.Text, nullable=False, comment='用户发送的消息')
    dify_response = db.Column(db.Text, nullable=True, comment='Dify返回的响应（JSON格式）')
    
    # Dify相关ID
    conversation_id = db.Column(db.String(100), nullable=True, index=True, comment='Dify对话ID')
    message_id = db.Column(db.String(100), nullable=True, index=True, comment='Dify消息ID')
    
    # 状态和元数据
    status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed'), 
                      default='pending', nullable=False, index=True, comment='对话状态')
    response_time = db.Column(db.Float, nullable=True, comment='响应时间（秒）')
    error_message = db.Column(db.Text, nullable=True, comment='错误信息')
    
    # 请求参数记录
    request_data = db.Column(db.Text, nullable=True, comment='完整请求数据（JSON格式）')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    
    # 关联关系
    user = db.relationship('User', backref='conversations')
    
    def to_dict(self, include_relations=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'task_id': self.task_id,
            'file_id': self.file_id,
            'user_id': self.user_id,
            'user_message': self.user_message,
            'conversation_id': self.conversation_id,
            'message_id': self.message_id,
            'status': self.status,
            'response_time': self.response_time,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 解析JSON数据
        if self.dify_response:
            try:
                data['dify_response'] = json.loads(self.dify_response)
            except:
                data['dify_response'] = self.dify_response
        else:
            data['dify_response'] = None
            
        if self.request_data:
            try:
                data['request_data'] = json.loads(self.request_data)
            except:
                data['request_data'] = None
        else:
            data['request_data'] = None
            
        if include_relations:
            data['task'] = self.task.to_dict() if self.task else None
            data['file'] = self.file.to_dict() if self.file else None
            data['user'] = self.user.to_dict() if self.user else None
            
        return data
    
    def update_status(self, status, error=None):
        """更新对话状态"""
        self.status = status
        if error:
            self.error_message = error
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def set_dify_response(self, response_data, conversation_id=None, message_id=None):
        """设置Dify响应信息"""
        if isinstance(response_data, dict):
            self.dify_response = json.dumps(response_data, ensure_ascii=False)
        else:
            self.dify_response = str(response_data)
            
        if conversation_id:
            self.conversation_id = conversation_id
        if message_id:
            self.message_id = message_id
            
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def set_request_data(self, request_data):
        """设置请求数据"""
        if isinstance(request_data, dict):
            self.request_data = json.dumps(request_data, ensure_ascii=False)
        else:
            self.request_data = str(request_data)
        db.session.commit()
    
    def set_response_time(self, response_time):
        """设置响应时间"""
        self.response_time = response_time
        db.session.commit()
    
    def save(self):
        """保存对话到数据库"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """从数据库删除对话记录"""
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def find_by_id(conversation_id):
        """根据ID查找对话"""
        return Conversation.query.get(conversation_id)
    
    @staticmethod
    def find_by_task_id(task_id, page=1, per_page=20):
        """根据任务ID查找对话"""
        return Conversation.query.filter_by(task_id=task_id).order_by(
            Conversation.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def find_by_user_id(user_id, page=1, per_page=20):
        """根据用户ID查找对话"""
        return Conversation.query.filter_by(user_id=user_id).order_by(
            Conversation.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def find_by_conversation_id(dify_conversation_id):
        """根据Dify对话ID查找对话"""
        return Conversation.query.filter_by(conversation_id=dify_conversation_id).all()
    
    def __repr__(self):
        return f'<Conversation {self.id} ({self.status})>' 