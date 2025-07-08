#!/bin/bash

# 直接安装中文字体脚本
# 不依赖包管理器，直接下载字体文件

set -e

echo "📥 直接下载安装中文字体"
echo "=================================="

# 创建字体目录
FONT_DIR="/usr/share/fonts/truetype/chinese"
echo "📁 创建字体目录: $FONT_DIR"
sudo mkdir -p "$FONT_DIR"

# 下载开源中文字体
echo "📥 下载WQY微米黑字体..."
cd /tmp

# 下载WQY微米黑字体（开源免费）
echo "正在尝试多个下载源..."

# 尝试多个下载源（包括国内镜像）
download_success=false

# 方法1: 使用清华大学镜像
echo "📥 尝试清华大学镜像..."
timeout 60 wget --timeout=30 --tries=2 -O wqy-microhei.ttc "https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ubuntu/pool/universe/f/fonts-wqy-microhei/fonts-wqy-microhei_0.2.0-beta-2_all.deb" 2>/dev/null && {
    echo "✅ 从清华镜像下载成功"
    # 解压deb包
    timeout 15 ar x fonts-wqy-microhei_0.2.0-beta-2_all.deb 2>/dev/null || true
    timeout 15 tar -xf data.tar.* 2>/dev/null || true
    if [ -f "usr/share/fonts/truetype/wqy/wqy-microhei.ttc" ]; then
        mv "usr/share/fonts/truetype/wqy/wqy-microhei.ttc" ./wqy-microhei.ttc
        download_success=true
    fi
} || {
    echo "⚠️  清华镜像下载失败"
}

# 方法2: 使用阿里云镜像
if [ "$download_success" = false ]; then
    echo "📥 尝试阿里云镜像..."
    timeout 60 wget --timeout=30 --tries=2 -O wqy-microhei.ttc "https://mirrors.aliyun.com/ubuntu/pool/universe/f/fonts-wqy-microhei/fonts-wqy-microhei_0.2.0-beta-2_all.deb" 2>/dev/null && {
        echo "✅ 从阿里云镜像下载成功"
        # 解压deb包
        timeout 15 ar x fonts-wqy-microhei_0.2.0-beta-2_all.deb 2>/dev/null || true
        timeout 15 tar -xf data.tar.* 2>/dev/null || true
        if [ -f "usr/share/fonts/truetype/wqy/wqy-microhei.ttc" ]; then
            mv "usr/share/fonts/truetype/wqy/wqy-microhei.ttc" ./wqy-microhei.ttc
            download_success=true
        fi
    } || {
        echo "⚠️  阿里云镜像下载失败"
    }
fi

# 方法3: 使用中科大镜像
if [ "$download_success" = false ]; then
    echo "📥 尝试中科大镜像..."
    timeout 60 wget --timeout=30 --tries=2 -O wqy-microhei.ttc "https://mirrors.ustc.edu.cn/ubuntu/pool/universe/f/fonts-wqy-microhei/fonts-wqy-microhei_0.2.0-beta-2_all.deb" 2>/dev/null && {
        echo "✅ 从中科大镜像下载成功"
        # 解压deb包
        timeout 15 ar x fonts-wqy-microhei_0.2.0-beta-2_all.deb 2>/dev/null || true
        timeout 15 tar -xf data.tar.* 2>/dev/null || true
        if [ -f "usr/share/fonts/truetype/wqy/wqy-microhei.ttc" ]; then
            mv "usr/share/fonts/truetype/wqy/wqy-microhei.ttc" ./wqy-microhei.ttc
            download_success=true
        fi
    } || {
        echo "⚠️  中科大镜像下载失败"
    }
fi

# 方法4: 使用GitHub代理
if [ "$download_success" = false ]; then
    echo "📥 尝试GitHub代理..."
    # 使用ghproxy.com代理
    timeout 60 wget --timeout=30 --tries=2 -O wqy-microhei.ttc "https://ghproxy.com/https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc" 2>/dev/null && {
        echo "✅ 从GitHub代理下载成功"
        download_success=true
    } || {
        # 尝试另一个GitHub代理
        timeout 60 wget --timeout=30 --tries=2 -O wqy-microhei.ttc "https://mirror.ghproxy.com/https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc" 2>/dev/null && {
            echo "✅ 从GitHub代理2下载成功"
            download_success=true
        } || {
            echo "⚠️  GitHub代理下载失败"
        }
    }
