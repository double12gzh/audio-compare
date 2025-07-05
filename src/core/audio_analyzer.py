"""
音频分析器核心模块
重构后的模块化音频分析器，整合各个功能组件
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, List

from .audio_loader import AudioLoader
from .feature_extractor import FeatureExtractor
from .similarity_calculator import SimilarityCalculator
from ..utils.config import AudioConfig
from ..utils.exceptions import AudioLoadError, FeatureExtractionError


class AudioAnalyzer:
    """音频分析器核心类（重构版）"""

    def __init__(self, config: Optional[AudioConfig] = None):
        """
        初始化音频分析器

        Args:
            config: 音频配置参数
        """
        self.config = config or AudioConfig()
        self._setup_components()

    def _setup_components(self):
        """设置各个组件"""
        self.loader = AudioLoader(self.config)
        self.feature_extractor = FeatureExtractor(self.config)
        self.similarity_calculator = SimilarityCalculator(n_mfcc=self.config.n_mfcc)

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
        return self.loader.load_audio_from_path(audio_path, resample)

    def extract_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取音频特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            特征字典
        """
        return self.feature_extractor.extract_features(y, sr)

    def get_audio_info(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        获取音频基本信息

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            音频信息字典
        """
        return self.feature_extractor.get_audio_info(y, sr)

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
        return self.similarity_calculator.calculate_comprehensive_similarity(
            y1, y2, sr1, sr2
        )

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
                features1 = self.feature_extractor.extract_features_for_comparison(
                    y1, sr1
                )
                features2 = self.feature_extractor.extract_features_for_comparison(
                    y2, sr2
                )
                results["original"] = self.similarity_calculator.compare_features(
                    features1, features2
                )

            # 2. 重采样到统一频率对比
            if sr2 is not None and sr1 != sr2:
                target_sr = max(sr1, sr2)
                y1_resampled, _ = self.loader.resample_audio(y1, sr1, target_sr)
                y2_resampled, _ = self.loader.resample_audio(y2, sr2, target_sr)
                results["resampled"] = self.calculate_similarity(
                    y1_resampled, y2_resampled, target_sr
                )

            return results

        except Exception as e:
            raise FeatureExtractionError(f"多尺度相似度计算失败: {str(e)}")

    def extract_basic_features(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        提取基本特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            基本特征字典
        """
        return self.feature_extractor.extract_basic_features(y, sr)

    def extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取频谱特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            频谱特征字典
        """
        return self.feature_extractor.extract_spectral_features(y, sr)

    def extract_mfcc_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取MFCC特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            MFCC特征字典
        """
        return self.feature_extractor.extract_mfcc_features(y, sr)

    def extract_rhythm_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取节奏特征

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            节奏特征字典
        """
        return self.feature_extractor.extract_rhythm_features(y, sr)

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
        return self.loader.resample_audio(y, orig_sr, target_sr)

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
        return self.loader.normalize_audio_length(y1, y2)

    def calculate_cosine_similarity(self, y1: np.ndarray, y2: np.ndarray) -> float:
        """
        计算余弦相似度

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据

        Returns:
            余弦相似度
        """
        return self.similarity_calculator.calculate_cosine_similarity(y1, y2)

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
        return self.similarity_calculator.calculate_mfcc_similarity(y1, y2, sr)
