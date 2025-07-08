// API基础配置
const API_BASE_URL = 'http://localhost:5000/api';
let currentToken = localStorage.getItem('access_token');

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
    setupEventListeners();
    checkLoginStatus();
});

// 初始化页面
function initializePage() {
    addLog('页面加载完成', 'info');
    updateConnectionStatus('检测中...', 'connecting');
    updateLoginStatus();
    
    // 自动测试连接
    testConnection();
}

// 设置事件监听器
function setupEventListeners() {
    // 注册表单
    document.getElementById('register-form').addEventListener('submit', function(e) {
        e.preventDefault();
        registerUser();
    });

    // 登录表单
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        loginUser();
    });

    // 忘记密码表单
    document.getElementById('forgot-password-form').addEventListener('submit', function(e) {
        e.preventDefault();
        forgotPassword();
    });

    // 重置密码表单
    document.getElementById('reset-password-form').addEventListener('submit', function(e) {
        e.preventDefault();
        resetPassword();
    });

    // 修改密码表单
    document.getElementById('change-password-form').addEventListener('submit', function(e) {
        e.preventDefault();
        changePassword();
    });
}

// 日志功能
function addLog(message, type = 'info') {
    const logArea = document.getElementById('log-area');
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;
    logArea.appendChild(logEntry);
    logArea.scrollTop = logArea.scrollHeight;
}

function clearLogs() {
    document.getElementById('log-area').innerHTML = '';
    addLog('日志已清空', 'info');
}

// 状态更新功能
function updateConnectionStatus(status, className) {
    const statusElement = document.getElementById('connection-status');
    statusElement.textContent = status;
    statusElement.className = `status-indicator ${className}`;
}

function updateLoginStatus() {
    const statusElement = document.getElementById('login-status');
    const userInfoElement = document.getElementById('user-info');
    
    if (currentToken) {
        statusElement.textContent = '已登录';
        statusElement.className = 'status-indicator logged-in';
        
        // 尝试获取用户信息来验证token有效性
        getUserProfile(false);
    } else {
        statusElement.textContent = '未登录';
        statusElement.className = 'status-indicator logged-out';
        // 立即隐藏用户信息并清除内容
        userInfoElement.style.display = 'none';
        userInfoElement.innerHTML = '';
    }
}

// 显示结果
function showResult(elementId, data, isSuccess = true) {
    const resultElement = document.getElementById(elementId);
    resultElement.className = `result-area ${isSuccess ? 'success' : 'error'}`;
    resultElement.textContent = JSON.stringify(data, null, 2);
    resultElement.style.display = 'block';
}

// API调用通用函数
async function apiCall(endpoint, method = 'GET', data = null, requireAuth = false) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
    };

    if (requireAuth && currentToken) {
        headers['Authorization'] = `Bearer ${currentToken}`;
    }

    const config = {
        method: method,
        headers: headers,
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    try {
        addLog(`发送请求: ${method} ${endpoint}`, 'info');
        const response = await fetch(url, config);
        const result = await response.json();
        
        if (response.ok) {
            addLog(`请求成功: ${response.status}`, 'success');
            return { success: true, data: result, status: response.status };
        } else {
            addLog(`请求失败: ${response.status} - ${result.message}`, 'error');
            return { success: false, data: result, status: response.status };
        }
    } catch (error) {
        addLog(`网络错误: ${error.message}`, 'error');
        return { success: false, error: error.message };
    }
}

// 测试连接
async function testConnection() {
    addLog('测试服务器连接...', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateConnectionStatus('已连接', 'connected');
            addLog(`服务器连接正常 - ${data.message}`, 'success');
        } else {
            updateConnectionStatus('连接异常', 'disconnected');
            addLog(`服务器响应异常: ${response.status}`, 'warning');
        }
    } catch (error) {
        updateConnectionStatus('连接失败', 'disconnected');
        addLog(`连接失败: ${error.message}`, 'error');
    }
}

// 用户注册
async function registerUser() {
    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    // 邮箱和密码是必填的
    if (!email || !password) {
        showResult('register-result', { error: '请填写邮箱和密码' }, false);
        return;
    }

    // 构建用户数据，如果用户名为空则不发送
    const userData = { email, password };
    if (username) {
        userData.username = username;
    }
    
    const result = await apiCall('/auth/register', 'POST', userData);
    
    showResult('register-result', result.data, result.success);
    
    if (result.success) {
        const displayName = username || email;
        addLog(`用户注册成功: ${displayName}`, 'success');
        // 清空表单
        document.getElementById('register-form').reset();
    } else {
        addLog(`用户注册失败: ${result.data.message}`, 'error');
    }
}

