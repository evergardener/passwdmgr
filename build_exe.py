# -*- coding: utf-8 -*-
#
# @Created : 2025-12-02 14:05
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    : windows环境构建exe
import PyInstaller.__main__
import os
import shutil
import sys
import platform
from pathlib import Path


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['dist', 'build']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"清理: {dir_name}")


def get_icon_path():
    """获取图标文件路径"""
    icon_files = [
        "resources/icons/favicon.ico",
        "resources/icons/favicon.png",
    ]
    for icon_file in icon_files:
        if os.path.exists(icon_file):
            print(f"使用图标: {icon_file}")
            return icon_file
    print("警告: 未找到图标文件，将使用默认图标")
    return None


def build_linux_arm64():
    """构建Linux ARM64可执行文件"""
    print("=" * 60)
    print("构建 Linux ARM64 可执行文件")
    print("=" * 60)

    clean_build_dirs()
    icon_path = get_icon_path()

    # 设置交叉编译环境变量
    os.environ['CC'] = 'aarch64-linux-gnu-gcc'
    os.environ['CXX'] = 'aarch64-linux-gnu-g++'

    # 定义构建参数
    params = [
        'main.py',
        '--name=PasswordManager',
        '--windowed',
        '--clean',
        '--onefile',
        '--add-data=resources:resources',
        '--add-data=config.json:.',
        '--add-data=*.db:.',
        # 关键：指定目标架构为ARM64
        '--target-arch=aarch64',
        # 隐藏导入
        '--hidden-import=cryptography',
        '--hidden-import=cryptography.hazmat.backends.openssl',
        '--hidden-import=mysql.connector',
        '--hidden-import=PyQt6',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageFile',
        '--hidden-import=PIL._imaging',
        '--exclude-module=tkinter',
    ]

    if icon_path:
        # 对于Linux，使用PNG图标
        if icon_path.endswith('.ico'):
            # 转换ICO为PNG
            png_path = icon_path.replace('.ico', '.png')
            try:
                from PIL import Image
                img = Image.open(icon_path)
                img.save(png_path)
                params.append(f'--icon={png_path}')
            except:
                print("无法转换ICO为PNG，将不使用图标")
        else:
            params.append(f'--icon={icon_path}')

    print("ARM64构建参数:")
    for param in params:
        print(f"  {param}")

    try:
        PyInstaller.__main__.run(params)
        print("\n✅ Linux ARM64 可执行文件构建完成！")

        # 检查文件架构
        import subprocess
        result = subprocess.run(['file', 'dist/PasswordManager'],
                                capture_output=True, text=True)
        print(f"文件信息: {result.stdout}")

    except Exception as e:
        print(f"构建失败: {e}")
        return False

    return True


def create_appdir_structure():
    """创建AppDir结构"""
    print("\n" + "=" * 60)
    print("创建 AppDir 结构")
    print("=" * 60)

    appdir = "PasswordManager.AppDir"

    # 清理旧的AppDir
    if os.path.exists(appdir):
        shutil.rmtree(appdir)

    # 创建目录结构
    dirs = [
        f"{appdir}/usr/bin",
        f"{appdir}/usr/lib",
        f"{appdir}/usr/share/applications",
        f"{appdir}/usr/share/icons/hicolor/256x256/apps",
        f"{appdir}/usr/share/passwordmanager",
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 复制可执行文件
    if os.path.exists("dist/PasswordManager"):
        shutil.copy("dist/PasswordManager", f"{appdir}/usr/bin/")
        os.chmod(f"{appdir}/usr/bin/PasswordManager", 0o755)
        print("✓ 复制可执行文件")
    else:
        print("✗ 可执行文件不存在，请先构建")
        return False

    # 复制资源文件
    if os.path.exists("resources"):
        shutil.copytree("resources", f"{appdir}/usr/share/passwordmanager/resources",
                        dirs_exist_ok=True)
        print("✓ 复制资源文件")

    # 复制配置文件
    if os.path.exists("config.json"):
        shutil.copy("config.json", f"{appdir}/usr/share/passwordmanager/")
        print("✓ 复制配置文件")

    # 复制图标
    icon_source = None
    if os.path.exists("resources/icons/favicon.png"):
        icon_source = "resources/icons/favicon.png"
    elif os.path.exists("resources/icons/favicon.ico"):
        icon_source = "resources/icons/favicon.ico"

    if icon_source:
        if icon_source.endswith('.ico'):
            # 转换ICO为PNG
            try:
                from PIL import Image
                img = Image.open(icon_source)
                img.save(f"{appdir}/usr/share/icons/hicolor/256x256/apps/passwordmanager.png")
                print("✓ 转换并复制图标")
            except Exception as e:
                print(f"✗ 图标转换失败: {e}")
                # 创建默认图标
                create_default_icon(f"{appdir}/usr/share/icons/hicolor/256x256/apps/passwordmanager.png")
        else:
            shutil.copy(icon_source, f"{appdir}/usr/share/icons/hicolor/256x256/apps/passwordmanager.png")
            print("✓ 复制图标")
    else:
        # 创建默认图标
        create_default_icon(f"{appdir}/usr/share/icons/hicolor/256x256/apps/passwordmanager.png")
        print("✓ 创建默认图标")

    # 创建.desktop文件
    create_desktop_file(appdir)

    # 创建AppRun脚本
    create_apprun_script(appdir)

    # 创建AppImage构建脚本
    create_appimage_build_script(appdir)

    print("\n✅ AppDir 结构创建完成！")
    print(f"AppDir 位置: {appdir}")
    print("\n下一步:")
    print("1. 确保您有 appimagetool 工具")
    print("2. 运行: ./build-appimage.sh")

    return True


def create_default_icon(output_path):
    """创建默认图标"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGBA', (256, 256), color=(74, 144, 226, 255))
        draw = ImageDraw.Draw(img)

        # 尝试加载字体
        try:
            font = ImageFont.truetype("Arial", 120)
        except:
            font = ImageFont.load_default()

        # 绘制文字
        draw.text((128, 128), "🔐", font=font, anchor="mm", fill=(255, 255, 255, 255))
        img.save(output_path)
    except Exception as e:
        print(f"创建默认图标失败: {e}")


def create_desktop_file(appdir):
    """创建.desktop文件"""
    desktop_content = """[Desktop Entry]
Type=Application
Name=Password Manager
GenericName=Password Manager
Comment=A secure password manager application
Icon=passwordmanager
Exec=passwordmanager
Categories=Utility;Security;
Terminal=false
StartupNotify=true
X-AppImage-Version=1.0.0
"""

    with open(f"{appdir}/passwordmanager.desktop", 'w') as f:
        f.write(desktop_content)

    # 复制到标准位置
    shutil.copy(f"{appdir}/passwordmanager.desktop",
                f"{appdir}/usr/share/applications/")

    print("✓ 创建 .desktop 文件")


def create_apprun_script(appdir):
    """创建AppRun脚本"""
    apprun_content = """#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"

# 设置环境变量
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS}"