fi

# 方法5: 原始sourceforge
if [ "$download_success" = false ]; then
    echo "📥 尝试SourceForge..."
    timeout 120 wget --timeout=60 --tries=2 -O wqy-microhei.tar.gz "https://downloads.sourceforge.net/project/wqy/wqy-microhei/0.2.0-beta/wqy-microhei-0.2.0-beta.tar.gz" 2>/dev/null && {
        echo "✅ 从SourceForge下载成功"
        timeout 30 tar -xzf wqy-microhei.tar.gz 2>/dev/null && {
            timeout 10 find . -name "wqy-microhei.ttc" -exec mv {} ./wqy-microhei.ttc \; 2>/dev/null
            download_success=true
        }
    } || {
        echo "⚠️  SourceForge下载失败"
    }
fi

# 如果下载成功，安装字体
if [ "$download_success" = true ] && [ -f "wqy-microhei.ttc" ]; then
    echo "📋 安装WQY微米黑字体..."
    sudo cp wqy-microhei.ttc "$FONT_DIR/"
    echo "✅ WQY微米黑字体安装成功"
else
    echo "⚠️  WQY微米黑字体下载失败，跳过安装"
fi

# 下载Noto Sans CJK字体（Google开源字体）
echo "📥 下载Noto Sans CJK字体..."

noto_success=false

# 只使用清华镜像下载Noto字体
echo "📥 尝试清华镜像下载Noto字体..."
timeout 120 wget --timeout=60 --tries=2 -O NotoSansCJK.ttc.zip "https://mirrors.tuna.tsinghua.edu.cn/github-release/notofonts/noto-cjk/LatestRelease/NotoSansCJK.ttc.zip" 2>/dev/null && {
    timeout 30 unzip -q NotoSansCJK.ttc.zip 2>/dev/null && {
        if [ -f "NotoSansCJK.ttc" ]; then
            echo "✅ Noto字体从清华镜像下载成功"
            noto_success=true
        fi
    }
} || {
    echo "⚠️  清华镜像Noto字体下载失败"
}

# 安装Noto字体
if [ "$noto_success" = true ]; then
    echo "📋 安装Noto字体..."
    sudo cp NotoSansCJK.* "$FONT_DIR/" 2>/dev/null || true
    echo "✅ Noto字体安装成功"
else
    echo "⚠️  Noto字体下载失败，但不影响使用"
fi

# 手动创建一个简单的中文字体（基于DejaVu）
echo "📝 创建字体映射配置..."
timeout 10 sudo tee "$FONT_DIR/fonts.conf" > /dev/null << 'EOF'
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
    <alias>
        <family>sans-serif</family>
        <prefer>
            <family>DejaVu Sans</family>
            <family>Liberation Sans</family>
        </prefer>
    </alias>
    <alias>
        <family>serif</family>
        <prefer>
            <family>DejaVu Serif</family>
            <family>Liberation Serif</family>
        </prefer>
    </alias>
    <alias>
        <family>monospace</family>
        <prefer>
            <family>DejaVu Sans Mono</family>
            <family>Liberation Mono</family>
        </prefer>
    </alias>
</fontconfig>
EOF

