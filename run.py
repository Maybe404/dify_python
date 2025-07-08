from app import create_app
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建Flask应用实例
app = create_app()

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"启动服务器: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug) 