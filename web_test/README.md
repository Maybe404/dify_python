# 前端API测试页面

这是一个简单的前端测试页面，用于测试用户管理系统的所有API接口。

## 功能特性

### 🔗 连接状态监控
- 实时显示与后端API的连接状态
- 自动定期检测连接（每30秒）
- 页面重新激活时自动检测

### 👤 用户状态管理
- 显示当前登录状态
- 自动保存和恢复登录token
- 显示当前用户详细信息

### 📝 API接口测试
1. **用户注册** - 测试用户注册功能
2. **用户登录** - 测试用户登录功能
3. **获取用户信息** - 测试获取用户资料
4. **Token验证** - 测试JWT token有效性
5. **用户登出** - 测试用户登出功能

### ⚡ 快速测试功能
- **一键测试** - 自动执行完整的测试流程
- **生成测试数据** - 自动生成测试用户信息
- **清空结果** - 清空所有测试结果显示

### 📋 操作日志
- 记录所有API调用和响应
- 显示详细的时间戳
- 支持清空日志功能

## 使用方法

### 1. 启动后端服务
确保您的Flask应用正在运行：
```bash
python run.py
```

### 2. 打开测试页面
在浏览器中打开 `web_test/index.html` 文件。

### 3. 配置API地址
如果您的后端服务不是运行在 `http://localhost:5000`，请修改 `script.js` 文件中的 `API_BASE_URL` 变量：

```javascript
const API_BASE_URL = 'http://your-server:port/api';
```

### 4. 开始测试

#### 手动测试
1. 点击"测试连接"确认后端服务正常
2. 点击"生成测试用户数据"自动填充表单
3. 依次测试注册、登录、获取用户信息等功能

#### 自动测试
点击"一键测试所有功能"按钮，系统将自动：
1. 测试服务器连接
2. 生成测试用户数据
3. 注册新用户
4. 登录用户
5. 获取用户信息
6. 验证Token
7. 登出用户

## 文件说明

- `index.html` - 主页面文件，包含所有UI元素
- `style.css` - 样式文件，提供美观的界面设计
- `script.js` - JavaScript逻辑文件，处理所有API调用
- `README.md` - 本说明文档
- `debug.html` - 前端调试工具，用于诊断API连接问题

## 界面说明

### 状态区域
- **连接状态**：显示与后端API的连接状态
- **登录状态**：显示当前用户的登录状态和基本信息

### API测试区域
每个API接口都有独立的测试卡片，包含：
- 输入表单（如果需要）
- 测试按钮
- 结果显示区域

### 快速测试区域
提供便捷的测试工具：
- 一键测试所有功能
- 生成测试用户数据
- 清空所有结果

### 日志区域
显示所有操作的详细日志，包括：
- API请求和响应
- 成功/失败状态
- 错误信息

## 响应格式

所有API响应都会以JSON格式显示，包含：
- 成功响应：绿色背景显示
- 错误响应：红色背景显示
- 信息响应：蓝色背景显示

## 注意事项

1. **CORS设置**：确保后端已正确配置CORS，允许前端页面访问API
2. **浏览器兼容性**：建议使用现代浏览器（Chrome、Firefox、Safari、Edge）
3. **本地存储**：页面使用localStorage保存登录token，关闭浏览器后仍会保持登录状态
4. **网络连接**：确保前端页面能够访问后端API地址

## 故障排除

### 连接失败
- 检查后端服务是否正在运行
- 确认API地址配置正确
- 检查防火墙和网络设置

### CORS错误
- 确保后端已安装并配置Flask-CORS
- 检查CORS配置是否允许前端域名

### Token过期
- 页面会自动处理token过期情况
- 如果遇到问题，可以手动清空浏览器localStorage

## 自定义配置

### 修改API地址
编辑 `script.js` 文件的第2行：
```javascript
const API_BASE_URL = 'http://your-api-server.com/api';
```

### 修改样式
编辑 `style.css` 文件来自定义页面外观。

### 添加新的API测试
在 `index.html` 中添加新的API卡片，并在 `script.js` 中添加相应的处理函数。

## 技术栈

- **HTML5** - 页面结构
- **CSS3** - 样式和动画
- **JavaScript (ES6+)** - 逻辑处理
- **Fetch API** - HTTP请求
- **LocalStorage** - 本地数据存储

这个测试页面提供了完整的用户管理系统API测试功能，帮助您快速验证后端接口的正确性。

## 🚨 前端连接问题排查指南

如果遇到前端无法调用后端API的问题，请按以下步骤排查：

