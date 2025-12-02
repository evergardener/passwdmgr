# -*- coding: utf-8 -*-
#
# @Created : 2025-12-02 14:05
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    : arm64本地构建appimage


import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def get_pyqt6_paths():
    """获取PyQt6的安装路径和库文件路径"""
    import PyQt6
    from PyQt6 import QtCore

    pyqt6_path = Path(PyQt6.__file__).parent
    qt_path = None

    # 尝试找到Qt库的安装位置
    try:
        # 通过QtCore获取Qt库路径
        qt_path = Path(QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.LibraryPath.LibrariesPath))
    except:
        # 回退到标准路径
        if sys.platform == "linux":
            # Linux下常见的Qt安装路径
            possible_paths = [
                "/usr/lib/aarch64-linux-gnu/qt6",
                "/usr/lib/qt6",
                "/usr/local/lib/qt6",
                str(Path.home() / ".local/lib/qt6"),
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    qt_path = Path(path)
                    break

    return {
        'pyqt6_python': pyqt6_path,
        'qt_libs': qt_path,
    }

def collect_qt_libraries():
    """收集Qt6运行时库"""
    print("收集Qt6运行时库...")

    qt_paths = get_pyqt6_paths()
    libraries_to_copy = []

    # 必需的Qt6核心库
    qt_libs = [
        'libQt6Core.so',
        'libQt6Gui.so',
        'libQt6Widgets.so',
        'libQt6DBus.so',  # DBus支持
    ]

    # 查找这些库
    search_paths = []
    if qt_paths['qt_libs']:
        search_paths.append(qt_paths['qt_libs'])

    # 系统库路径
    system_paths = [
        '/usr/lib/aarch64-linux-gnu',
        '/usr/lib',
        '/usr/local/lib',
    ]
    search_paths.extend(system_paths)

    found_libs = {}
    for lib_name in qt_libs:
        for search_path in search_paths:
            lib_path = Path(search_path) / lib_name
            if lib_path.exists():
                found_libs[lib_name] = str(lib_path)
                print(f"  ✓ 找到 {lib_name}: {lib_path}")
                break
            else:
                # 尝试带版本号的库
                versioned_pattern = f"{lib_name}.*"
                for lib_file in Path(search_path).glob(versioned_pattern):
                    if lib_file.is_file():
                        found_libs[lib_name] = str(lib_file)
                        print(f"  ✓ 找到 {lib_name}: {lib_file}")
                        break

        if lib_name not in found_libs:
            print(f"  ✗ 未找到 {lib_name}")

    return found_libs

def create_fixed_spec_file():
    """创建修复的spec文件，确保PyQt6被正确打包"""

    # 获取PyQt6路径
    import PyQt6
    pyqt6_path = Path(PyQt6.__file__).parent

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

# 添加PyQt6的路径到分析路径
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 打包整个resources目录
        ('resources', 'resources'),
        # ('config.json', '.'),
        # ('*.db', '.'),
        
        # 关键：打包PyQt6的Python模块
        ('{pyqt6_path}', 'PyQt6'),
        
        # 打包Qt插件
        ('/usr/lib/aarch64-linux-gnu/qt6/plugins', 'qt6/plugins'),
        
        # arm64 本地打包注释以下行
        # ('/usr/lib/qt6/plugins', 'qt6/plugins'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtDBus',
        'PyQt6.sip',
        
        'cryptography',
        'cryptography.hazmat.backends.openssl',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
        
        'mysql.connector',
        
        'PIL',
        'PIL.Image',
        'PIL.ImageFile',
        'PIL._imaging',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=['runtime_hook.py'],  # 添加运行时钩子
    excludes=['tkinter', 'test', 'unittest'],
    noarchive=False,
    optimize=0,
)

# 收集二进制文件
pyz = PYZ(a.pure, a.zipped_data)

# 显式添加Qt库
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
    target_arch='aarch64',  # 指定ARM64架构
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/favicon.png' if os.path.exists('resources/icons/favicon.png') else None,
)
'''

    with open('PasswordManager.spec', 'w') as f:
        f.write(spec_content)

    print("✓ 创建修复的spec文件")

def create_runtime_hook():
    """创建运行时钩子，设置Qt环境变量"""

    hook_content = '''# -*- coding: utf-8 -*-
"""
运行时钩子 - 设置Qt环境变量
"""
import os
import sys

