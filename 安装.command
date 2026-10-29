#!/bin/bash
cd "$(dirname "$0")" || exit 1
clear
echo "短片六工序 · 安装"
echo "================================"
echo
bash ./install.sh
echo
echo "================================"
read -n 1 -s -r -p "按任意键关闭窗口"
echo
