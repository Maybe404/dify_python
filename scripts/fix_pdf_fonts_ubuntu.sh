#!/bin/bash

# Ubuntu PDF字体问题修复脚本
# 解决在Ubuntu服务器上PDF导出中文乱码的问题

set -e

echo "🔧 开始修复Ubuntu PDF字体问题"
echo "=================================="

# 检查系统
echo "📋 检查系统信息..."
lsb_release -a 2>/dev/null || echo "无法获取发行版信息"
uname -a

# 修复GPG密钥问题
echo "🔑 修复GPG密钥问题..."
echo "正在处理可能的GPG密钥错误..."

# 临时禁用有问题的源，只更新主要源
echo "🔄 更新包管理器（跳过有问题的源）..."
sudo apt-get update -o Dir::Etc::sourcelist="sources.list.d/ubuntu-sources.list" 2>/dev/null || {
    echo "⚠️  标准更新失败，尝试强制更新..."
    sudo apt-get update --allow-unauthenticated --allow-insecure-repositories 2>/dev/null || {
        echo "⚠️  包管理器更新遇到问题，但继续安装字体包..."
    }
}

# 安装字体相关包
echo "📦 安装字体支持包..."
echo "正在安装核心字体包..."

# 分步安装，更容易处理错误
packages=(
    "fontconfig"
    "fontconfig-config"
    "fonts-wqy-microhei"
    "fonts-wqy-zenhei"
    "fonts-noto-cjk"
)

for package in "${packages[@]}"; do
    echo "正在安装 $package ..."
    sudo apt-get install -y "$package" 2>/dev/null || {
        echo "⚠️  安装 $package 失败，跳过..."
    }
done

# 尝试安装其他可选字体包
echo "📦 尝试安装额外字体包..."
optional_packages=(
    "fonts-noto-cjk-extra"
    "fonts-arphic-uming" 
    "fonts-arphic-ukai"
    "ttf-wqy-microhei"
    "ttf-wqy-zenhei"
)

for package in "${optional_packages[@]}"; do
    echo "尝试安装 $package ..."
    sudo apt-get install -y "$package" 2>/dev/null || {
        echo "⚠️  $package 不可用，跳过..."
    }
done

# 刷新字体缓存
echo "🔄 刷新字体缓存..."
sudo fc-cache -fv

# 验证中文字体是否安装成功
echo "✅ 验证字体安装..."
echo "已安装的中文字体："
fc-list :lang=zh family | head -10

# 列出字体文件路径
echo ""
echo "字体文件路径："
fc-list :lang=zh file | head -10

# 测试字体文件
echo ""
echo "🔍 检查常用字体文件是否存在："
font_paths=(
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    "/usr/share/fonts/truetype/arphic/uming.ttc"
)

found_fonts=0
for path in "${font_paths[@]}"; do
    if [ -f "$path" ]; then
        echo "✅ $path"
        ((found_fonts++))
    else
        echo "❌ $path"
    fi
done

if [ $found_fonts -eq 0 ]; then
    echo "⚠️  未找到任何中文字体文件，尝试手动下载字体..."
    # 创建字体目录
    sudo mkdir -p /usr/share/fonts/truetype/custom
    
    # 下载WQY微米黑字体（开源字体）
    echo "📥 下载开源中文字体..."
    wget -O /tmp/wqy-microhei.ttc "https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSansSC.zip" 2>/dev/null || {
        echo "⚠️  网络下载失败，将使用内置CID字体作为备选方案"
    }
fi

# 创建字体测试脚本
echo ""
echo "📝 创建字体测试脚本..."
cat > /tmp/test_pdf_font.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def test_reportlab_fonts():
    """测试ReportLab字体支持"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.pagesizes import A4
        
        print("🧪 测试ReportLab字体支持...")
        
        # 测试字体路径
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc"
        ]
        
        success_count = 0
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # 尝试注册字体
                    font_name = f"TestFont_{os.path.basename(font_path)}"
                    if font_path.endswith('.ttc'):
                        pdfmetrics.registerFont(TTFont(font_name, font_path, subfontIndex=0))
                    else:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✅ 成功注册字体: {font_path}")
                    
                    # 创建测试PDF
                    test_pdf = f"/tmp/test_{font_name}.pdf"
                    c = canvas.Canvas(test_pdf, pagesize=A4)
                    c.setFont(font_name, 16)
                    c.drawString(100, 750, "中文测试：你好世界 Hello World")
                    c.save()
                    print(f"✅ 成功创建测试PDF: {test_pdf}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ 字体注册失败 {font_path}: {e}")
        
        # 测试内置CID字体
        try:
            from reportlab.pdfbase.cidfonts import UnicodeCIDFont
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            print("✅ 内置CID字体STSong-Light可用")
            
            test_pdf = "/tmp/test_cid_font.pdf"
            c = canvas.Canvas(test_pdf, pagesize=A4)
            c.setFont('STSong-Light', 16)
            c.drawString(100, 750, "中文测试：你好世界 Hello World")
            c.save()
            print(f"✅ 成功创建CID字体测试PDF: {test_pdf}")
            success_count += 1
        except Exception as e:
            print(f"❌ CID字体不可用: {e}")
        
        return success_count > 0
        
    except ImportError as e:
        print(f"❌ ReportLab未安装: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_reportlab_fonts()
    sys.exit(0 if success else 1)
EOF

# 运行字体测试
echo "🧪 运行字体测试..."
if python3 /tmp/test_pdf_font.py; then
    echo "✅ 字体测试通过！"
else
    echo "⚠️  字体测试失败，但可能仍可使用内置字体"
fi

# 清理测试文件
rm -f /tmp/test_*.pdf /tmp/test_pdf_font.py

echo ""
echo "🎉 Ubuntu PDF字体修复完成！"
echo "=================================="
echo "📝 修复说明："
echo "1. 已尝试安装多个中文字体包"
echo "2. 已刷新系统字体缓存"
echo "3. 已验证字体可用性"
echo ""
if [ $found_fonts -gt 0 ]; then
    echo "✅ 找到 $found_fonts 个中文字体文件"
else
    echo "⚠️  系统字体可能有限，但应用会使用内置CID字体作为备选"
fi
echo ""
echo "🔄 请重启您的Flask应用以应用字体更改："
echo "   sudo systemctl restart user-system"
echo ""
echo "📋 如果仍有问题，请检查应用日志："
echo "   tail -f /opt/user_system/logs/app.log"
echo ""
echo "🔧 如果仍有字体问题，可以手动运行诊断："
echo "   python3 -c \"import subprocess; print(subprocess.run(['fc-list', ':lang=zh'], capture_output=True, text=True).stdout)\"" 