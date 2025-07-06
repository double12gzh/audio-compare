"""
相似度计算模块
包含各种音频相似度计算方法
"""

import numpy as np
import librosa
from typing import Dict, Any, Optional

from .mfcc_metrics import MFCCMetrics
from ..utils.exceptions import FeatureExtractionError


class SimilarityCalculator:
    """相似度计算器类"""

    def __init__(self, n_mfcc: int = 13):
        """
        初始化相似度计算器

        Args:
            n_mfcc: MFCC系数数量
        """
        self.mfcc_calculator = MFCCMetrics(n_mfcc=n_mfcc)

    def calculate_cosine_similarity(self, y1: np.ndarray, y2: np.ndarray) -> float:
        """
        计算余弦相似度

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据

        Returns:
            余弦相似度
        """
        try:
            # 计算向量的点积
            dot_product = np.dot(y1, y2)
            # 计算向量的模长
            norm1 = np.linalg.norm(y1)
            norm2 = np.linalg.norm(y2)
            # 计算余弦相似度
            if norm1 > 0 and norm2 > 0:
                cosine_sim = dot_product / (norm1 * norm2)
                return float(cosine_sim)
            else:
                return 0.0
        except Exception:
            return 0.0

    def calculate_correlation(self, y1: np.ndarray, y2: np.ndarray) -> float:
        """
        计算相关系数

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据

        Returns:
            相关系数
        """
        try:
            correlation = np.corrcoef(y1, y2)[0, 1]
            return float(correlation) if not np.isnan(correlation) else 0.0
        except Exception:
            return 0.0

    def calculate_mse(self, y1: np.ndarray, y2: np.ndarray) -> float:
        """
        计算均方误差

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据

        Returns:
            均方误差
        """
        try:
            return float(np.mean((y1 - y2) ** 2))
        except Exception:
            return float("inf")

    def calculate_snr(self, y1: np.ndarray, y2: np.ndarray) -> float:
        """
        计算信噪比

        Args:
            y1: 第一个音频数据（信号）
            y2: 第二个音频数据（噪声）

        Returns:
            信噪比（dB）
        """
        try:
            signal_power = np.mean(y1**2)
            noise_power = np.mean((y1 - y2) ** 2)
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                return float(snr)
            else:
                return float("inf")
        except Exception:
            return float("inf")

    def calculate_mfcc_similarity(
        self, y1: np.ndarray, y2: np.ndarray, sr: int
    ) -> float:
        """
        计算MFCC相似度

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据
            sr: 采样率

        Returns:
            MFCC相似度
        """
        return self.mfcc_calculator.calculate_mfcc_similarity(y1, y2, sr)

    def calculate_spectral_similarity(
        self, y1: np.ndarray, y2: np.ndarray, sr: int
    ) -> float:
        """
        计算频谱相似度

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据
            sr: 采样率

        Returns:
            频谱相似度
        """
        try:
            # 计算频谱质心
            centroid1 = librosa.feature.spectral_centroid(y=y1, sr=sr)
            centroid2 = librosa.feature.spectral_centroid(y=y2, sr=sr)

            # 计算频谱带宽
            bandwidth1 = librosa.feature.spectral_bandwidth(y=y1, sr=sr)
            bandwidth2 = librosa.feature.spectral_bandwidth(y=y2, sr=sr)

            # 计算频谱滚降
            rolloff1 = librosa.feature.spectral_rolloff(y=y1, sr=sr)
            rolloff2 = librosa.feature.spectral_rolloff(y=y2, sr=sr)

            # 计算各特征的相似度
            centroid_sim = self.calculate_cosine_similarity(
                np.mean(centroid1, axis=1), np.mean(centroid2, axis=1)
            )
            bandwidth_sim = self.calculate_cosine_similarity(
                np.mean(bandwidth1, axis=1), np.mean(bandwidth2, axis=1)
            )
            rolloff_sim = self.calculate_cosine_similarity(
                np.mean(rolloff1, axis=1), np.mean(rolloff2, axis=1)
            )

            # 返回平均相似度
            return (centroid_sim + bandwidth_sim + rolloff_sim) / 3.0

        except Exception:
            return 0.0

    def calculate_comprehensive_similarity(
        self, y1: np.ndarray, y2: np.ndarray, sr1: int, sr2: int = None
    ) -> Dict[str, float]:
        """
        计算综合相似度（包含多种指标）

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据
            sr1: 第一个音频的采样率
            sr2: 第二个音频的采样率（如果不同）

        Returns:
            综合相似度指标字典
        """
        if y1 is None or y2 is None:
            return {}

        try:
            # 如果采样率不同，重采样到统一频率
            if sr2 is not None and sr1 != sr2:
                # 选择较高的采样率作为目标
                target_sr = max(sr1, sr2)
                if sr1 != target_sr:
                    y1 = librosa.resample(y1, orig_sr=sr1, target_sr=target_sr)
                if sr2 != target_sr:
                    y2 = librosa.resample(y2, orig_sr=sr2, target_sr=target_sr)
                sr = target_sr
            else:
                sr = sr1

            # 确保两个音频长度一致
            min_len = min(len(y1), len(y2))
            y1 = y1[:min_len]
            y2 = y2[:min_len]

            # 计算各种相似度指标
            correlation = self.calculate_correlation(y1, y2)
            mse = self.calculate_mse(y1, y2)
            snr = self.calculate_snr(y1, y2)
            cosine_similarity = self.calculate_cosine_similarity(y1, y2)
            mfcc_similarity = self.calculate_mfcc_similarity(y1, y2, sr)
            spectral_similarity = self.calculate_spectral_similarity(y1, y2, sr)

            return {
                "correlation": correlation,
                "mse": mse,
                "snr": snr,
                "cosine_similarity": cosine_similarity,
                "mfcc_similarity": mfcc_similarity,
                "spectral_similarity": spectral_similarity,
                "comparison_sr": sr,  # 记录对比使用的采样率
            }

        except Exception as e:
            raise FeatureExtractionError(f"相似度计算失败: {str(e)}")

    def compare_features(
        self, features1: Dict[str, np.ndarray], features2: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        比较两个音频的特征

        Args:
            features1: 第一个音频的特征
            features2: 第二个音频的特征

        Returns:
            特征相似度字典
        """
        similarities = {}

        for feature_name in features1.keys():
            if feature_name in features2:
                f1 = features1[feature_name].flatten()
                f2 = features2[feature_name].flatten()

                # 确保长度一致
                min_len = min(len(f1), len(f2))
                f1 = f1[:min_len]
                f2 = f2[:min_len]

                similarities[
                    f"{feature_name}_similarity"
                ] = self.calculate_cosine_similarity(f1, f2)

        return similarities
