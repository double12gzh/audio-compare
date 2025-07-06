"""
缓存管理器模块
用于缓存音频分析结果和图表，避免重复计算
"""

import hashlib
import pickle
import os
import time
from typing import Any, Optional, Dict
from functools import wraps
import streamlit as st


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = "./cache", max_size: int = 100, ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            max_size: 最大缓存条目数
            ttl: 缓存生存时间（秒）
        """
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.ttl = ttl
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数转换为字符串并生成哈希
        key_str = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{key}.pkl")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        # 检查文件是否过期
        if time.time() - os.path.getmtime(cache_path) > self.ttl:
            os.remove(cache_path)
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            # 如果读取失败，删除损坏的缓存文件
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            
            # 清理过期缓存
            self._cleanup_expired()
            
            # 如果缓存条目过多，删除最旧的
            self._enforce_max_size()
        except Exception as e:
            print(f"缓存写入失败: {e}")
    
    def _cleanup_expired(self):
        """清理过期的缓存文件"""
        current_time = time.time()
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                file_path = os.path.join(self.cache_dir, filename)
                if current_time - os.path.getmtime(file_path) > self.ttl:
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
    
    def _enforce_max_size(self):
        """强制执行最大缓存大小"""
        cache_files = []
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                file_path = os.path.join(self.cache_dir, filename)
                cache_files.append((file_path, os.path.getmtime(file_path)))
        
        if len(cache_files) > self.max_size:
            # 按修改时间排序，删除最旧的
            cache_files.sort(key=lambda x: x[1])
            for file_path, _ in cache_files[:-self.max_size]:
                try:
                    os.remove(file_path)
                except Exception:
                    pass
    
    def clear(self):
        """清空所有缓存"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    os.remove(file_path)
                except Exception:
                    pass


# 全局缓存管理器实例
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cached_result(func):
    """缓存装饰器，用于缓存函数结果"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_manager = get_cache_manager()
        cache_key = cache_manager._generate_key(func.__name__, *args, **kwargs)
        
        # 尝试从缓存获取结果
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 执行函数并缓存结果
        result = func(*args, **kwargs)
        cache_manager.set(cache_key, result)
        return result
    
    return wrapper


def streamlit_cached(func):
    """Streamlit缓存装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 使用Streamlit的缓存机制
        return st.cache_data(ttl=3600)(func)(*args, **kwargs)
    return wrapper 