// 用户登录
async function loginUser() {
    const credential = document.getElementById('login-credential').value;
    const password = document.getElementById('login-password').value;

    if (!credential || !password) {
        showResult('login-result', { error: '请填写用户名/邮箱和密码' }, false);
        return;
    }

    const loginData = { credential, password };
    const result = await apiCall('/auth/login', 'POST', loginData);
    
    showResult('login-result', result.data, result.success);
    
    if (result.success) {
        currentToken = result.data.data.access_token;
        localStorage.setItem('access_token', currentToken);
        addLog(`用户登录成功: ${credential}`, 'success');
        updateLoginStatus();
        
        // 清空表单
        document.getElementById('login-form').reset();
    } else {
        addLog(`用户登录失败: ${result.data.message}`, 'error');
    }
}

// 获取用户信息
async function getUserProfile(showInResult = true) {
    if (!currentToken) {
        if (showInResult) {
            showResult('profile-result', { error: '请先登录' }, false);
        }
        return;
    }

    const result = await apiCall('/auth/profile', 'GET', null, true);
    
    if (showInResult) {
        showResult('profile-result', result.data, result.success);
    }
    
    if (result.success) {
        addLog('获取用户信息成功', 'success');
        
        // 更新用户信息显示
        const userInfoElement = document.getElementById('user-info');
        const user = result.data.data.user;
        userInfoElement.innerHTML = `
            <strong>用户ID:</strong> ${user.id}<br>
            <strong>用户名:</strong> ${user.username}<br>
            <strong>邮箱:</strong> ${user.email}<br>
            <strong>状态:</strong> ${user.is_active ? '激活' : '禁用'}<br>
            <strong>注册时间:</strong> ${new Date(user.created_at).toLocaleString()}
        `;
        userInfoElement.style.display = 'block';
    } else {
        if (!showInResult) {
            // 如果是静默检查用户信息失败，不记录错误日志
            addLog(`Token验证失败，已清除登录状态: ${result.data.message}`, 'warning');
        } else {
            addLog(`获取用户信息失败: ${result.data.message}`, 'error');
        }
        
        if (result.status === 401) {
            // Token可能已过期或被撤销
            currentToken = null;
            localStorage.removeItem('access_token');
            // 立即清除用户信息显示
            const userInfoElement = document.getElementById('user-info');
            userInfoElement.style.display = 'none';
            userInfoElement.innerHTML = '';
            updateLoginStatus();
        }
    }
}

// 验证Token
async function verifyToken() {
    if (!currentToken) {
        showResult('verify-result', { error: '没有可验证的token' }, false);
        return;
    }

    const result = await apiCall('/auth/verify-token', 'POST', null, true);
    
    showResult('verify-result', result.data, result.success);
    
    if (result.success) {
        addLog('Token验证成功', 'success');
    } else {
        addLog(`Token验证失败: ${result.data.message}`, 'error');
        if (result.status === 401) {
            currentToken = null;
            localStorage.removeItem('access_token');
            // 立即清除用户信息显示
            const userInfoElement = document.getElementById('user-info');
            userInfoElement.style.display = 'none';
            userInfoElement.innerHTML = '';
            updateLoginStatus();
        }
    }
}

// 用户登出
async function logout() {
    if (!currentToken) {
        showResult('logout-result', { error: '当前未登录' }, false);
        return;
    }

    const result = await apiCall('/auth/logout', 'POST', null, true);
    
    showResult('logout-result', result.data, result.success);
    
    if (result.success) {
        addLog('用户登出成功', 'success');
    } else {
        addLog(`用户登出失败: ${result.data.message}`, 'warning');
    }
    
    // 无论成功失败都清除本地token
    currentToken = null;
    localStorage.removeItem('access_token');
    updateLoginStatus();
}

// 忘记密码
async function forgotPassword() {
    const email = document.getElementById('forgot-email').value;

    if (!email) {
        showResult('forgot-password-result', { error: '请输入邮箱地址' }, false);
        return;
    }

    const forgotData = { email };
    const result = await apiCall('/auth/forgot-password', 'POST', forgotData);
    
    showResult('forgot-password-result', result.data, result.success);
    
    if (result.success) {
        addLog(`密码重置令牌已生成: ${email}`, 'success');
        
        // 如果返回了重置令牌，自动填入重置密码表单
        if (result.data.data && result.data.data.reset_token) {
            document.getElementById('reset-token').value = result.data.data.reset_token;
            addLog('重置令牌已自动填入重置密码表单', 'info');
        }
        
        // 清空表单
        document.getElementById('forgot-password-form').reset();
    } else {
        addLog(`生成重置令牌失败: ${result.data.message}`, 'error');
    }
}

