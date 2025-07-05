"""
特征提取模块
整合所有音频特征提取功能
"""

import numpy as np
import librosa
from typing import Dict, Any, Optional

from .basic_metrics import BasicMetrics
from .spectral_metrics import SpectralMetrics
from .mfcc_metrics import MFCCMetrics
from ..utils.config import AudioConfig
from ..utils.exceptions import FeatureExtractionError


class FeatureExtractor:
    """特征提取器类"""

    def __init__(self, config: Optional[AudioConfig] = None):
        """
        初始化特征提取器

        Args:
            config: 音频配置参数
        """
        self.config = config or AudioConfig()
        self._setup_components()

    def _setup_components(self):
        """设置各个组件"""
        self.basic_calculator = BasicMetrics()
        self.spectral_calculator = SpectralMetrics(
            n_fft=self.config.n_fft,
            hop_length=self.config.hop_length,
            fmin=self.config.fmin,
            fmax=self.config.fmax,
        )
        self.mfcc_calculator = MFCCMetrics(
            n_mfcc=self.config.n_mfcc,
            n_fft=self.config.n_fft,
            hop_length=self.config.hop_length,
            dct_type=self.config.dct_type,
            norm=self.config.norm,
        )

    def extract_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取音频特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            特征字典
        """
        if y is None:
            raise FeatureExtractionError("音频数据为空")

        try:
            features = {}

            # 基本特征
            basic_features = self.basic_calculator.extract_all_basic_features(y, sr)
            features.update(basic_features)

            # 频谱特征
            spectral_features = self.spectral_calculator.extract_all_spectral_features(
                y, sr
            )
            features.update(spectral_features)

            # MFCC特征
            mfcc_features = self.mfcc_calculator.extract_all_mfcc_features(y, sr)
            features.update(mfcc_features)

            return features

        except Exception as e:
            raise FeatureExtractionError(f"特征提取失败: {str(e)}")

    def extract_basic_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        提取基本特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            基本特征字典
        """
        return self.basic_calculator.extract_all_basic_features(y, sr)

    def extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取频谱特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            频谱特征字典
        """
        return self.spectral_calculator.extract_all_spectral_features(y, sr)

    def extract_mfcc_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取MFCC特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            MFCC特征字典
        """
        return self.mfcc_calculator.extract_all_mfcc_features(y, sr)

    def extract_features_for_comparison(
        self, y: np.ndarray, sr: int
    ) -> Dict[str, np.ndarray]:
        """
        提取用于比较的特征（返回完整特征向量）

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            特征字典（包含完整特征向量）
        """
        features = {}

        # 频谱特征
        spectral_features = (
            self.spectral_calculator.extract_spectral_features_for_comparison(y, sr)
        )
        features.update(spectral_features)

        # MFCC特征
        mfcc_features = self.mfcc_calculator.extract_mfcc_for_comparison(y, sr)
        features.update(mfcc_features)

        # 节奏特征
        features["tempo"] = librosa.beat.tempo(y=y, sr=sr)

        return features

    def get_audio_info(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        获取音频基本信息

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            音频信息字典
        """
        return self.basic_calculator.get_audio_info(y, sr)

    def extract_rhythm_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取节奏特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            节奏特征字典
        """
        try:
            # 计算节拍
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

            # 计算起始强度
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)

            # 计算节拍间隔
            beat_intervals = (
                np.diff(beat_frames) if len(beat_frames) > 1 else np.array([0])
            )

            return {
                "tempo": float(tempo),
                "beat_frames": beat_frames,
                "onset_strength_mean": float(np.mean(onset_env)),
                "onset_strength_std": float(np.std(onset_env)),
                "beat_intervals_mean": float(np.mean(beat_intervals)),
                "beat_intervals_std": float(np.std(beat_intervals)),
            }
        except Exception as e:
            return {
                "tempo": 0.0,
                "beat_frames": np.array([]),
                "onset_strength_mean": 0.0,
                "onset_strength_std": 0.0,
                "beat_intervals_mean": 0.0,
                "beat_intervals_std": 0.0,
            }
