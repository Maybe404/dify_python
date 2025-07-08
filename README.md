# 用户管理系统

这是一个基于Flask的用户管理系统，提供完整的用户认证、密码管理、日志记录等功能。使用MySQL数据库，具备完善的环境配置和部署方案。

## 📖 文档导航

- 🎯 [API接口文档](docs/api_index.html) - 可视化API文档索引
- 📋 [详细API文档](docs/api.md) - 完整的API接口说明  
- 🧪 [前端测试工具](web_test/index.html) - 内置API测试界面
- 🔧 [调试工具](web_test/debug.html) - API连接诊断工具
- ⚙️ [配置检查清单](docs/configuration_checklist.md) - 重要配置指南
- 🚀 [部署指南](#linux-服务器部署) - Linux服务器完整部署步骤
- 🌍 [环境配置指南](docs/environment_guide.md) - 开发/生产环境管理
- 📋 [日志系统指南](docs/logs_guide.md) - 日志记录、查看和分析

## 数据库说明

### 数据库配置
- **主要数据库**: 远程MySQL数据库
- **MySQL数据库**: 高性能关系型数据库 (`mysql+pymysql://`) - 唯一支持的数据库

### 用户信息存储
用户信息存储在远程MySQL数据库的 `users` 表中，包含以下字段：
- `id`: 用户唯一标识符（主键，自增）
- `username`: 用户名（唯一，3-20字符）
- `email`: 邮箱地址（唯一）
- `password_hash`: 加密后的密码（bcrypt哈希）
- `is_active`: 用户状态（激活/禁用）
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 远程MySQL数据库配置
请参考 `docs/database_config.md` 文档进行远程MySQL数据库配置。支持各大云服务商的MySQL数据库。

## 项目结构说明

```
├── app/                    # 应用程序主目录
│   ├── __init__.py        # Flask应用工厂函数
│   ├── models/            # 数据模型目录
│   │   ├── __init__.py   
│   │   └── user.py       # 用户模型（数据库表结构）
│   ├── routes/            # 路由处理目录
│   │   ├── __init__.py   
│   │   └── auth.py       # 认证相关路由（API接口）
│   ├── utils/             # 工具函数目录
│   │   ├── __init__.py   
│   │   └── security.py   # 安全相关工具函数（数据验证）
│   └── config/            # 配置文件目录
│       ├── __init__.py   
│       └── config.py     # 应用配置（数据库、JWT等）
├── scripts/               # 脚本目录
│   ├── init_db.py        # 数据库初始化脚本
│   └── jwt_debug_consolidated.py # JWT调试脚本
├── tests/                 # 测试文件目录
│   ├── __init__.py       
│   └── test_auth.py      # 认证功能测试
├── docs/                  # 文档目录
│   ├── api.md            # API接口文档
│   ├── database_config.md # 数据库配置使用说明
│   ├── configuration_checklist.md # 配置检查清单（重要）
│   ├── mysql_setup.md    # MySQL数据库设置指南（已废弃）
│   └── deployment.md     # 部署指南
├── web_test/              # 前端测试页面
│   ├── index.html        # 测试页面主文件
│   ├── style.css         # 页面样式文件
│   ├── script.js         # JavaScript逻辑文件
│   └── README.md         # 前端测试说明文档
├── instance/              # 实例文件目录（可删除）
├── requirements.txt       # 项目依赖
├── run.py                # 应用启动文件
├── test_mysql_connection.py # MySQL连接测试脚本
├── database_setup.sql    # MySQL建表脚本
└── env_example.txt       # 环境变量示例文件

```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 环境配置

#### 方式一：快速设置（推荐）
```bash
# 运行快速设置脚本，自动创建.env文件
python quick_setup.py
```

#### 方式二：手动配置
```bash
# Windows
copy env_example.txt .env

# Linux/Mac
cp env_example.txt .env
```

然后编辑 `.env` 文件，配置数据库连接信息和安全密钥。

⚠️ **重要**：请参考 `docs/configuration_checklist.md` 获取完整的配置指南。

### 3. 数据库设置

#### 配置远程MySQL数据库
1. 参考 `docs/database_config.md` 获取详细配置说明
2. 使用 `database_setup.sql` 脚本在您的远程MySQL数据库中创建表
3. 编辑 `.env` 文件，填入您的远程MySQL连接信息：
   ```bash
   DB_HOST=your-mysql-host.com
   DB_PORT=3306
   DB_USERNAME=your-username
   DB_PASSWORD=your-password
   DB_NAME=your-database-name
   ```
4. 测试数据库连接：
   ```bash
   python test_mysql_connection.py
   ```
5. 初始化数据库（可选，如果需要创建测试用户）：
   ```bash
   python scripts/init_db.py
   ```

### 4. 运行应用
```bash
python run.py
```

应用将在 `http://localhost:5000` 启动

## 前端测试页面

项目包含一个简单的前端测试页面，用于测试所有API接口：

1. **打开测试页面**：
   ```bash
   # 在浏览器中打开
   web_test/index.html
   ```

2. **功能特性**：
   - 🔗 实时连接状态监控
   - 👤 用户状态管理
   - 📝 完整的API接口测试
   - ⚡ 一键测试所有功能
   - 📋 详细的操作日志

3. **使用方法**：
   - 确保后端服务正在运行
   - 在浏览器中打开 `web_test/index.html`
   - 点击"一键测试所有功能"进行自动测试
   - 或手动测试各个API接口

详细说明请查看 `web_test/README.md` 文件。

## 数据库迁移

MySQL数据库初始化：
```bash
# 初始化MySQL数据库表
python scripts/init_db.py
```

## 📖 API文档

### 🚀 **Dify API V2 (推荐使用)**

V2采用应用场景配置管理，支持多个页面使用不同的API配置：

**完整的V2接口文档**: [`docs/API_V2_DOCUMENTATION.md`](docs/API_V2_DOCUMENTATION.md)

**核心接口**:
```javascript
// 多语言问答页面
POST /api/dify/v2/multilingual_qa/chat-simple
GET  /api/dify/v2/multilingual_qa/conversations
GET  /api/dify/v2/multilingual_qa/messages

// 标准查询页面  
POST /api/dify/v2/standard_query/chat-simple
GET  /api/dify/v2/standard_query/conversations
GET  /api/dify/v2/standard_query/messages

// 配置管理
GET  /api/dify/v2/scenarios                    # 获取所有应用场景
GET  /api/dify/v2/{scenario}/config           # 获取场景配置
```

### 📄 **任务结果分页查询API (新增)**

为了优化大量结果数据的展示，新增专门的分页查询接口：

**分页接口文档**: [`docs/PAGINATION_API_GUIDE.md`](docs/PAGINATION_API_GUIDE.md)

**分页接口**:
```javascript
// 分页查询任务结果（仅支持特定任务类型）
GET  /api/tasks/{task_id}/results/paginated   # 获取分页结果
```

**支持的任务类型**:
- `standard_review` - 标准审查
- `standard_recommendation` - 标准推荐  
- `standard_international` - 标准国际化辅助

**请求参数**:
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20，最大100）
- `sort_by`: 排序字段（默认sn）
- `sort_order`: 排序方向（asc/desc，默认asc）

### 🔄 **V1 兼容性接口**

为了保持向后兼容，V1接口仍然可用：

**传统接口文档**: [`docs/api.md`](docs/api.md)

```javascript
// V1 接口（向后兼容，使用 multilingual_qa 场景）
POST /api/dify/chat-simple
GET  /api/dify/conversations  
GET  /api/dify/messages
GET  /api/dify/config
```

### 📋 **迁移指南**

**架构优化指南**: [`docs/DIFY_API_OPTIMIZATION_GUIDE.md`](docs/DIFY_API_OPTIMIZATION_GUIDE.md)

## 功能特性

### 🔐 用户管理系统
- ✅ 用户注册（用户名可选，邮箱必填）
- ✅ 用户登录（支持用户名或邮箱登录）
- ✅ 用户登出（JWT token撤销）
- ✅ 密码加密存储（bcrypt哈希）
- ✅ JWT token认证
- ✅ 强密码验证（12位，包含大小写字母、数字、特殊字符）

### 🤖 Dify API 集成系统

> **现代化的 Dify API 集成中间件，支持多应用场景配置管理**

## 📋 核心特性

- 🎯 **多场景配置管理** - 支持不同页面使用不同的 Dify API 配置
- 🔐 **JWT 身份验证** - 完整的用户认证和权限管理系统  
- 📊 **实时流式响应** - 支持 Dify API 的流式对话响应
- 📝 **任务管理系统** - 文件上传和任务处理功能
- 🗄️ **MySQL 数据库** - 可靠的数据持久化存储
- 📋 **完整的日志系统** - 详细的操作日志和错误追踪
- 🔄 **自动化部署** - 支持 Linux 服务器一键部署

## 🎨 支持的应用场景

| 场景标识 | 名称 | 描述 | API 路径 |
|---------|------|------|----------|
| `multilingual_qa` | 多语言问答 | 多语言问答页面专用配置 | `/api/dify/v2/multilingual_qa/*` |
| `standard_query` | 标准查询 | 标准查询页面专用配置 | `/api/dify/v2/standard_query/*` |

## 🚀 API 接口

### 📡 **基础路径结构**

```
https://your-domain.com/api/dify/v2/{scenario}/{endpoint}
```

### 🔗 **核心接口列表**

| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| **聊天消息** | `POST` | `/api/dify/v2/{scenario}/chat-simple` | 发送聊天消息，支持流式响应 |
| **会话列表** | `GET` | `/api/dify/v2/{scenario}/conversations` | 获取会话列表 |
| **消息历史** | `GET` | `/api/dify/v2/{scenario}/messages` | 获取消息历史记录 |
| **场景配置** | `GET` | `/api/dify/v2/{scenario}/config` | 获取场景配置信息 |
| **场景列表** | `GET` | `/api/dify/v2/scenarios` | 获取所有支持的场景 |

### 🔄 **向后兼容接口**

为了平滑迁移，系统提供向后兼容的路由，自动转发到 `multilingual_qa` 场景：

| 兼容接口 | 自动转发到 |
|----------|------------|
| `/api/dify/v2/chat-simple` | `/api/dify/v2/multilingual_qa/chat-simple` |
| `/api/dify/v2/conversations` | `/api/dify/v2/multilingual_qa/conversations` |
| `/api/dify/v2/messages` | `/api/dify/v2/multilingual_qa/messages` |
| `/api/dify/v2/config` | `/api/dify/v2/scenarios` |

### 🛠️ 系统基础设施
- ✅ 使用MySQL高性能数据库
- ✅ 完整的API文档（V1和V2）
- ✅ 单元测试
- ✅ 数据库迁移工具
- ✅ 完善的日志系统
- ✅ 错误处理和监控

## 🔍 日志系统

### 日志配置

项目内置了完善的日志系统，支持开发和生产环境的不同配置：

**日志位置**：
- 📁 **开发环境**: 控制台输出 + `logs/app.log`
- 📁 **生产环境**: `logs/app.log` （轮转日志，单文件最大10MB）

**日志级别**：
- 🔧 **开发环境**: DEBUG级别（详细调试信息）
- 🚀 **生产环境**: INFO级别（重要信息记录）

**日志内容**：
- 用户登录/注册操作
- API请求记录
- 错误和异常信息
- 应用启动信息

**查看日志**：
```bash
# 查看最新日志
tail -f logs/app.log

# 查看错误日志
grep "ERROR" logs/app.log

# 查看今天的登录记录
grep "登录" logs/app.log | grep $(date +%Y-%m-%d)
```

### 📊 日志分析工具

项目提供了强大的日志分析工具，帮助您快速定位问题：

```bash
# 查看日志摘要和统计信息
python scripts/log_analyzer.py

# 搜索特定关键词
python scripts/log_analyzer.py --search "登录失败"

# 过滤特定级别的日志
python scripts/log_analyzer.py --level ERROR

# 查看最近1小时的日志
python scripts/log_analyzer.py --hours 1

# 组合搜索
python scripts/log_analyzer.py --search "用户" --level INFO --hours 2
```

### 📝 详细日志记录

项目包含完整的日志记录系统，记录以下信息：

1. **API请求日志**：
   - 请求方法、路径、IP地址、User-Agent
   - 响应状态码、处理耗时、请求ID
   - 完整的请求追踪链路

2. **安全事件日志**：
   - 用户登录/注册成功/失败及原因
   - 密码修改、用户登出操作
   - 可疑活动检测和告警

3. **业务操作日志**：
   - 用户操作记录（CRUD操作）
   - 数据库操作追踪
   - 系统状态变更记录

4. **性能监控日志**：
   - 慢查询检测（>1秒）
   - API响应时间统计
   - 资源使用监控

5. **错误处理日志**：
   - 系统异常详细堆栈
   - 数据验证错误
   - 网络连接问题

### 🔍 日志查看示例

```bash
# 查看系统错误
python scripts/log_analyzer.py --level ERROR

# 检查登录问题
python scripts/log_analyzer.py --search "登录" --hours 24

# 监控性能问题
python scripts/log_analyzer.py --search "耗时"

# 安全事件分析
python scripts/log_analyzer.py --search "安全事件"

# 检查特定IP的活动
python scripts/log_analyzer.py --search "IP: 192.168.1.100"
```

**日志分析报告示例**：
- 📈 基本统计（总条数、时间范围、各级别分布）
- 🔴 错误统计（错误总数、最近错误列表）
- 🔒 安全事件统计（登录成功/失败、注册等）
- 🌐 API请求统计（总数、平均响应时间、慢请求）
- 🌍 最活跃IP地址和用户统计

详细的日志系统文档请查看：[docs/logging_system.md](docs/logging_system.md)

## 🔐 JWT Token 问题排查

如果遇到token验证问题（如"Invalid header string"错误），请查看：[docs/jwt_troubleshooting.md](docs/jwt_troubleshooting.md)

**快速诊断命令**：
```bash
# JWT token 诊断工具
python scripts/test_jwt_token.py

# 查看token相关错误日志
python scripts/log_analyzer.py --search "token" --level ERROR
```

**日志配置环境变量**：
```bash
LOG_LEVEL=INFO                    # 日志级别: DEBUG/INFO/WARNING/ERROR
LOG_TO_STDOUT=False               # 是否输出到控制台
LOG_TO_FILE=True                  # 是否写入文件
LOG_FILE_PATH=logs/app.log        # 日志文件路径
LOG_MAX_BYTES=10485760           # 单文件最大大小(10MB)
LOG_BACKUP_COUNT=10              # 保留的备份文件数量
```

## 🚀 Ubuntu服务器快速部署

### 系统要求
- Ubuntu 18.04+ 
- Python 3.7+
- MySQL数据库（本地或远程）

### 快速部署（复制项目到maybe_code文件夹）

#### 1. 准备环境
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install python3 python3-pip python3-venv mysql-client -y

# 进入项目目录
cd /path/to/maybe_code/Dify_Code
```

#### 2. 安装依赖
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 配置环境
```bash
# 复制环境配置
cp env_example.txt .env

# 编辑配置文件（重要！）
nano .env
```

**必须配置的环境变量**：
```bash
# 生产环境设置
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# 数据库配置
DB_HOST=your-mysql-host
DB_USERNAME=your-username  
DB_PASSWORD=your-password
DB_NAME=your-database-name

# 服务器配置
HOST=0.0.0.0
PORT=5000
```

#### 4. 启动服务命令

**启动服务**：
```bash
# 进入项目目录
cd /path/to/maybe_code/Dify_Code

# 激活虚拟环境
source venv/bin/activate

# 后台启动服务
nohup python run.py > logs/server.log 2>&1 &

# 保存进程ID（用于后续停止服务）
echo $! > server.pid

# 查看启动状态
tail -f logs/server.log
```

#### 5. 停止服务命令

**停止服务**：
```bash
# 进入项目目录
cd /path/to/maybe_code/Dify_Code

# 方式1：使用保存的进程ID
if [ -f server.pid ]; then
    kill $(cat server.pid)
    rm server.pid
    echo "服务已停止"
else
    echo "未找到进程ID文件"
fi

# 方式2：强制停止所有相关进程
pkill -f "python run.py"
echo "所有相关进程已停止"
```

#### 6. 服务管理命令

**查看服务状态**：
```bash
# 查看进程
ps aux | grep "python run.py"

# 查看端口占用
netstat -tlnp | grep 5000

# 查看应用日志
tail -f logs/app.log

# 查看服务器日志
tail -f logs/server.log
```

**重启服务**：
```bash
# 进入项目目录
cd /path/to/maybe_code/Dify_Code

# 停止服务
if [ -f server.pid ]; then
    kill $(cat server.pid)
    rm server.pid
fi

# 等待3秒
sleep 3

# 重新启动
source venv/bin/activate
nohup python run.py > logs/server.log 2>&1 &
echo $! > server.pid

echo "服务已重启"
```

### 防火墙设置
```bash
# 开放5000端口
sudo ufw allow 5000

# 查看防火墙状态
sudo ufw status
```

### 测试部署
```bash
# 测试API连接
curl http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"TestPass123"}'
```

---

## 🚀 Linux服务器部署

### 系统要求

- Ubuntu 18.04+ / CentOS 7+ / Debian 10+
- Python 3.8+
- 2GB+ RAM
- 20GB+ 磁盘空间

### 部署步骤

#### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y   # Ubuntu/Debian
# sudo yum update -y                     # CentOS

# 安装必需软件
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor
# sudo yum install -y python3 python3-pip git nginx supervisor  # CentOS

# 创建部署用户
sudo useradd -m -s /bin/bash appuser
sudo usermod -aG www-data appuser
```

