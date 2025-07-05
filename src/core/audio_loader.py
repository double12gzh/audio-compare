"""
音频加载模块
负责音频文件的加载、验证和预处理
"""

import librosa
import numpy as np
import os
from typing import Optional, Tuple

from ..utils.config import AudioConfig
from ..utils.exceptions import AudioLoadError


class AudioLoader:
    """音频加载器类"""

    def __init__(self, config: Optional[AudioConfig] = None):
        """
        初始化音频加载器

        Args:
            config: 音频配置参数
        """
        self.config = config or AudioConfig()
        self.sample_rate = self.config.default_sample_rate
        self.supported_formats = [".wav", ".mp3", ".flac", ".ogg", ".m4a"]

    def load_audio_from_path(
        self, audio_path: str, resample: bool = True
    ) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """
        从文件路径加载音频文件

        Args:
            audio_path: 音频文件路径
            resample: 是否重采样到配置的采样率

        Returns:
            Tuple[音频数据, 采样率]
        """
        try:
            if not audio_path or not audio_path.strip():
                return None, None

            audio_path = audio_path.strip()
            self._validate_audio_file(audio_path)

            # 根据配置决定是否重采样
            target_sr = self.sample_rate if resample else None
            y, sr = librosa.load(audio_path, sr=target_sr)

            return y, sr

        except Exception as e:
            raise AudioLoadError(f"音频加载失败: {str(e)}")

    def _validate_audio_file(self, audio_path: str):
        """
        验证音频文件

        Args:
            audio_path: 音频文件路径

        Raises:
            AudioLoadError: 文件验证失败时抛出
        """
        if not os.path.exists(audio_path):
            raise AudioLoadError(f"文件不存在: {audio_path}")

        # 检查文件扩展名
        file_ext = os.path.splitext(audio_path)[1].lower()
        if file_ext not in self.supported_formats:
            raise AudioLoadError(f"不支持的音频格式: {file_ext}")

    def resample_audio(
        self, y: np.ndarray, orig_sr: int, target_sr: int
    ) -> Tuple[np.ndarray, int]:
        """
        重采样音频

        Args:
            y: 音频数据
            orig_sr: 原始采样率
            target_sr: 目标采样率

        Returns:
            Tuple[重采样后的音频数据, 目标采样率]
        """
        if orig_sr == target_sr:
            return y, orig_sr

        y_resampled = librosa.resample(y, orig_sr=orig_sr, target_sr=target_sr)
        return y_resampled, target_sr

    def normalize_audio_length(
        self, y1: np.ndarray, y2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        标准化两个音频的长度（取较短的长度）

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据

        Returns:
            Tuple[标准化后的音频1, 标准化后的音频2]
        """
        min_len = min(len(y1), len(y2))
        return y1[:min_len], y2[:min_len]