def setup_qt_environment():
    """设置Qt环境变量"""
    
    # 获取程序所在目录
    if getattr(sys, 'frozen', False):
        # 打包后的程序
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 设置Qt插件路径
    qt_plugin_paths = []
    
    # 在打包目录中查找插件
    possible_plugin_dirs = [
        os.path.join(base_path, 'qt6', 'plugins'),
        os.path.join(base_path, 'PyQt6', 'Qt6', 'plugins'),
        os.path.join(base_path, 'Qt6', 'plugins'),
    ]
    
    for plugin_dir in possible_plugin_dirs:
        if os.path.exists(plugin_dir):
            qt_plugin_paths.append(plugin_dir)
    
    # 如果找到了插件路径，设置环境变量
    if qt_plugin_paths:
        os.environ['QT_PLUGIN_PATH'] = ':'.join(qt_plugin_paths)
        print(f"设置 QT_PLUGIN_PATH: {os.environ['QT_PLUGIN_PATH']}")
    
    # 设置Qt库路径
    qt_lib_paths = []
    possible_lib_dirs = [
        os.path.join(base_path, 'qt6', 'lib'),
        os.path.join(base_path, 'lib'),
        os.path.join(base_path, 'PyQt6', 'Qt6', 'lib'),
    ]
    
    for lib_dir in possible_lib_dirs:
        if os.path.exists(lib_dir):
            qt_lib_paths.append(lib_dir)
    
    if qt_lib_paths:
        os.environ['LD_LIBRARY_PATH'] = ':'.join(qt_lib_paths) + ':' + os.environ.get('LD_LIBRARY_PATH', '')
    
    # 设置平台插件（对于AppImage很重要）
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(base_path, 'qt6', 'plugins', 'platforms')
    
    # 设置QML导入路径
    os.environ['QML2_IMPORT_PATH'] = os.path.join(base_path, 'qt6', 'qml')

