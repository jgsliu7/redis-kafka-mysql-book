#!/bin/zsh
# 双击启动 0917/ 审阅页同步服务；关掉本窗口即停止服务。
cd "$(dirname "$0")/../scripts" || exit 1
echo "审阅同步服务启动中…… 浏览器打开 → http://127.0.0.1:8734/"
echo "（关闭本窗口或按 Ctrl+C 停止服务；定稿自动落盘 0917/finals/，无需手动保存）"
python3 review_sync_server.py