# 设置应用程序特定路径
export APP_BASE="${HERE}/usr/share/passwordmanager"
export RESOURCE_PATH="${APP_BASE}/resources"

# 如果配置文件不存在，从AppImage复制
if [ ! -f "${HOME}/.config/password-manager/config.json" ]; then
    mkdir -p "${HOME}/.config/password-manager"
    cp -f "${APP_BASE}/config.json" "${HOME}/.config/password-manager/" 2>/dev/null || true
fi

# 运行应用程序
exec "${HERE}/usr/bin/PasswordManager" "$@"
"""

    with open(f"{appdir}/AppRun", 'w') as f:
        f.write(apprun_content)

    os.chmod(f"{appdir}/AppRun", 0o755)
    print("✓ 创建 AppRun 脚本")


def create_appimage_build_script(appdir):
    """创建AppImage构建脚本"""
    build_script = """#!/bin/bash
# Password Manager AppImage 构建脚本

set -e

# 检查参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "用法: $0 [版本号]"
    echo "示例: $0 1.0.0"
    exit 0
fi

VERSION="${1:-1.0.0}"
APPDIR="PasswordManager.AppDir"
OUTPUT="PasswordManager-${VERSION}-arm64.AppImage"

echo "=== 构建 Password Manager AppImage ==="
echo "版本: ${VERSION}"
echo "输出文件: ${OUTPUT}"
echo "架构: arm64 (aarch64)"
echo "===================================="

# 检查 appimagetool
if ! command -v appimagetool &> /dev/null; then
    echo "错误: appimagetool 未安装"
    echo "请从 https://github.com/AppImage/AppImageKit/releases 下载"
    echo "或者运行: wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    echo "然后: chmod +x appimagetool-x86_64.AppImage"
    echo "最后: sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool"
    exit 1
fi

# 检查 AppDir 是否存在
if [ ! -d "${APPDIR}" ]; then
    echo "错误: ${APPDIR} 目录不存在"
    echo "请先运行: python build_exe.py --arm64-appimage"
    exit 1
fi

echo "步骤 1/3: 检查 AppDir 结构..."
if [ ! -f "${APPDIR}/AppRun" ]; then
    echo "错误: AppRun 脚本不存在"
    exit 1
fi

if [ ! -f "${APPDIR}/passwordmanager.desktop" ]; then
    echo "错误: .desktop 文件不存在"
    exit 1
fi

if [ ! -f "${APPDIR}/usr/bin/PasswordManager" ]; then
    echo "错误: 可执行文件不存在"
    exit 1
fi

echo "步骤 2/3: 设置图标链接..."
# 确保图标链接正确
if [ -f "${APPDIR}/usr/share/icons/hicolor/256x256/apps/passwordmanager.png" ]; then
    cd "${APPDIR}"
    ln -sf "usr/share/icons/hicolor/256x256/apps/passwordmanager.png" ".DirIcon" 2>/dev/null || true
    ln -sf "usr/share/icons/hicolor/256x256/apps/passwordmanager.png" "passwordmanager.png" 2>/dev/null || true
    cd ..
