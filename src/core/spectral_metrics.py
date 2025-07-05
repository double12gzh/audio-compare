"""
频谱指标计算模块
包含频谱质心、带宽、滚降等频谱特征
"""

import numpy as np
import librosa
from typing import Dict, Any, Optional


class SpectralMetrics:
    """频谱指标计算类"""

    def __init__(
        self,
        n_fft: int = 2048,
        hop_length: int = 512,
        fmin: int = 0,
        fmax: Optional[int] = None,
    ):
        """
        初始化频谱指标计算器

        Args:
            n_fft: FFT窗口大小
            hop_length: 跳跃长度
            fmin: 最小频率
            fmax: 最大频率
        """
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.fmin = fmin
        self.fmax = fmax

    def calculate_spectral_centroid(self, y: np.ndarray, sr: int) -> float:
        """
        计算频谱质心

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            频谱质心
        """
        return np.mean(
            librosa.feature.spectral_centroid(
                y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length
            )
        )

    def calculate_spectral_bandwidth(self, y: np.ndarray, sr: int) -> float:
        """
        计算频谱带宽

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            频谱带宽
        """
        return np.mean(
            librosa.feature.spectral_bandwidth(
                y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length
            )
        )

    def calculate_spectral_rolloff(
        self, y: np.ndarray, sr: int, roll_percent: float = 0.85
    ) -> float:
        """
        计算频谱滚降

        Args:
            y: 音频数据
            sr: 采样率
            roll_percent: 滚降百分比

        Returns:
            频谱滚降
        """
        return np.mean(
            librosa.feature.spectral_rolloff(
                y=y,
                sr=sr,
                roll_percent=roll_percent,
                n_fft=self.n_fft,
                hop_length=self.hop_length,
            )
        )

    def calculate_spectral_contrast(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        计算频谱对比度

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            频谱对比度特征
        """
        return np.mean(
            librosa.feature.spectral_contrast(
                y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length
            ),
            axis=1,
        )

    def calculate_spectral_flatness(self, y: np.ndarray, sr: int) -> float:
        """
        计算频谱平坦度

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            频谱平坦度
        """
        return np.mean(
            librosa.feature.spectral_flatness(
                y=y, n_fft=self.n_fft, hop_length=self.hop_length
            )
        )

    def calculate_spectral_rolloff_percentile(
        self, y: np.ndarray, sr: int, percentile: float = 0.85
    ) -> float:
        """
        计算频谱滚降百分位数

        Args:
            y: 音频数据
            sr: 采样率
            percentile: 百分位数

        Returns:
            频谱滚降百分位数
        """
        return np.mean(
            librosa.feature.spectral_rolloff(
                y=y,
                sr=sr,
                roll_percent=percentile,
                n_fft=self.n_fft,
                hop_length=self.hop_length,
            )
        )

    def calculate_spectral_centroid_std(self, y: np.ndarray, sr: int) -> float:
        """
        计算频谱质心标准差

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            频谱质心标准差
        """
        return np.std(
            librosa.feature.spectral_centroid(
                y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length
            )
        )

    def calculate_spectral_bandwidth_std(self, y: np.ndarray, sr: int) -> float:
        """
        计算频谱带宽标准差

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            频谱带宽标准差
        """
        return np.std(
            librosa.feature.spectral_bandwidth(
                y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length
            )
        )

    def extract_all_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取所有频谱特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            频谱特征字典
        """
        features = {
            "spectral_centroid": self.calculate_spectral_centroid(y, sr),
            "spectral_bandwidth": self.calculate_spectral_bandwidth(y, sr),
            "spectral_rolloff": self.calculate_spectral_rolloff(y, sr),
            "spectral_flatness": self.calculate_spectral_flatness(y, sr),
            "spectral_centroid_std": self.calculate_spectral_centroid_std(y, sr),
            "spectral_bandwidth_std": self.calculate_spectral_bandwidth_std(y, sr),
        }

        # 添加频谱对比度（返回均值）
        spectral_contrast = self.calculate_spectral_contrast(y, sr)
        features["spectral_contrast_mean"] = np.mean(spectral_contrast)
        features["spectral_contrast_std"] = np.std(spectral_contrast)

        return features

    def extract_spectral_features_for_comparison(
        self, y: np.ndarray, sr: int
    ) -> Dict[str, np.ndarray]:
        """
        提取用于比较的频谱特征（返回完整特征向量）

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            频谱特征字典（包含完整特征向量）
        """
        features = {
            "spectral_centroid": librosa.feature.spectral_centroid(
                y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length
            )[0],
            "spectral_bandwidth": librosa.feature.spectral_bandwidth(
                y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length
            )[0],
            "spectral_rolloff": librosa.feature.spectral_rolloff(
                y=y,
                sr=sr,
                roll_percent=0.85,
                n_fft=self.n_fft,
                hop_length=self.hop_length,
            )[0],
            "spectral_contrast": librosa.feature.spectral_contrast(
                y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length
            ),
        }
        return features
