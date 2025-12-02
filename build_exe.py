import PyInstaller.__main__
import os
import shutil
import sys


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['dist', 'build']  # 移除了 __pycache__
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


def create_and_use_spec_file():
    """创建并使用.spec文件进行构建（推荐方式）"""
    clean_build_dirs()
    icon_path = get_icon_path()

    # 定义需要打包的数据文件
    datas = [
        ('resources', 'resources'),  # 打包整个资源目录
        ('config.json', '.'),
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


def build_with_pyinstaller():
    """方式二：直接使用参数构建（备选）"""
    print("=" * 60)
    print("PyInstaller 打包工具")
    print("=" * 60)
    clean_build_dirs()
    icon_file = get_icon_path()

    # 注意：Windows路径分隔符为分号(;)
    params = [
        'main.py',
        '--name=PasswordManager',
        '--windowed',
        '--clean',
        '--onefile',
        # 关键修改：打包整个resources目录
        '--add-data=resources;resources',
        '--add-data=config.json;.',
        '--add-data=*.db;.',
        '--hidden-import=cryptography',
        '--hidden-import=cryptography.hazmat.backends.openssl',
        '--hidden-import=mysql.connector',
        '--hidden-import=PyQt6',
        '--hidden-import=PIL',
    ]

    if icon_file:
        params.append(f'--icon={icon_file}')

    print("构建参数:")
    for param in params:
        print(f"  {param}")

    PyInstaller.__main__.run(params)
    print("\n✅ 直接参数构建完成！")


if __name__ == "__main__":
    try:
        import PyInstaller
    except ImportError:
        print("请先安装 PyInstaller: pip install pyinstaller")
        sys.exit(1)

    # 推荐使用方式一：创建并使用spec文件
    create_and_use_spec_file()

    # 或者使用方式二：直接参数构建（注释掉上一行，取消下面一行的注释）
    # build_with_pyinstaller()