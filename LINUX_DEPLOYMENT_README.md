# Linux服务器部署指南

## 📋 项目部署说明

### 问题1: 项目是否可以直接复制到Linux服务器运行？

**答案**: ✅ **可以**，但需要满足以下条件：

#### 环境要求
- **Python**: 3.7+ (推荐 3.8+)
- **操作系统**: Ubuntu 18.04+, CentOS 7+, RHEL 7+ 或其他Linux发行版
- **数据库**: MySQL 5.7+ (必需)
- **内存**: 至少 512MB
- **磁盘**: 至少 1GB 可用空间

#### 快速部署步骤

1. **复制项目文件**
   ```bash
   # 上传项目到服务器
   scp -r /path/to/Dify_Code user@server:/opt/
   # 或者
   git clone <repository-url> /opt/Dify_Code
   ```

2. **安装依赖**
   ```bash
   cd /opt/Dify_Code
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
   ```

3. **配置环境**
   ```bash
   cp env_example.txt .env
   # 编辑 .env 文件配置数据库等信息
   nano .env
   ```

4. **启动服务**
   ```bash
   # 简单方式（关闭终端会停止）
   python3 run.py
   
   # 后台运行方式（推荐）
   ./start_background.sh
   ```

### 问题2: 关闭终端窗口会终止项目运行吗？

**答案**: ⚠️ **会终止**，但我们提供了多种解决方案：

#### 方案1: 使用nohup命令（简单）
```bash
# 使用我们提供的脚本
./start_background.sh    # 启动后台服务
./status_background.sh   # 查看服务状态  
./stop_background.sh     # 停止服务
```

#### 方案2: 使用screen命令
```bash
# 安装screen
sudo apt install screen  # Ubuntu/Debian
sudo yum install screen   # CentOS/RHEL

# 创建screen会话
screen -S user_system
python3 run.py

# 分离会话: Ctrl+A, D
# 重新连接: screen -r user_system
```

#### 方案3: 使用systemd服务（推荐生产环境）
```bash
# 使用我们提供的自动部署脚本
sudo ./deploy_linux.sh

# 手动管理服务
sudo systemctl start user-system    # 启动
sudo systemctl stop user-system     # 停止
sudo systemctl restart user-system  # 重启
sudo systemctl status user-system   # 查看状态
```

#### 方案4: 使用Docker（推荐）
```bash
# 如果有Docker环境
docker-compose up -d
```

## 🚀 快速开始

### Step 1: 上传项目
```bash
# 方式1: SCP上传
scp -r Dify_Code user@your-server:/opt/

# 方式2: Git克隆
ssh user@your-server
git clone <your-repo-url> /opt/Dify_Code
```

### Step 2: 安装依赖
```bash
cd /opt/Dify_Code
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: 配置环境变量
```bash
cp env_example.txt .env
# 编辑配置文件
nano .env

# 主要配置项：
# - SECRET_KEY: Flask密钥
# - JWT_SECRET_KEY: JWT密钥  
# - DB_HOST, DB_USERNAME, DB_PASSWORD: 数据库连接
```

### Step 4: 启动服务
```bash
# 开发/测试环境
./start_background.sh

# 生产环境（推荐）
sudo ./deploy_linux.sh
```

### Step 5: 验证服务
```bash
# 检查服务状态
./status_background.sh

# 测试API
curl http://localhost:5000/api/health
curl http://localhost:5000/api/ping
```

## 🔧 服务管理命令

### 简单后台运行方式
```bash
./start_background.sh     # 启动后台服务
./stop_background.sh      # 停止服务
./status_background.sh    # 查看状态
tail -f logs/app.log      # 查看应用日志
tail -f logs/nohup.log    # 查看系统日志
```

### systemd服务方式
```bash
sudo systemctl start user-system     # 启动服务
sudo systemctl stop user-system      # 停止服务
sudo systemctl restart user-system   # 重启服务
sudo systemctl enable user-system    # 开机自启
sudo systemctl disable user-system   # 禁用自启
sudo systemctl status user-system    # 查看状态
sudo journalctl -u user-system -f    # 查看日志
```

### Docker方式
```bash
docker-compose up -d        # 启动所有服务
docker-compose down         # 停止所有服务
docker-compose logs -f app  # 查看应用日志
docker-compose restart app  # 重启应用
```

## 🌐 外网访问配置

### 防火墙配置
```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 5000
sudo ufw enable

# CentOS/RHEL (firewalld)  
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# 直接使用iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

### Nginx反向代理（推荐）
```nginx
# /etc/nginx/sites-available/user-system
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 监控和日志

### 日志文件位置
- **应用日志**: `logs/app.log`
- **系统日志**: `logs/nohup.log` (nohup方式)
- **systemd日志**: `journalctl -u user-system` (systemd方式)

### 常用监控命令
```bash
# 查看实时日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log

# 查看服务状态
./status_background.sh

# 查看端口监听
netstat -tuln | grep 5000
```

## ⚠️ 注意事项

1. **生产环境**: 请使用systemd或Docker方式部署
2. **安全配置**: 修改默认密钥，配置防火墙
3. **数据库**: 项目仅支持MySQL数据库
4. **备份**: 定期备份数据和配置文件
5. **更新**: 定期更新系统和依赖包

## 🆘 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **权限问题**
   ```bash
   chmod +x *.sh
   chown -R $USER:$USER /opt/Dify_Code
   ```

3. **Python版本问题**
   ```bash
   python3 --version
   which python3
   ```

4. **依赖安装失败**
   ```bash
   pip install -r requirements.txt -v
   ```

5. **数据库连接问题**
   ```bash
   # 检查MySQL服务
   sudo systemctl status mysql
   
   # 测试连接
   mysql -h localhost -u root -p
   ``` 