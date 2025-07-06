#!/usr/bin/env python3
"""
缓存清理工具
用于清理过期的缓存文件和Streamlit缓存
"""

import os
import shutil
import streamlit as st
from src.utils.cache_manager import get_cache_manager


def clear_all_caches():
    """清理所有缓存"""
    print("🧹 开始清理缓存...")
    
    # 清理文件缓存
    cache_manager = get_cache_manager()
    cache_manager.clear()
    print("✅ 文件缓存已清理")
    
    # 清理Streamlit缓存
    try:
        st.cache_data.clear()
        print("✅ Streamlit数据缓存已清理")
    except Exception as e:
        print(f"⚠️  Streamlit缓存清理失败: {e}")
    
    # 清理临时文件
    temp_dirs = ["./cache", "./temp", "./tmp"]
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"✅ 临时目录已清理: {temp_dir}")
            except Exception as e:
                print(f"⚠️  临时目录清理失败 {temp_dir}: {e}")
    
    print("🎉 缓存清理完成！")


def show_cache_info():
    """显示缓存信息"""
    cache_manager = get_cache_manager()
    cache_dir = cache_manager.cache_dir
    
    if os.path.exists(cache_dir):
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.pkl')]
        total_size = sum(os.path.getsize(os.path.join(cache_dir, f)) for f in cache_files)
        
        print(f"📊 缓存信息:")
        print(f"  缓存目录: {cache_dir}")
        print(f"  缓存文件数: {len(cache_files)}")
        print(f"  总大小: {total_size / 1024 / 1024:.2f} MB")
        print(f"  最大缓存数: {cache_manager.max_size}")
        print(f"  缓存TTL: {cache_manager.ttl} 秒")
    else:
        print("📊 缓存目录不存在")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "clear":
            clear_all_caches()
        elif command == "info":
            show_cache_info()
        else:
            print("用法: python cache_cleaner.py [clear|info]")
    else:
        print("缓存清理工具")
        print("用法:")
        print("  python cache_cleaner.py clear  # 清理所有缓存")
        print("  python cache_cleaner.py info   # 显示缓存信息") 