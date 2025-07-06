#!/usr/bin/env python3
"""
优化版启动脚本
包含性能优化选项和缓存管理
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def setup_optimized_environment():
    """设置优化环境"""
    print("🚀 设置优化环境...")
    
    # 设置环境变量
    os.environ["STREAMLIT_SERVER_MAX_UPLOAD_SIZE"] = "200"  # 200MB
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    
    # 创建缓存目录
    cache_dir = Path("./cache")
    cache_dir.mkdir(exist_ok=True)
    
    print("✅ 环境设置完成")


def clear_cache():
    """清理缓存"""
    print("🧹 清理缓存...")
    try:
        from cache_cleaner import clear_all_caches
        clear_all_caches()
    except ImportError:
        print("⚠️  缓存清理工具不可用")
        # 手动清理缓存目录
        cache_dir = Path("./cache")
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            cache_dir.mkdir()
            print("✅ 缓存目录已清理")


def show_cache_info():
    """显示缓存信息"""
    try:
        from cache_cleaner import show_cache_info
        show_cache_info()
    except ImportError:
        print("⚠️  缓存信息工具不可用")


def start_app(port=8501, host="localhost", clear_cache_first=False):
    """启动应用"""
    if clear_cache_first:
        clear_cache()
    
    setup_optimized_environment()
    
    print(f"🎵 启动TTS音频验收工具...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"🔧 调试模式: 已启用")
    print(f"💾 缓存: 已启用")
    
    # 启动Streamlit应用
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.address", host,
        "--server.maxUploadSize", "200",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="TTS音频验收工具 - 优化版启动器")
    parser.add_argument("--port", type=int, default=8501, help="服务器端口")
    parser.add_argument("--host", default="localhost", help="服务器地址")
    parser.add_argument("--clear-cache", action="store_true", help="启动前清理缓存")
    parser.add_argument("--cache-info", action="store_true", help="显示缓存信息")
    parser.add_argument("--clear-cache-only", action="store_true", help="仅清理缓存")
    
    args = parser.parse_args()
    
    if args.cache_info:
        show_cache_info()
        return
    
    if args.clear_cache_only:
        clear_cache()
        return
    
    start_app(args.port, args.host, args.clear_cache)


if __name__ == "__main__":
    main() 