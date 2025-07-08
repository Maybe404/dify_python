# Scripts 工具脚本目录

本目录包含项目相关的工具脚本和实用程序。

## 📋 脚本列表

### 配置和检查脚本
- **`check_config.py`** - 配置检查脚本，用于诊断环境变量和配置问题
- **`test_mysql_connection.py`** - MySQL数据库连接测试脚本
- **`test_frontend.py`** - 前端API连接测试脚本
- **`test_jwt_token.py`** - JWT token诊断脚本，用于排查token相关问题
- **`jwt_debug_consolidated.py`** - 🆕 整合的JWT调试和测试脚本（替换了多个重复脚本）
- **`test_password.py`** - 🆕 密码验证规则测试脚本

### 数据库相关脚本
- **`init_db.py`** - 数据库初始化脚本
- **`jwt_debug_consolidated.py`** - JWT调试和测试工具
- **`update_username_nullable.py`** - 更新用户名字段为可空的迁移脚本
- **`database_setup.sql`** - 数据库结构初始化SQL脚本

### 环境管理脚本
- **`switch_env.py`** - 环境切换脚本（开发/生产环境）
- **`secrets.py`** - 密钥生成工具

### 日志分析脚本
- **`log_analyzer.py`** - 完整的日志分析工具
- **`view_logs.py`** - 日志查看器（支持过滤）
- **`view_logs_simple.py`** - 简单日志查看器

## 🚀 使用方法

### 配置检查
```bash
# 完整配置检查
python scripts/check_config.py

# 数据库连接测试
python scripts/test_mysql_connection.py

# 前端API连接测试
python scripts/test_frontend.py

# JWT token诊断
python scripts/test_jwt_token.py

# 🆕 综合JWT调试（推荐使用）
python scripts/jwt_debug_consolidated.py

# 🆕 密码验证测试
python scripts/test_password.py
```

### 环境管理
```bash
# 查看当前环境
python scripts/switch_env.py --current

# 切换到生产环境
python scripts/switch_env.py production

# 切换到开发环境
python scripts/switch_env.py development
```

### 数据库管理
```bash
# 初始化数据库
python scripts/init_db.py

# 初始化MySQL数据库
python scripts/init_db.py

# 更新用户名字段为可空（新需求）
python scripts/update_username_nullable.py
```

### 日志分析
```bash
# 查看最新100条日志
python scripts/view_logs_simple.py

# 分析错误日志
python scripts/log_analyzer.py --level ERROR

# 搜索特定关键词
python scripts/log_analyzer.py --search "登录失败"
```

## 📁 文件结构

```
scripts/
├── README.md                   # 本说明文档
├── check_config.py            # 配置检查
├── test_mysql_connection.py   # 数据库连接测试
├── test_frontend.py           # 前端连接测试
├── test_jwt_token.py          # JWT token诊断
├── init_db.py                 # 数据库初始化
├── migrate_to_mysql.py        # 数据迁移
├── update_username_nullable.py # 用户名字段可空迁移
├── database_setup.sql         # 数据库SQL脚本
├── switch_env.py              # 环境切换
├── secrets.py                 # 密钥生成
├── log_analyzer.py            # 日志分析器
├── view_logs.py               # 日志查看器
└── view_logs_simple.py        # 简单日志查看器
```

## 💡 使用建议

1. **部署前检查**：运行 `check_config.py` 确保配置正确
2. **连接测试**：使用 `test_mysql_connection.py` 和 `test_frontend.py` 验证服务
3. **环境管理**：使用 `switch_env.py` 在不同环境间切换
4. **日志监控**：定期使用日志分析工具查看系统状态

## 🔧 开发者注意事项

- 所有脚本都应该从项目根目录运行
- 脚本会自动添加父目录到Python路径以便导入项目模块
- 建议在虚拟环境中运行这些脚本 