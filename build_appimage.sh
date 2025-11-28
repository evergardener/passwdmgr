#!/bin/bash

# 密码管理器 AppImage 打包脚本
set -e

echo "开始构建 Password Manager AppImage..."

# 清理旧构建
rm -rf build/ dist/ AppDir

# 创建虚拟环境（可选）
# python3 -m venv venv
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 使用 PyInstaller 构建
echo "使用 PyInstaller 构建..."
pyinstaller --name="PasswordManager" \
            --windowed \
            --onefile \
            --add-data="gui/*.py:gui" \
            --add-data="core/*.py:core" \
            --add-data="models/*.py:models" \
            --add-data="utils/*.py:utils" \
            --hidden-import="mysql.connector" \
            --hidden-import="cryptography" \
            --hidden-import="PyQt6" \
            --target-arch=arm64 \
            main.py

# 创建 AppDir 结构
echo "创建 AppDir 结构..."
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# 复制可执行文件
cp dist/PasswordManager AppDir/usr/bin/

# 创建图标（如果没有，可以使用系统图标）
if [ ! -f "icons/app_icon.png" ]; then
    mkdir -p icons
    # 这里可以创建一个简单的图标
    convert -size 256x256 xc:blue -pointsize 20 -fill white -annotate +0+0 "PM" icons/app_icon.png
fi

cp icons/app_icon.png AppDir/usr/share/icons/hicolor/256x256/apps/password-manager.png

# 创建桌面文件
cat > AppDir/usr/share/applications/password-manager.desktop << EOF
[Desktop Entry]
Name=Password Manager
Comment=A secure password manager application
Exec=PasswordManager
Icon=password-manager
Type=Application
Categories=Utility;Security;
StartupNotify=true
Terminal=false
EOF

# 下载 linuxdeploy 工具（如果不存在）
if [ ! -f "linuxdeploy-arm64.AppImage" ]; then
    echo "下载 linuxdeploy AppImage..."
    wget -O linuxdeploy-arm64.AppImage \
        "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-arm64.AppImage"
    chmod +x linuxdeploy-arm64.AppImage
fi

# 创建 AppImage
echo "创建 AppImage..."
./linuxdeploy-arm64.AppImage \
    --appdir AppDir \
    --output appimage

echo "构建完成！AppImage 文件已创建。"