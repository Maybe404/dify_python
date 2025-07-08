import unittest
import json
from app import create_app, db
from app.models.user import User

class AuthTestCase(unittest.TestCase):
    """认证功能测试用例"""
    
    def setUp(self):
        """测试前准备"""
        import os
        
        # 设置测试环境配置
        os.environ['FLASK_CONFIG'] = 'testing'
        
        # 确保测试数据库配置存在
        if not os.getenv('TEST_DB_PASSWORD') and not os.getenv('DB_PASSWORD'):
            os.environ['DB_PASSWORD'] = 'test_password'  # 测试用的默认密码
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        with self.app.app_context():
            # 创建测试数据库表
            try:
                db.create_all()
            except Exception as e:
                self.fail(f"❌ 测试数据库连接失败: {e}. 请确保MySQL测试数据库 'user_system_test' 存在并可访问")
    
    def tearDown(self):
        """测试后清理"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_user_registration(self):
        """测试用户注册"""
        response = self.client.post('/api/auth/register', 
                                  json={
                                      'username': 'testuser',
                                      'email': 'test@example.com',
                                      'password': 'TestPass123'
                                  })
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], '注册成功')
    
    def test_user_login(self):
        """测试用户登录"""
        # 先注册一个用户
        self.client.post('/api/auth/register', 
                        json={
                            'username': 'testuser',
                            'email': 'test@example.com',
                            'password': 'TestPass123'
                        })
        
        # 测试登录
        response = self.client.post('/api/auth/login',
                                  json={
                                      'credential': 'testuser',
                                      'password': 'TestPass123'
                                  })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('access_token', data['data'])
    
    def test_invalid_registration(self):
        """测试无效注册数据"""
        response = self.client.post('/api/auth/register',
                                  json={
                                      'username': 'ab',  # 用户名太短
                                      'email': 'invalid-email',  # 无效邮箱
                                      'password': '123'  # 密码太简单
                                  })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('errors', data)

if __name__ == '__main__':
    unittest.main() 