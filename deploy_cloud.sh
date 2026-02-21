@echo off
REM ===== 云服务器自动部署脚本 =====
REM 在阿里云 Windows 服务器的 PowerShell 中执行

echo [1/6] 安装 Python 依赖包...
pip install requests beautifulsoup4 lxml pandas numpy pyyaml loguru schedule
pip install easytrader

echo [2/6] 测试 easytrader 安装...
python -c "import easytrader; print('easytrader 安装成功')"

echo [3/6] 创建项目目录...
mkdir C:\arbitrage_cn
mkdir C:\arbitrage_cn\src
mkdir C:\arbitrage_cn\src\api
mkdir C:\arbitrage_cn\src\strategies
mkdir C:\arbitrage_cn\src\utils
mkdir C:\arbitrage_cn\config
mkdir C:\arbitrage_cn\logs
mkdir C:\arbitrage_cn\data

echo [4/6] 下载项目文件...
REM 这里需要手动上传项目文件
echo 请将 Mac 上的项目文件上传到 C:\arbitrage_cn\

echo [5/6] 测试 Python 环境...
python --version

echo [6/6] 部署完成！
echo.
echo 下一步：
echo 1. 安装涨乐财富通
echo 2. 登录券商客户端
echo 3. 测试 easytrader 连接
echo.
pause