#### 2. 克隆项目

```bash
# 切换到部署用户
sudo su - appuser

# 克隆项目
cd /home/appuser
git clone <your-repo-url> user_system
cd user_system

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 配置环境

```bash
# 复制配置文件
cp env_example.txt .env

# 编辑配置文件
nano .env
```

**生产环境配置**：
```bash
# Flask应用配置
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here
HOST=127.0.0.1
PORT=5000

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600

# 数据库配置
DB_HOST=your-database-host
DB_PORT=3306
DB_USERNAME=your-username
DB_PASSWORD=your-password
DB_NAME=your-database-name

# 日志配置
LOG_LEVEL=INFO
LOG_TO_STDOUT=False
LOG_TO_FILE=True
LOG_FILE_PATH=/home/appuser/user_system/logs/app.log
```

#### 4. 数据库初始化

```bash
# 测试数据库连接
python scripts/test_mysql_connection.py

# 验证配置
python scripts/check_config.py

# 创建日志目录
mkdir -p logs
```

#### 5. 配置Supervisor（进程管理）

```bash
# 创建supervisor配置
sudo nano /etc/supervisor/conf.d/user_system.conf
```

**Supervisor配置文件**：
```ini
[program:user_system]
command=/home/appuser/user_system/venv/bin/python run.py
directory=/home/appuser/user_system
user=appuser
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/user_system_error.log
stdout_logfile=/var/log/user_system.log
environment=PATH="/home/appuser/user_system/venv/bin"
```

```bash
# 重载supervisor配置
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start user_system