# 在模块导入前执行
setup_qt_environment()
'''

    with open('runtime_hook.py', 'w') as f:
        f.write(hook_content)

    print("✓ 创建运行时钩子")

def build_with_pyqt6_fix():
    """修复PyQt6问题的构建"""

    print("=" * 60)
    print("修复PyQt6依赖问题的ARM64构建")
    print("=" * 60)

    # 清理旧文件
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    # 创建运行时钩子
    create_runtime_hook()

    # 创建修复的spec文件
    create_fixed_spec_file()

    # 使用PyInstaller构建
    cmd = [
        'pyinstaller',
        'PasswordManager.spec',
        '--clean',
        '--noconfirm',
    ]

    print("执行构建命令...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ 构建成功")

        # 验证构建结果
        exe_path = 'dist/PasswordManager'
        if os.path.exists(exe_path):
            print(f"可执行文件: {exe_path}")

            # 检查文件信息
            try:
                file_result = subprocess.run(['file', exe_path],
                                           capture_output=True, text=True)
                print(f"文件信息: {file_result.stdout}")
            except:
                pass

            # 检查依赖
            try:
                ldd_result = subprocess.run(['ldd', exe_path],
                                          capture_output=True, text=True)
                print("依赖检查:")
                print(ldd_result.stdout[:500])  # 只显示前500字符
            except:
                print("无法检查依赖")

        return True
    else:
        print("❌ 构建失败")
        print(f"错误: {result.stderr}")
        return False

def create_appdir_with_qt():
    """创建包含Qt运行时库的AppDir"""

    print("\n创建AppDir结构（包含Qt运行时库）...")

    appdir = "PasswordManager.AppDir"

    # 清理旧的AppDir
    if os.path.exists(appdir):
        shutil.rmtree(appdir)

    # 创建目录结构
    dirs = [
        f"{appdir}/usr/bin",
        f"{appdir}/usr/lib",
        f"{appdir}/usr/lib/qt6",
        f"{appdir}/usr/lib/qt6/plugins",
        f"{appdir}/usr/lib/qt6/plugins/platforms",
        f"{appdir}/usr/share/applications",
        f"{appdir}/usr/share/icons/hicolor/256x256/apps",
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 复制可执行文件
    if os.path.exists("dist/PasswordManager"):
        shutil.copy("dist/PasswordManager", f"{appdir}/usr/bin/")
        os.chmod(f"{appdir}/usr/bin/PasswordManager", 0o755)
        print("✓ 复制可执行文件")
    else:
        print("✗ 可执行文件不存在")
        return False

    # 收集并复制Qt库
    qt_libs = collect_qt_libraries()

    for lib_name, lib_path in qt_libs.items():
        try:
            shutil.copy(lib_path, f"{appdir}/usr/lib/")
            print(f"✓ 复制 {lib_name}")
        except Exception as e:
            print(f"✗ 复制 {lib_name} 失败: {e}")

    # 复制Qt插件
    copy_qt_plugins(appdir)

    # 复制资源文件
    if os.path.exists("resources"):
        shutil.copytree("resources", f"{appdir}/usr/share/passwordmanager/resources",
                       dirs_exist_ok=True)
        print("✓ 复制资源文件")

    # 创建桌面文件
    create_desktop_file(appdir)

    # 处理图标
    copy_icon(appdir)

    # 创建AppRun脚本（修复版）
    create_fixed_apprun(appdir)

    print(f"\n✅ AppDir 创建完成: {appdir}")
    return True

def copy_qt_plugins(appdir):
    """复制Qt插件"""
    print("复制Qt插件...")

    # Qt插件源路径
    plugin_sources = [
        '/usr/lib/aarch64-linux-gnu/qt6/plugins',
        '/usr/lib/qt6/plugins',
        '/usr/local/lib/qt6/plugins',
    ]

    plugin_source = None
    for source in plugin_sources:
        if os.path.exists(source):
            plugin_source = source
            break

    if plugin_source:
        try:
            # 复制平台插件（必需）
            platforms_src = os.path.join(plugin_source, 'platforms')
            if os.path.exists(platforms_src):
                shutil.copytree(platforms_src,
                              f"{appdir}/usr/lib/qt6/plugins/platforms",
                              dirs_exist_ok=True)
                print("✓ 复制平台插件")

            # 复制其他重要插件
            for plugin_type in ['platformthemes', 'imageformats', 'styles']:
                plugin_src = os.path.join(plugin_source, plugin_type)
                if os.path.exists(plugin_src):
                    shutil.copytree(plugin_src,
                                  f"{appdir}/usr/lib/qt6/plugins/{plugin_type}",
                                  dirs_exist_ok=True)
                    print(f"✓ 复制 {plugin_type} 插件")
        except Exception as e:
            print(f"✗ 复制插件失败: {e}")
    else:
        print("✗ 未找到Qt插件")

def create_desktop_file(appdir):
    """创建桌面文件"""
    desktop_content = '''[Desktop Entry]
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
'''

    desktop_path = f"{appdir}/passwordmanager.desktop"
    with open(desktop_path, 'w') as f:
        f.write(desktop_content)

    # 复制到标准位置
    shutil.copy(desktop_path, f"{appdir}/usr/share/applications/")
    print("✓ 创建桌面文件")

def copy_icon(appdir):
    """复制图标"""
    # 尝试不同图标源
    icon_sources = [
        'resources/icons/favicon.png',
        'resources/icons/favicon.ico',
    ]

    icon_source = None
    for source in icon_sources:
        if os.path.exists(source):
            icon_source = source
            break

    icon_dest = f"{appdir}/usr/share/icons/hicolor/256x256/apps/passwordmanager.png"

    if icon_source:
        if icon_source.endswith('.ico'):
            # 转换ICO为PNG
            try:
                from PIL import Image
                img = Image.open(icon_source)
                img.save(icon_dest)
                print("✓ 转换并复制图标")
            except Exception as e:
                print(f"✗ 图标转换失败: {e}")
                create_default_icon(icon_dest)
        else:
            shutil.copy(icon_source, icon_dest)
            print("✓ 复制图标")
    else:
        create_default_icon(icon_dest)
        print("✓ 创建默认图标")

    # 创建图标链接
    os.chdir(appdir)
    os.symlink('usr/share/icons/hicolor/256x256/apps/passwordmanager.png', '.DirIcon')
    os.symlink('usr/share/icons/hicolor/256x256/apps/passwordmanager.png', 'passwordmanager.png')
    os.chdir('..')

def create_default_icon(path):
    """创建默认图标"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGBA', (256, 256), color=(74, 144, 226, 255))
        draw = ImageDraw.Draw(img)

        # 尝试使用DejaVu字体
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        ]

        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, 100)
                    break
                except:
                    pass

        if not font:
            # 使用默认字体
            font = ImageFont.load_default()

        # 绘制锁图标
        draw.text((128, 128), "🔐", font=font, anchor="mm",
                 fill=(255, 255, 255, 255))
        img.save(path)
    except Exception as e:
        print(f"创建默认图标失败: {e}")

def create_fixed_apprun(appdir):
    """创建修复的AppRun脚本"""

    apprun_content = '''#!/bin/bash
# 修复版AppRun脚本 - 专门解决PyQt6依赖问题

set -e

# 获取AppImage所在目录
HERE="$(dirname "$(readlink -f "${0}")")"
echo "AppImage目录: $HERE"

# 设置环境变量
export PATH="${HERE}/usr/bin:${PATH}"

# 设置库路径 - 关键修复
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib/qt6:${LD_LIBRARY_PATH}"

# 设置Qt环境变量 - 关键修复
export QT_PLUGIN_PATH="${HERE}/usr/lib/qt6/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${HERE}/usr/lib/qt6/plugins/platforms"
export QML2_IMPORT_PATH="${HERE}/usr/lib/qt6/qml"

# 设置Python路径
export PYTHONPATH="${HERE}/usr/share/passwordmanager:${PYTHONPATH}"

# 调试信息
echo "环境变量设置:"
echo "  LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
echo "  QT_PLUGIN_PATH=$QT_PLUGIN_PATH"
echo "  QT_QPA_PLATFORM_PLUGIN_PATH=$QT_QPA_PLATFORM_PLUGIN_PATH"

