"""
音频分析器核心模块
提供音频加载、特征提取、可视化等功能
"""

import librosa
import numpy as np
import tempfile
import os
from typing import Optional, Tuple, Dict, Any, List

from ..utils.config import AudioConfig, VisualizationConfig
from ..utils.exceptions import AudioLoadError, FeatureExtractionError


class AudioAnalyzer:
    """音频分析器核心类"""

    def __init__(self, config: Optional[AudioConfig] = None):
        """
        初始化音频分析器

        Args:
            config: 音频配置参数
        """
        self.config = config or AudioConfig()
        self._setup_parameters()

    def _setup_parameters(self):
        """设置分析参数"""
        self.sample_rate = self.config.default_sample_rate
        self.n_fft = self.config.n_fft
        self.hop_length = self.config.hop_length
        self.n_mels = self.config.n_mels
        self.n_mfcc = self.config.n_mfcc

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
            if not os.path.exists(audio_path):
                raise AudioLoadError(f"文件不存在: {audio_path}")

            # 检查文件扩展名
            file_ext = os.path.splitext(audio_path)[1].lower()
            supported_formats = [".wav", ".mp3", ".flac", ".ogg", ".m4a"]
            if file_ext not in supported_formats:
                raise AudioLoadError(f"不支持的音频格式: {file_ext}")

            # 根据配置决定是否重采样
            target_sr = self.sample_rate if resample else None
            y, sr = librosa.load(audio_path, sr=target_sr)

            return y, sr

        except Exception as e:
            raise AudioLoadError(f"音频加载失败: {str(e)}")

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
            features["duration"] = len(y) / sr
            features["rms"] = np.sqrt(np.mean(y**2))
            features["zero_crossing_rate"] = np.mean(
                librosa.feature.zero_crossing_rate(y)
            )

            # 频谱特征
            features["spectral_centroid"] = np.mean(
                librosa.feature.spectral_centroid(y=y, sr=sr)
            )
            features["spectral_bandwidth"] = np.mean(
                librosa.feature.spectral_bandwidth(y=y, sr=sr)
            )
            features["spectral_rolloff"] = np.mean(
                librosa.feature.spectral_rolloff(y=y, sr=sr)
            )

            # MFCC特征
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
            features["mfcc_mean"] = np.mean(mfcc, axis=1)
            features["mfcc_std"] = np.std(mfcc, axis=1)

            return features

        except Exception as e:
            raise FeatureExtractionError(f"特征提取失败: {str(e)}")

    def get_audio_info(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
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
            "duration": len(y) / sr,
            "sample_rate": sr,
            "rms": np.sqrt(np.mean(y**2)),
            "zero_crossing_rate": np.mean(librosa.feature.zero_crossing_rate(y)),
        }

    def calculate_similarity(
        self, y1: np.ndarray, y2: np.ndarray, sr1: int, sr2: int = None
    ) -> Dict[str, float]:
        """
        计算两个音频的相似度（支持不同采样率）

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据
            sr1: 第一个音频的采样率
            sr2: 第二个音频的采样率（如果不同）

        Returns:
            相似度指标字典
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

            # 计算相关系数
            correlation = np.corrcoef(y1, y2)[0, 1]

            # 计算均方误差
            mse = np.mean((y1 - y2) ** 2)

            # 计算信噪比
            signal_power = np.mean(y1**2)
            noise_power = np.mean((y1 - y2) ** 2)
            snr = (
                10 * np.log10(signal_power / noise_power)
                if noise_power > 0
                else float("inf")
            )

            # 计算余弦相似度
            cosine_similarity = self._calculate_cosine_similarity(y1, y2)

            # 计算MFCC相似度
            mfcc_similarity = self._calculate_mfcc_similarity(y1, y2, sr)

            return {
                "correlation": correlation,
                "mse": mse,
                "snr": snr,
                "cosine_similarity": cosine_similarity,
                "mfcc_similarity": mfcc_similarity,
                "comparison_sr": sr,  # 记录对比使用的采样率
            }

        except Exception as e:
            raise FeatureExtractionError(f"相似度计算失败: {str(e)}")

    def _calculate_cosine_similarity(self, y1: np.ndarray, y2: np.ndarray) -> float:
        """计算余弦相似度"""
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

    def _calculate_mfcc_similarity(
        self, y1: np.ndarray, y2: np.ndarray, sr: int
    ) -> float:
        """计算MFCC特征相似度"""
        try:
            # 提取MFCC特征
            mfcc1 = librosa.feature.mfcc(y=y1, sr=sr, n_mfcc=self.n_mfcc)
            mfcc2 = librosa.feature.mfcc(y=y2, sr=sr, n_mfcc=self.n_mfcc)

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

    def calculate_multi_scale_similarity(
        self, y1: np.ndarray, y2: np.ndarray, sr1: int, sr2: int = None
    ) -> Dict[str, Dict[str, float]]:
        """
        多尺度相似度对比（保持原始采样率和重采样对比）

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据
            sr1: 第一个音频的采样率
            sr2: 第二个音频的采样率

        Returns:
            多尺度相似度结果
        """
        results = {}

        try:
            # 1. 原始采样率对比（如果不同，则分别分析）
            if sr2 is None or sr1 == sr2:
                results["original"] = self.calculate_similarity(y1, y2, sr1)
            else:
                # 分别计算每个音频的特征
                features1 = self._extract_audio_features(y1, sr1)
                features2 = self._extract_audio_features(y2, sr2)
                results["original"] = self._compare_features(features1, features2)

            # 2. 重采样到统一频率对比
            if sr2 is not None and sr1 != sr2:
                target_sr = max(sr1, sr2)
                y1_resampled = librosa.resample(y1, orig_sr=sr1, target_sr=target_sr)
                y2_resampled = librosa.resample(y2, orig_sr=sr2, target_sr=target_sr)
                results["resampled"] = self.calculate_similarity(
                    y1_resampled, y2_resampled, target_sr
                )

            return results

        except Exception as e:
            raise FeatureExtractionError(f"多尺度相似度计算失败: {str(e)}")

    def _extract_audio_features(self, y: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """提取音频特征"""
        features = {}

        # 频谱特征
        features["spectral_centroid"] = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        features["spectral_bandwidth"] = librosa.feature.spectral_bandwidth(y=y, sr=sr)[
            0
        ]
        features["spectral_rolloff"] = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

        # MFCC特征
        features["mfcc"] = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)

        # 节奏特征
        features["tempo"] = librosa.beat.tempo(y=y, sr=sr)

        return features

    def _compare_features(
        self, features1: Dict[str, np.ndarray], features2: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """比较两个音频的特征"""
        similarities = {}

        for feature_name in features1.keys():
            if feature_name in features2:
                f1 = features1[feature_name].flatten()
                f2 = features2[feature_name].flatten()

                # 确保长度一致
                min_len = min(len(f1), len(f2))
                f1 = f1[:min_len]
                f2 = f2[:min_len]

                similarities[f"{feature_name}_similarity"] = (
                    self._calculate_cosine_similarity(f1, f2)
                )

        return similarities