### 1. 确认后端服务状态

```bash
# 确保后端服务已启动
python run.py

# 检查服务是否运行在正确端口
netstat -an | findstr :5000  # Windows
lsof -i :5000               # Linux/Mac
```

### 2. 检查配置文件

```bash
# 运行配置检查脚本
python check_config.py

# 确认 .env 文件存在并配置正确
# （之前可能只更新了 env_example.txt 而没有创建 .env 文件）
```

### 3. 验证API连接

```bash
# 运行前端连接测试
python test_frontend.py
```

### 4. 浏览器测试

1. **使用调试工具**：
   - 打开 `web_test/debug.html`
   - 点击"运行完整诊断"
   - 查看详细的连接测试结果

2. **检查浏览器开发者工具**：
   - 按F12打开开发者工具
   - 查看Console标签是否有错误信息
   - 查看Network标签检查请求状态

### 5. 常见问题及解决方案

#### 问题1: CORS错误
```
Access to fetch at 'http://localhost:5000/api/...' from origin 'file://' has been blocked by CORS policy
```
**解决方案**：
- 确保Flask-CORS已正确配置（已在代码中配置）
- 尝试使用HTTP服务器而非直接打开HTML文件

#### 问题2: 连接被拒绝
```
TypeError: Failed to fetch
```
**解决方案**：
- 确认后端服务已启动
- 检查防火墙设置
- 尝试使用 `localhost` 替代 `127.0.0.1`

#### 问题3: 422错误 (Unprocessable Entity)
```
POST /api/auth/verify-token HTTP/1.1" 422
```
**解决方案**：
- 这通常是JWT token验证失败，属于正常行为
- 如果持续出现，检查JWT配置

#### 问题4: 404错误 (Not Found)
```
GET /api/auth/register HTTP/1.1" 404
```
**解决方案**：
- 检查API路由配置
- 确认蓝图注册正确
- 验证URL路径拼写

### 6. API URL配置

前端默认使用以下API地址：
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

如果需要修改，可以：
1. 直接编辑 `web_test/script.js` 文件
2. 使用 `debug.html` 的URL配置功能

### 7. 快速验证步骤

1. **确认.env文件存在**：
   ```bash
   # 如果不存在，从示例文件复制
   copy env_example.txt .env  # Windows
   cp env_example.txt .env    # Linux/Mac
   ```

2. **启动后端服务**：
   ```bash
   python run.py
   ```

3. **运行连接测试**：
   ```bash
   python test_frontend.py
   ```

4. **测试前端界面**：
   - 直接双击打开 `web_test/index.html`
   - 或者使用本地HTTP服务器

### 8. 性能优化建议

- 使用现代浏览器（Chrome, Firefox, Edge）
- 确保JavaScript已启用
- 清除浏览器缓存和localStorage
- 检查网络连接稳定性

### 9. 开发者工具使用

1. **Network标签**：
   - 查看HTTP请求状态
   - 检查请求头和响应体
   - 确认CORS头信息

2. **Console标签**：
   - 查看JavaScript错误
   - 检查API调用日志
   - 验证数据格式

3. **Application标签**：
   - 检查localStorage中的token
   - 清除存储的认证信息

## 使用方法

1. 确保后端服务已启动
2. 打开 `index.html` 文件
3. 使用各个功能模块测试API

## 功能特性

### 用户认证
- 用户注册
- 用户登录
- 用户登出
- 获取用户信息
- Token验证

### 密码管理
- 忘记密码（邮件重置）
- 重置密码
- 修改密码

### 系统功能
- 连接状态检测
- 实时日志记录
- 错误信息显示
- 自动Token管理

## 技术特点

- 现代JavaScript ES6+语法
- 响应式界面设计
- 实时状态更新
- 详细错误处理
- 本地存储管理

## 调试功能

`debug.html` 提供了专门的调试工具：

- 基础连接测试
- CORS配置检查
- API端点验证
- 网络诊断工具
- 修复建议生成

## 注意事项

1. 确保后端服务在访问前端页面之前已启动
2. 某些浏览器可能需要HTTP服务器环境而非file://协议
3. 检查浏览器控制台获取详细错误信息
4. 确保所有依赖的Python包已安装

## 故障排除

如果遇到问题：

1. 运行 `python check_config.py` 检查配置
2. 运行 `python test_frontend.py` 测试连接
3. 使用 `debug.html` 进行详细诊断
4. 查看浏览器开发者工具
5. 检查后端服务日志输出 