# 设置字体文件权限
echo "🔧 设置字体文件权限..."
timeout 10 sudo chmod 644 "$FONT_DIR"/* 2>/dev/null || true
timeout 10 sudo chown root:root "$FONT_DIR"/* 2>/dev/null || true

# 刷新字体缓存
echo "🔄 刷新字体缓存..."
timeout 60 sudo fc-cache -fv

# 验证安装结果
echo "✅ 验证字体安装..."
echo "字体目录内容："
timeout 10 ls -la "$FONT_DIR"

echo ""
echo "系统中的字体："
timeout 10 fc-list | grep -i "chinese\|cjk\|han\|noto\|wqy" || echo "未找到中文字体名称"

# 检查我们安装的字体文件
echo ""
echo "🔍 检查安装的字体文件："
for font_file in "$FONT_DIR"/*; do
    if [ -f "$font_file" ] && [[ "$font_file" =~ \.(ttf|ttc|otf)$ ]]; then
        size=$(du -h "$font_file" | cut -f1)
        echo "✅ $font_file ($size)"
    fi
done

# 创建字体测试脚本
echo ""
echo "📝 创建字体测试脚本..."
timeout 10 cat > /tmp/test_fonts.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def test_fonts():
    """测试字体可用性"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.lib.pagesizes import A4
        
        print("🧪 测试字体支持...")
        
        # 测试我们安装的字体
        font_dir = "/usr/share/fonts/truetype/chinese"
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith(('.ttf', '.ttc', '.otf')):
                    font_path = os.path.join(font_dir, font_file)
                    try:
                        font_name = f"Custom_{font_file.replace('.', '_')}"
                        if font_file.endswith('.ttc'):
                            pdfmetrics.registerFont(TTFont(font_name, font_path, subfontIndex=0))
                        else:
                            pdfmetrics.registerFont(TTFont(font_name, font_path))
                        print(f"✅ 成功注册字体: {font_file}")
                        
                        # 创建测试PDF
                        test_pdf = f"/tmp/test_{font_name}.pdf"
                        c = canvas.Canvas(test_pdf, pagesize=A4)
                        c.setFont(font_name, 16)
                        c.drawString(100, 750, "中文测试：你好世界！Hello World 123")
                        c.save()
                        print(f"✅ 测试PDF: {test_pdf}")
                        return True
                        
                    except Exception as e:
                        print(f"❌ 字体注册失败 {font_file}: {e}")
        
        # 测试内置CID字体
        print("\n🔤 测试内置CID字体...")
        cid_fonts = ['STSong-Light', 'STSongStd-Light', 'HeiseiMin-W3']
        for cid_name in cid_fonts:
            try:
                pdfmetrics.registerFont(UnicodeCIDFont(cid_name))
                print(f"✅ CID字体可用: {cid_name}")
                
                test_pdf = f"/tmp/test_{cid_name}.pdf"
                c = canvas.Canvas(test_pdf, pagesize=A4)
                c.setFont(cid_name, 16)
                c.drawString(100, 750, "中文测试：你好世界！Hello World 123")
                c.save()
                print(f"✅ CID测试PDF: {test_pdf}")
                return True
                
            except Exception as e:
                print(f"❌ CID字体不可用 {cid_name}: {e}")
        
        # 测试系统字体
        print("\n🔤 测试系统字体...")
        system_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]
        
        for font_path in system_fonts:
            if os.path.exists(font_path):
                try:
                    font_name = f"System_{os.path.basename(font_path).replace('.', '_')}"
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✅ 系统字体可用: {os.path.basename(font_path)}")
                    
                    test_pdf = f"/tmp/test_{font_name}.pdf"
                    c = canvas.Canvas(test_pdf, pagesize=A4)
                    c.setFont(font_name, 16)
                    c.drawString(100, 750, "English Test: Hello World 123")
                    c.save()
                    print(f"✅ 系统字体测试PDF: {test_pdf}")
                    
                except Exception as e:
                    print(f"❌ 系统字体注册失败 {font_path}: {e}")
        
        return False
        
    except ImportError as e:
        print(f"❌ ReportLab未安装: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_fonts()
    print(f"\n{'✅ 字体测试成功' if success else '⚠️  字体测试失败，但应用仍可运行'}")
    sys.exit(0)
EOF

# 运行字体测试
echo "🧪 运行字体测试..."
timeout 60 python3 /tmp/test_fonts.py

# 清理临时文件
echo "🧹 清理临时文件..."
timeout 30 rm -f /tmp/wqy-microhei.tar.gz /tmp/wqy-microhei.ttc /tmp/NotoSansCJK.* /tmp/test_fonts.py
timeout 30 rm -f /tmp/fonts-wqy-microhei_*.deb /tmp/data.tar.* /tmp/control.tar.*
timeout 30 find /tmp -name "wqy-*" -type d -exec rm -rf {} + 2>/dev/null || true
timeout 30 find /tmp -name "usr" -type d -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "🎉 字体安装完成！"
echo "=================================="
echo "📝 安装说明："
echo "1. 已尝试下载并安装开源中文字体"
echo "2. 已配置字体映射"
echo "3. 已刷新字体缓存"
echo "4. 已测试字体可用性"
echo ""
echo "🔄 请重启您的Flask应用："
echo "   sudo systemctl restart user-system"
echo ""
echo "💡 重要提示："
echo "   即使没有安装中文字体，ReportLab的内置CID字体"
echo "   (如STSong-Light)仍可以显示中文文本"
echo ""
echo "📋 查看测试PDF文件："
echo "   ls -la /tmp/test_*.pdf" 