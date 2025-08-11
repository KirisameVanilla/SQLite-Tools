@echo off
echo 启动SQLite桌面工具...
echo.

REM 激活虚拟环境并运行程序
call venv\Scripts\activate
python sqlite_tool.py

echo.
echo 程序已退出
pause