# 检查状态
sudo supervisorctl status
```

#### 6. 配置Nginx（反向代理）

```bash
# 创建nginx配置
sudo nano /etc/nginx/sites-available/user_system
```

**Nginx配置文件**：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

    # API接口
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件和前端
    location / {
        root /home/appuser/user_system;
        try_files $uri $uri/ =404;
        index docs/api_index.html;
    }

    # 日志配置
    access_log /var/log/nginx/user_system_access.log;
    error_log /var/log/nginx/user_system_error.log;
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/user_system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 7. SSL证书配置（推荐）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 设置自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 8. 防火墙配置

```bash
# 配置UFW防火墙
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

#### 9. 系统服务设置

```bash
# 设置服务自启动
sudo systemctl enable nginx
sudo systemctl enable supervisor

# 启动服务
sudo systemctl start nginx
sudo systemctl start supervisor
```

### 部署验证

```bash
# 检查应用状态
sudo supervisorctl status user_system

# 检查日志
sudo tail -f /var/log/user_system.log
sudo tail -f /home/appuser/user_system/logs/app.log

# 测试API
curl -X POST http://your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"TestPass123"}'
```

### 维护操作

```bash
# 重启应用
sudo supervisorctl restart user_system

# 更新代码
cd /home/appuser/user_system
git pull
sudo supervisorctl restart user_system

# 查看系统状态
sudo supervisorctl status
sudo systemctl status nginx

# 备份数据库（如使用MySQL）
mysqldump -h your-host -u username -p database_name > backup_$(date +%Y%m%d).sql
```