fi

echo "步骤 3/3: 打包 AppImage..."
# 设置架构为ARM64并打包
ARCH=aarch64 appimagetool "${APPDIR}" "${OUTPUT}"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ AppImage 构建成功!"
    echo "文件: ${OUTPUT}"
    echo "大小: $(du -h ${OUTPUT} | cut -f1)"
    echo ""
    echo "使用说明:"
    echo "1. 赋予执行权限: chmod +x ${OUTPUT}"
    echo "2. 直接运行: ./${OUTPUT}"
    echo "3. 或安装到系统:"
    echo "   sudo mv ${OUTPUT} /usr/local/bin/password-manager"
else
    echo "❌ AppImage 构建失败"
    exit 1
fi
"""

    with open("build-appimage.sh", 'w') as f:
        f.write(build_script)

    os.chmod("build-appimage.sh", 0o755)
    print("✓ 创建 AppImage 构建脚本")


def build_windows_x86_64():
    """构建Windows x86_64可执行文件"""
    print("构建Windows版本...")
    # 现有的Windows构建逻辑
    create_and_use_spec_file()


def create_and_use_spec_file():
    """创建并使用.spec文件进行构建（推荐方式）"""
    clean_build_dirs()
    icon_path = get_icon_path()

    # 定义需要打包的数据文件
    datas = [
        ('resources', 'resources'),  # 打包整个资源目录
        ('*.db', '.'),  # 打包所有数据库文件
    ]

    # 定义需要隐藏导入的模块
    hiddenimports = [
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'cryptography',
        'cryptography.hazmat.backends.openssl',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.kdf',
        'cryptography.hazmat.primitives.ciphers',
        'mysql.connector',
        'PIL',
        'PIL._imaging',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
    ]

    excludes = ['tkinter', 'test', 'unittest']

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas={datas},
    hiddenimports={hiddenimports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={excludes},
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PasswordManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={repr(icon_path) if icon_path else 'NONE'},
)
'''
    spec_filename = 'PasswordManager.spec'
    with open(spec_filename, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print(f"创建并写入: {spec_filename}")

    # 使用spec文件进行构建
    PyInstaller.__main__.run([spec_filename])
    print("✅ 使用spec文件构建完成！")


def print_usage():
    """打印使用说明"""
    print("""
Password Manager 构建工具
=========================

用法:
  python build_exe.py [选项]

选项:
  --windows          构建 Windows x86_64 可执行文件 (默认)
  --arm64-appimage   构建 Linux ARM64 AppImage
  --all              构建所有平台
  --help, -h         显示此帮助信息

示例:
  python build_exe.py --windows          # 构建Windows版本
  python build_exe.py --arm64-appimage   # 构建Linux ARM64 AppImage
  python build_exe.py --all              # 构建所有版本
    """)


def main():
    """主函数"""
    try:
        import PyInstaller
    except ImportError:
        print("请先安装 PyInstaller: pip install pyinstaller")
        sys.exit(1)

    # 检查参数
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "--windows"

    if target in ["--help", "-h"]:
        print_usage()
        return

    if target == "--windows":
        print("构建 Windows x86_64 版本...")
        create_and_use_spec_file()

    elif target == "--arm64-appimage":
        print("构建 Linux ARM64 AppImage...")

        # 检查当前系统
        if platform.system() != "Linux":
            print("警告: ARM64构建建议在Linux系统上进行")
            print("您可以使用Docker容器进行交叉编译:")
            print("  docker run --rm -v $(pwd):/app -w /app python:3.12-slim \\")
            print("    apt-get update && apt-get install -y \\")
            print("    aarch64-linux-gnu-gcc gcc-arm-linux-gnueabihf \\")
            print("    && pip install pyinstaller \\")
            print("    && python build_exe.py --arm64-appimage")

        # 检查必要的包
        try:
            import subprocess
            result = subprocess.run(['which', 'aarch64-linux-gnu-gcc'],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                print("警告: 未找到 aarch64-linux-gnu-gcc 编译器")
                print("请安装交叉编译工具链:")
                print("  Ubuntu/Debian: sudo apt-get install gcc-aarch64-linux-gnu")
                print("  Fedora: sudo dnf install gcc-aarch64-linux-gnu")
                print("  Arch: sudo pacman -S aarch64-linux-gnu-gcc")

                response = input("是否继续？(可能需要系统工具链) [y/N]: ")
                if response.lower() != 'y':
                    return
        except:
            pass

        # 构建可执行文件
        if build_linux_arm64():
            # 创建AppDir结构
            create_appdir_structure()

    elif target == "--all":
        print("构建所有平台版本...")
        print("\n1. 构建Windows版本...")
        create_and_use_spec_file()
        print("\n2. 构建Linux ARM64版本...")
        if build_linux_arm64():
            create_appdir_structure()

    else:
        print(f"未知选项: {target}")
        print_usage()


if __name__ == "__main__":
    main()