# 密码管理器

## 项目功能概述

这是一个完全本地使用的密码管理器，支持：
1. 管理员密码：程序打开不强制校验密码（选择跳过可进入程序），查看密码需校验管理员密码；
2. 密码条目加密：密码条目使用AES256加密，密码条目的密钥使用用户密码进行计算，用户密码使用MD5加密；
3. 密码条目管理：支持新增、删除、编辑密码条目；
4. 数据库存储：支持SQLite（默认）和MySQL，相关配置保存本地 `config.json`，暂未做加密存储；
5. 数据库迁移（未验证，慎用！）：支持SQLite到MySQL数据库迁移，不支持反向。

## 项目构建

1. 支持构建 Window 环境 x86_64 架构 exe 单文件；
2. 支持构建 Linux arm64 架构 appimage 单文件；
3. 后续是否支持其它架构或程序包取决于使用需求，短期内大概率是没有的，主要是编了也测不了。

## 使用

### IDE 运行

1. 安装项目依赖： `pip install requirements.txt`;
2. 运行启动文件 `main.py`，会在项目根目录生成 `config.json` 和 `sqlite.db` 文件，并打开程序。

### exe 构建

1. 安装项目依赖： `pip install requirements.txt`;
2. 运行 exe 构建脚本：`build_exe.py`;
3. 如果一切顺利，构建后会在项目根目录生成 `dist` 文件夹，里面有 `PasswordManager.exe` 文件，运行即可。

### appimage 构建

1. 安装项目依赖： `pip install requirements.txt`;
2. 运行 appimage 构建脚本：`build_arm64.py`;


## AI使用声明

本项目几乎**所有代码**使用DeepSeek官方助手生成，作者对于Python GUI及QT相关开发一窍不通，因此如果遇到任何bug或问题，请下载之后，上传 `core`, `gui`, `utils`, `main.py` 等主要文件至AI询问解决。

就算问我，我也是上面这个方法解决。