// 重置密码
async function resetPassword() {
    const resetToken = document.getElementById('reset-token').value;
    const newPassword = document.getElementById('new-password').value;

    if (!resetToken || !newPassword) {
        showResult('reset-password-result', { error: '请填写重置令牌和新密码' }, false);
        return;
    }

    const resetData = { 
        reset_token: resetToken, 
        new_password: newPassword 
    };
    const result = await apiCall('/auth/reset-password', 'POST', resetData);
    
    showResult('reset-password-result', result.data, result.success);
    
    if (result.success) {
        addLog('密码重置成功', 'success');
        
        // 清空表单
        document.getElementById('reset-password-form').reset();
        
        // 提示用户可以使用新密码登录
        addLog('请使用新密码重新登录', 'info');
    } else {
        addLog(`密码重置失败: ${result.data.message}`, 'error');
    }
}

// 修改密码（需要登录）
async function changePassword() {
    if (!currentToken) {
        showResult('change-password-result', { error: '请先登录' }, false);
        return;
    }

    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('change-new-password').value;

    if (!currentPassword || !newPassword) {
        showResult('change-password-result', { error: '请填写当前密码和新密码' }, false);
        return;
    }

    const changeData = { 
        current_password: currentPassword, 
        new_password: newPassword 
    };
    const result = await apiCall('/auth/change-password', 'POST', changeData, true);
    
    showResult('change-password-result', result.data, result.success);
    
    if (result.success) {
        addLog('密码修改成功', 'success');
        
        // 清空表单
        document.getElementById('change-password-form').reset();
        
        // 提示用户需要重新登录
        addLog('密码已修改，建议重新登录', 'info');
    } else {
        addLog(`密码修改失败: ${result.data.message}`, 'error');
        
        if (result.status === 401) {
            // Token可能已过期
            currentToken = null;
            localStorage.removeItem('access_token');
            updateLoginStatus();
        }
    }
}

// 生成测试用户数据
function generateTestUser() {
    const timestamp = Date.now();
    const testUser = {
        username: `testuser${timestamp}`,
        email: `test${timestamp}@example.com`,
        password: 'TestPass123'
    };

    document.getElementById('reg-username').value = testUser.username;
    document.getElementById('reg-email').value = testUser.email;
    document.getElementById('reg-password').value = testUser.password;

    document.getElementById('login-credential').value = testUser.username;
    document.getElementById('login-password').value = testUser.password;

    addLog(`生成测试用户数据: ${testUser.username}`, 'info');
}

// 清空所有结果
function clearAllResults() {
    const resultAreas = document.querySelectorAll('.result-area');
    resultAreas.forEach(area => {
        area.style.display = 'none';
        area.textContent = '';
    });
    addLog('清空所有结果显示', 'info');
}

// 检查登录状态
function checkLoginStatus() {
    if (currentToken) {
        addLog('发现本地存储的token，验证中...', 'info');
        verifyToken();
    }
}

// 一键测试所有功能
async function quickTest() {
    addLog('开始一键测试所有功能...', 'info');
    
    // 1. 测试连接
    await testConnection();
    await sleep(1000);
    
    // 2. 生成测试用户
    generateTestUser();
    await sleep(500);
    
    // 3. 注册用户
    addLog('自动注册测试用户...', 'info');
    await registerUser();
    await sleep(1000);
    
    // 4. 测试忘记密码功能
    addLog('自动测试忘记密码功能...', 'info');
    const testEmail = document.getElementById('reg-email').value;
    if (testEmail) {
        document.getElementById('forgot-email').value = testEmail;
        await forgotPassword();
        await sleep(1000);
        
        // 5. 测试重置密码功能
        addLog('自动测试重置密码功能...', 'info');
        document.getElementById('new-password').value = 'NewTestPass123';
        await resetPassword();
        await sleep(1000);
        
        // 6. 使用新密码登录
        addLog('使用新密码登录...', 'info');
        document.getElementById('login-password').value = 'NewTestPass123';
        await loginUser();
        await sleep(1000);
    } else {
        // 4. 登录用户（如果没有邮箱信息）
        addLog('自动登录测试用户...', 'info');
        await loginUser();
        await sleep(1000);
    }
    
    // 7. 获取用户信息
    if (currentToken) {
        addLog('自动获取用户信息...', 'info');
        await getUserProfile();
        await sleep(1000);
        
        // 8. 验证Token
        addLog('自动验证Token...', 'info');
        await verifyToken();
        await sleep(1000);
        
        // 9. 测试修改密码功能
        addLog('自动测试修改密码功能...', 'info');
        document.getElementById('current-password').value = 'NewTestPass123';
        document.getElementById('change-new-password').value = 'FinalTestPass123';
        await changePassword();
        await sleep(1000);
        
        // 10. 登出
        addLog('自动登出用户...', 'info');
        await logout();
    }
    
    addLog('一键测试完成！包含密码重置功能测试', 'success');
}

// 辅助函数：延迟
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 页面可见性变化时检查连接状态
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        testConnection();
    }
});

// 定期检查连接状态（每30秒）
setInterval(testConnection, 30000); 