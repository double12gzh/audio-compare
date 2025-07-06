"""
自定义异常类
"""


class AudioAnalysisError(Exception):
    """音频分析基础异常"""

    pass


class AudioLoadError(AudioAnalysisError):
    """音频加载异常"""

    pass


class FeatureExtractionError(AudioAnalysisError):
    """特征提取异常"""

    pass
