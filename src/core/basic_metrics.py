"""
基本音频指标计算模块
包含时长、RMS、过零率等基本音频特征
"""

import numpy as np
import librosa
from typing import Dict, Any


class BasicMetrics:
    """基本音频指标计算类"""

    @staticmethod
    def calculate_duration(y: np.ndarray, sr: int) -> float:
        """
        计算音频时长

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            音频时长（秒）
        """
        return len(y) / sr

    @staticmethod
    def calculate_rms(y: np.ndarray) -> float:
        """
        计算均方根值（Root Mean Square）

        Args:
            y: 音频数据

        Returns:
            RMS值
        """
        return np.sqrt(np.mean(y**2))

    @staticmethod
    def calculate_zero_crossing_rate(y: np.ndarray) -> float:
        """
        计算过零率

        Args:
            y: 音频数据

        Returns:
            过零率
        """
        return np.mean(librosa.feature.zero_crossing_rate(y))

    @staticmethod
    def calculate_peak_amplitude(y: np.ndarray) -> float:
        """
        计算峰值幅度

        Args:
            y: 音频数据

        Returns:
            峰值幅度
        """
        return np.max(np.abs(y))

    @staticmethod
    def calculate_crest_factor(y: np.ndarray) -> float:
        """
        计算峰值因子（峰值与RMS的比值）

        Args:
            y: 音频数据

        Returns:
            峰值因子
        """
        rms = BasicMetrics.calculate_rms(y)
        if rms == 0:
            return 0.0
        peak = BasicMetrics.calculate_peak_amplitude(y)
        return peak / rms

    @staticmethod
    def calculate_dynamic_range(y: np.ndarray) -> float:
        """
        计算动态范围（最大值与最小值的差值）

        Args:
            y: 音频数据

        Returns:
            动态范围
        """
        return np.max(y) - np.min(y)

    @staticmethod
    def extract_all_basic_features(y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        提取所有基本特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            基本特征字典
        """
        features = {
            "duration": BasicMetrics.calculate_duration(y, sr),
            "rms": BasicMetrics.calculate_rms(y),
            "zero_crossing_rate": BasicMetrics.calculate_zero_crossing_rate(y),
            "peak_amplitude": BasicMetrics.calculate_peak_amplitude(y),
            "crest_factor": BasicMetrics.calculate_crest_factor(y),
            "dynamic_range": BasicMetrics.calculate_dynamic_range(y),
        }
        return features

    @staticmethod
    def get_audio_info(y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        获取音频基本信息

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            音频信息字典
        """
        if y is None:
            return {}

        return {
            "duration": BasicMetrics.calculate_duration(y, sr),
            "sample_rate": sr,
            "rms": BasicMetrics.calculate_rms(y),
            "zero_crossing_rate": BasicMetrics.calculate_zero_crossing_rate(y),
        }
