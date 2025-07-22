#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
德州扑克游戏后端启动脚本
"""

import uvicorn
import os
from pathlib import Path

# 设置工作目录
backend_dir = Path(__file__).parent
os.chdir(backend_dir)

if __name__ == "__main__":
    print("正在启动德州扑克游戏后端服务器...")
    print(f"工作目录: {backend_dir}")
    print("服务器地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("WebSocket连接: ws://localhost:8000/ws")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )