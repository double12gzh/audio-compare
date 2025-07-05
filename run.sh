#!/bin/bash

echo "正在启动 TTS 音频验收工具..."
echo ""
echo "请确保已安装所有依赖包："
echo "pip install -r requirements.txt"
echo ""
echo "启动应用..."
streamlit run app.py --server.port 8080 --server.address 0.0.0.0