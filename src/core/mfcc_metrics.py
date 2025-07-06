"""
MFCC指标计算模块
包含MFCC特征提取和计算
"""

import numpy as np
import librosa
from typing import Dict, Any, Optional


class MFCCMetrics:
    """MFCC指标计算类"""

    def __init__(
        self,
        n_mfcc: int = 13,
        n_fft: int = 2048,
        hop_length: int = 512,
        dct_type: int = 2,
        norm: str = "ortho",
    ):
        """
        初始化MFCC指标计算器

        Args:
            n_mfcc: MFCC系数数量
            n_fft: FFT窗口大小
            hop_length: 跳跃长度
            dct_type: DCT类型
            norm: 归一化方式
        """
        self.n_mfcc = n_mfcc
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.dct_type = dct_type
        self.norm = norm

    def extract_mfcc(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        提取MFCC特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            MFCC特征矩阵
        """
        return librosa.feature.mfcc(
            y=y,
            sr=sr,
            n_mfcc=self.n_mfcc,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            dct_type=self.dct_type,
            norm=self.norm,
        )

    def calculate_mfcc_mean(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        计算MFCC均值

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            MFCC均值向量
        """
        mfcc = self.extract_mfcc(y, sr)
        return np.mean(mfcc, axis=1)

    def calculate_mfcc_std(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        计算MFCC标准差

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            MFCC标准差向量
        """
        mfcc = self.extract_mfcc(y, sr)
        return np.std(mfcc, axis=1)

    def calculate_mfcc_delta(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        计算MFCC一阶差分

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            MFCC一阶差分
        """
        mfcc = self.extract_mfcc(y, sr)
        return librosa.feature.delta(mfcc)

    def calculate_mfcc_delta2(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        计算MFCC二阶差分

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            MFCC二阶差分
        """
        mfcc = self.extract_mfcc(y, sr)
        return librosa.feature.delta(mfcc, order=2)

    def calculate_mfcc_statistics(
        self, y: np.ndarray, sr: int
    ) -> Dict[str, np.ndarray]:
        """
        计算MFCC统计特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            MFCC统计特征字典
        """
        mfcc = self.extract_mfcc(y, sr)

        return {
            "mfcc_mean": np.mean(mfcc, axis=1),
            "mfcc_std": np.std(mfcc, axis=1),
            "mfcc_min": np.min(mfcc, axis=1),
            "mfcc_max": np.max(mfcc, axis=1),
            "mfcc_range": np.max(mfcc, axis=1) - np.min(mfcc, axis=1),
        }

    def extract_all_mfcc_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取所有MFCC特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            MFCC特征字典
        """
        # 基础MFCC特征
        mfcc = self.extract_mfcc(y, sr)

        # 统计特征
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_std = np.std(mfcc, axis=1)

        # 差分特征
        mfcc_delta = self.calculate_mfcc_delta(y, sr)
        mfcc_delta2 = self.calculate_mfcc_delta2(y, sr)

        features = {
            "mfcc_mean": mfcc_mean,
            "mfcc_std": mfcc_std,
            "mfcc_delta_mean": np.mean(mfcc_delta, axis=1),
            "mfcc_delta_std": np.std(mfcc_delta, axis=1),
            "mfcc_delta2_mean": np.mean(mfcc_delta2, axis=1),
            "mfcc_delta2_std": np.std(mfcc_delta2, axis=1),
        }

        return features

    def extract_mfcc_for_comparison(
        self, y: np.ndarray, sr: int
    ) -> Dict[str, np.ndarray]:
        """
        提取用于比较的MFCC特征（返回完整特征矩阵）

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            MFCC特征字典（包含完整特征矩阵）
        """
        return {
            "mfcc": self.extract_mfcc(y, sr),
            "mfcc_delta": self.calculate_mfcc_delta(y, sr),
            "mfcc_delta2": self.calculate_mfcc_delta2(y, sr),
        }

    def calculate_mfcc_similarity(
        self, y1: np.ndarray, y2: np.ndarray, sr: int
    ) -> float:
        """
        计算两个音频的MFCC相似度

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据
            sr: 采样率

        Returns:
            MFCC相似度
        """
        try:
            # 提取MFCC特征
            mfcc1 = self.extract_mfcc(y1, sr)
            mfcc2 = self.extract_mfcc(y2, sr)

            # 计算MFCC特征的均值
            mfcc1_mean = np.mean(mfcc1, axis=1)
            mfcc2_mean = np.mean(mfcc2, axis=1)

            # 计算余弦相似度
            dot_product = np.dot(mfcc1_mean, mfcc2_mean)
            norm1 = np.linalg.norm(mfcc1_mean)
            norm2 = np.linalg.norm(mfcc2_mean)

            if norm1 > 0 and norm2 > 0:
                mfcc_sim = dot_product / (norm1 * norm2)
                return float(mfcc_sim)
            else:
                return 0.0
        except Exception:
            return 0.0