### 监控和日志

```bash
# 应用日志
tail -f /home/appuser/user_system/logs/app.log

# Supervisor日志
tail -f /var/log/user_system.log
tail -f /var/log/user_system_error.log

# Nginx日志
tail -f /var/log/nginx/user_system_access.log
tail -f /var/log/nginx/user_system_error.log

# 系统资源监控
htop
df -h
free -h
```

### 故障排除

#### 常见问题

1. **应用无法启动**
   ```bash
   # 检查配置
   cd /home/appuser/user_system
   source venv/bin/activate
   python scripts/check_config.py
   ```

2. **数据库连接失败**
   ```bash
   # 测试数据库连接
   python scripts/test_mysql_connection.py
   ```

3. **权限问题**
   ```bash
   # 修复文件权限
   sudo chown -R appuser:www-data /home/appuser/user_system
   sudo chmod -R 755 /home/appuser/user_system
   ```

4. **端口被占用**
   ```bash
   # 检查端口占用
   sudo netstat -tlnp | grep :5000
   sudo lsof -i :5000
   ```

## 🔧 开发工具

### 📁 Scripts工具脚本
所有工具脚本已整理到 `scripts/` 目录下，详细说明请查看 [scripts/README.md](scripts/README.md)

### 配置检查

```bash
# 完整配置检查
python scripts/check_config.py

# 前端连接测试
python scripts/test_frontend.py

# 数据库连接测试
python scripts/test_mysql_connection.py
```

### 环境切换

```bash
# 查看当前环境
python scripts/switch_env.py --current

# 切换到生产环境
python scripts/switch_env.py production

# 切换到开发环境
python scripts/switch_env.py development

# 查看所有可用环境
python scripts/switch_env.py --list
```

### 日志分析

```bash
# 查看最新日志
python scripts/view_logs_simple.py

# 高级日志分析
python scripts/log_analyzer.py --help
```

## 技术栈

- **后端框架**: Flask 2.3.3
- **数据库ORM**: SQLAlchemy 3.0.5
- **认证**: JWT (Flask-JWT-Extended 4.5.3)
- **密码加密**: Bcrypt
- **数据库**: MySQL
- **跨域支持**: Flask-CORS
- **数据验证**: email-validator
- **日志系统**: Python logging + RotatingFileHandler
- **部署**: Nginx + Supervisor 