/**
 * JWT Token 辅助函数
 * 用于前端token的验证、存储和处理
 */

/**
 * 验证JWT token格式是否正确
 * @param {string} token - JWT token
 * @returns {boolean} - 是否为有效格式
 */
function isValidJWTFormat(token) {
    if (!token || typeof token !== 'string') {
        return false;
    }
    
    const parts = token.split('.');
    return parts.length === 3 && parts.every(part => part.length > 0);
}

/**
 * 解码JWT token的payload部分（不验证签名）
 * @param {string} token - JWT token
 * @returns {object|null} - 解码后的payload或null
 */
function decodeJWTPayload(token) {
    try {
        if (!isValidJWTFormat(token)) {
            return null;
        }
        
        const parts = token.split('.');
        const payload = parts[1];
        
        // 添加padding如果需要
        const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
        const decoded = atob(paddedPayload);
        
        return JSON.parse(decoded);
    } catch (error) {
        console.error('JWT解码失败:', error);
        return null;
    }
}

/**
 * 检查token是否过期
 * @param {string} token - JWT token
 * @returns {boolean} - 是否过期
 */
function isTokenExpired(token) {
    const payload = decodeJWTPayload(token);
    if (!payload || !payload.exp) {
        return true; // 无法解析或无过期时间，视为过期
    }
    
    const now = Math.floor(Date.now() / 1000);
    return payload.exp <= now;
}

/**
 * 获取token剩余有效时间（秒）
 * @param {string} token - JWT token
 * @returns {number} - 剩余秒数，如果已过期返回0
 */
function getTokenRemainingTime(token) {
    const payload = decodeJWTPayload(token);
    if (!payload || !payload.exp) {
        return 0;
    }
    
    const now = Math.floor(Date.now() / 1000);
    const remaining = payload.exp - now;
    return Math.max(0, remaining);
}

/**
 * 安全地存储token
 * @param {string} token - JWT token
 */
function storeToken(token) {
    if (!isValidJWTFormat(token)) {
        console.error('尝试存储无效格式的token');
        return false;
    }
    
    try {
        localStorage.setItem('access_token', token);
        return true;
    } catch (error) {
        console.error('Token存储失败:', error);
        return false;
    }
}

/**
 * 获取存储的token并验证
 * @returns {string|null} - 有效的token或null
 */
function getValidToken() {
    try {
        const token = localStorage.getItem('access_token');
        
        if (!token) {
            return null;
        }
        
        if (!isValidJWTFormat(token)) {
            console.warn('存储的token格式无效，将清除');
            clearToken();
            return null;
        }
        
        if (isTokenExpired(token)) {
            console.warn('存储的token已过期，将清除');
            clearToken();
            return null;
        }
        
        return token;
    } catch (error) {
        console.error('获取token失败:', error);
        clearToken();
        return null;
    }
}

/**
 * 清除存储的token
 */
function clearToken() {
    try {
        localStorage.removeItem('access_token');
    } catch (error) {
        console.error('清除token失败:', error);
    }
}

/**
 * 创建带Authorization头的fetch选项
 * @param {object} options - 原始fetch选项
 * @returns {object} - 包含Authorization头的选项
 */
function createAuthenticatedOptions(options = {}) {
    const token = getValidToken();
    
    if (!token) {
        throw new Error('No valid token available');
    }
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    return {
        ...options,
        headers
    };
}

/**
 * 验证API响应中的token错误
 * @param {Response} response - fetch响应对象
 * @param {object} data - 响应数据
 * @returns {boolean} - 是否为token相关错误
 */
function isTokenError(response, data) {
    if (response.status === 401 || response.status === 422) {
        const message = data.message || data.msg || '';
        const tokenErrorKeywords = [
            'token', 'Token', 'JWT', 'authorization', 'expired', 
            'invalid', 'unauthorized', 'header string'
        ];
        
        return tokenErrorKeywords.some(keyword => 
            message.toLowerCase().includes(keyword.toLowerCase())
        );
    }
    return false;
}

/**
 * 处理token错误的统一函数
 * @param {Response} response - fetch响应对象
 * @param {object} data - 响应数据
 */
function handleTokenError(response, data) {
    if (isTokenError(response, data)) {
        console.warn('检测到token错误，清除本地token:', data.message || data.msg);
        clearToken();
        
        // 可以在这里添加重定向到登录页面的逻辑
        // window.location.href = '/login';
    }
}

/**
 * 诊断token问题
 * @param {string} token - 要诊断的token（可选，默认使用存储的token）
 * @returns {object} - 诊断结果
 */
function diagnoseToken(token = null) {
    token = token || localStorage.getItem('access_token');
    
    const result = {
        hasToken: !!token,
        isValidFormat: false,
        isExpired: true,
        payload: null,
        remainingTime: 0,
        issues: []
    };
    
    if (!token) {
        result.issues.push('No token found in localStorage');
        return result;
    }
    
    // 检查格式
    result.isValidFormat = isValidJWTFormat(token);
    if (!result.isValidFormat) {
        result.issues.push('Invalid JWT format (should have 3 parts separated by dots)');
        return result;
    }
    
    // 解码payload
    result.payload = decodeJWTPayload(token);
    if (!result.payload) {
        result.issues.push('Failed to decode token payload');
        return result;
    }
    
    // 检查过期
    result.isExpired = isTokenExpired(token);
    result.remainingTime = getTokenRemainingTime(token);
    
    if (result.isExpired) {
        result.issues.push('Token has expired');
    } else {
        result.issues.push(`Token is valid for ${result.remainingTime} seconds`);
    }
    
    return result;
}

// 导出所有函数（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        isValidJWTFormat,
        decodeJWTPayload,
        isTokenExpired,
        getTokenRemainingTime,
        storeToken,
        getValidToken,
        clearToken,
        createAuthenticatedOptions,
        isTokenError,
        handleTokenError,
        diagnoseToken
    };
}

// 在控制台提供调试函数
if (typeof window !== 'undefined') {
    window.jwtHelper = {
        diagnose: diagnoseToken,
        clear: clearToken,
        check: () => {
            const result = diagnoseToken();
            console.table(result);
            return result;
        }
    };
    
    console.log('JWT Helper loaded. Use jwtHelper.check() to diagnose token issues.');
} 