# 检查Qt库
echo "检查Qt库..."
ls -la "${HERE}/usr/lib/" | grep -i qt || echo "未找到Qt库"

# 检查Qt插件
echo "检查Qt插件..."
ls -la "${HERE}/usr/lib/qt6/plugins/" 2>/dev/null || echo "未找到插件目录"
ls -la "${HERE}/usr/lib/qt6/plugins/platforms/" 2>/dev/null || echo "未找到平台插件"

# 检查可执行文件
echo "检查可执行文件..."
ls -la "${HERE}/usr/bin/PasswordManager"

# 设置应用程序数据目录
export APP_DATA_DIR="${HOME}/.local/share/password-manager"
mkdir -p "${APP_DATA_DIR}"

# 复制默认配置（如果不存在）
if [ ! -f "${HOME}/.config/password-manager/config.json" ]; then
    mkdir -p "${HOME}/.config/password-manager"
    cp -f "${HERE}/usr/share/passwordmanager/config.json" \
          "${HOME}/.config/password-manager/" 2>/dev/null || true
fi

# 复制数据库文件（如果不存在）
if [ ! -f "${APP_DATA_DIR}/password_manager.db" ]; then
    cp -f "${HERE}/usr/share/passwordmanager/*.db" \
          "${APP_DATA_DIR}/" 2>/dev/null || true
fi

echo "启动应用程序..."
# 运行应用程序
exec "${HERE}/usr/bin/PasswordManager" "$@"
'''

    apprun_path = f"{appdir}/AppRun"
    with open(apprun_path, 'w') as f:
        f.write(apprun_content)

    os.chmod(apprun_path, 0o755)
    print("✓ 创建修复的AppRun脚本")

def package_appimage():
    """打包AppImage"""

    print("\n打包AppImage...")

    # 检查appimagetool
    appimagetool_path = None
    possible_paths = [
        '/usr/local/bin/appimagetool',
        '/usr/bin/appimagetool',
        './appimagetool',
    ]

    for path in possible_paths:
        if os.path.exists(path):
            appimagetool_path = path
            break

    if not appimagetool_path:
        print("下载appimagetool...")
        subprocess.run([
            'wget', '-q',
            'https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-aarch64.AppImage',
            '-O', 'appimagetool'
        ], check=True)
        os.chmod('appimagetool', 0o755)
        appimagetool_path = './appimagetool'

    # 打包AppImage
    output = "PasswordManager-arm64-fixed.AppImage"
    cmd = [appimagetool_path, 'PasswordManager.AppDir', output]

    # 设置架构
    env = os.environ.copy()
    env['ARCH'] = 'aarch64'

    print(f"执行打包: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ AppImage创建成功: {output}")

        # 显示文件信息
        try:
            subprocess.run(['file', output], check=True)
            subprocess.run(['ls', '-lh', output], check=True)
        except:
            pass

        return True
    else:
        print("❌ AppImage创建失败")
        print(f"错误: {result.stderr}")
        return False

def test_appimage():
    """测试AppImage"""

    appimage = "PasswordManager-arm64-fixed.AppImage"

    if not os.path.exists(appimage):
        print("AppImage不存在")
        return

    print(f"\n测试AppImage: {appimage}")

    # 赋予执行权限
    os.chmod(appimage, 0o755)

    # 运行测试命令
    print("运行测试命令...")
    try:
        result = subprocess.run([appimage, '--appimage-help'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ AppImage测试通过")
        else:
            print("❌ AppImage测试失败")
            print(f"输出: {result.stdout}")
            print(f"错误: {result.stderr}")
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("Password Manager ARM64 AppImage修复构建工具")
    print("专门解决PyQt6模块缺失问题")
    print("=" * 60)

    try:
        # 检查必要模块
        import PyQt6
        print("✓ PyQt6 已安装")
    except ImportError:
        print("✗ PyQt6 未安装，正在安装...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyQt6'], check=True)

    # 构建流程
    print("\n1. 修复PyQt6依赖并构建...")
    if not build_with_pyqt6_fix():
        return

    print("\n2. 创建AppDir结构...")
    if not create_appdir_with_qt():
        return

    print("\n3. 打包AppImage...")
    if not package_appimage():
        return

    print("\n4. 测试AppImage...")
    test_appimage()

    print("\n" + "=" * 60)
    print("构建完成!")
    print("=" * 60)
    print(f"\n生成的AppImage: PasswordManager-arm64-fixed.AppImage")
    print("\n使用说明:")
    print("  chmod +x PasswordManager-arm64-fixed.AppImage")
    print("  ./PasswordManager-arm64-fixed.AppImage")
    print("\n如果仍有问题，请查看AppRun脚本中的调试信息")

if __name__ == "__main__":
    main()