"""
配置管理模块
使用数据类来管理各种配置参数
"""

import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple

AUDIO_ROOT = "./audio_files"


@dataclass
class AudioConfig:
    """音频处理配置"""

    default_sample_rate: int = 22050
    n_fft: int = 2048
    hop_length: int = 512
    win_length: int = 2048
    n_mels: int = 128
    fmin: int = 0
    fmax: Optional[int] = None
    n_mfcc: int = 13
    dct_type: int = 2
    norm: str = "ortho"
    spectral_rolloff_percentile: float = 0.85


@dataclass
class VisualizationConfig:
    """可视化配置"""

    waveform_height: int = 400
    spectrogram_height: int = 400
    comparison_height: int = 600
    waveform_color: str = "#1f77b4"
    comparison_color1: str = "#1f77b4"
    comparison_color2: str = "#ff7f0e"
    mel_colorscale: str = "Viridis"
    mfcc_colorscale: str = "RdBu"
    title_font_size: int = 16
    axis_font_size: int = 12


@dataclass
class SimilarityConfig:
    """相似度计算配置"""

    correlation_threshold: float = 0.8
    mse_threshold: float = 0.01
    snr_threshold: float = 20.0


@dataclass
class FileConfig:
    """文件处理配置"""

    supported_formats: List[str] = None
    max_file_size: int = 100  # MB
    max_batch_files: int = 50
    temp_dir: Optional[str] = None

    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ["wav", "mp3", "flac", "ogg", "m4a"]


@dataclass
class UIConfig:
    """界面配置"""

    page_title: str = "TTS 音频验收工具"
    page_icon: str = "🎵"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    theme: Dict[str, str] = None

    def __post_init__(self):
        if self.theme is None:
            self.theme = {
                "primaryColor": "#1f77b4",
                "backgroundColor": "#ffffff",
                "secondaryBackgroundColor": "#f0f2f6",
                "textColor": "#262730",
            }


@dataclass
class FeatureConfig:
    """特征配置"""

    basic_features: List[str] = None
    spectral_features: List[str] = None
    mfcc_features: List[str] = None
    rhythm_features: List[str] = None

    def __post_init__(self):
        if self.basic_features is None:
            self.basic_features = ["duration", "rms", "zero_crossing_rate"]
        if self.spectral_features is None:
            self.spectral_features = [
                "spectral_centroid",
                "spectral_bandwidth",
                "spectral_rolloff",
                "spectral_contrast",
                "spectral_flatness",
            ]
        if self.mfcc_features is None:
            self.mfcc_features = ["mfcc_mean", "mfcc_std", "mfcc_delta", "mfcc_delta2"]
        if self.rhythm_features is None:
            self.rhythm_features = ["tempo", "beat_frames", "onset_strength"]


@dataclass
class ExportConfig:
    """导出配置"""

    csv_encoding: str = "utf-8"
    csv_separator: str = ","
    chart_format: str = "png"
    chart_scale: int = 2
    report_template: str = "html"


@dataclass
class AppConfig:
    """应用总配置"""

    audio: AudioConfig = None
    visualization: VisualizationConfig = None
    similarity: SimilarityConfig = None
    file: FileConfig = None
    ui: UIConfig = None
    feature: FeatureConfig = None
    export: ExportConfig = None
    audio_root: str = AUDIO_ROOT

    def __post_init__(self):
        if self.audio is None:
            self.audio = AudioConfig()
        if self.visualization is None:
            self.visualization = VisualizationConfig()
        if self.similarity is None:
            self.similarity = SimilarityConfig()
        if self.file is None:
            self.file = FileConfig()
        if self.ui is None:
            self.ui = UIConfig()
        if self.feature is None:
            self.feature = FeatureConfig()
        if self.export is None:
            self.export = ExportConfig()
        if not hasattr(self, "audio_root") or self.audio_root is None:
            self.audio_root = AUDIO_ROOT

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AppConfig":
        """从字典创建配置对象"""
        return cls(
            audio=AudioConfig(**config_dict.get("audio", {})),
            visualization=VisualizationConfig(**config_dict.get("visualization", {})),
            similarity=SimilarityConfig(**config_dict.get("similarity", {})),
            file=FileConfig(**config_dict.get("file", {})),
            ui=UIConfig(**config_dict.get("ui", {})),
            feature=FeatureConfig(**config_dict.get("feature", {})),
            export=ExportConfig(**config_dict.get("export", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "audio": self.audio.__dict__,
            "visualization": self.visualization.__dict__,
            "similarity": self.similarity.__dict__,
            "file": self.file.__dict__,
            "ui": self.ui.__dict__,
            "feature": self.feature.__dict__,
            "export": self.export.__dict__,
        }


def scan_audio_files_in_dir(
    directory: str, exts=(".wav", ".mp3", ".flac", ".ogg", ".m4a")
) -> List[str]:
    """
    扫描目录下所有音频文件，返回文件名列表（不含路径）
    """
    if not os.path.isdir(directory):
        return []
    files = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in exts]
    return files


def find_matching_files(dir_a: str, dir_b: str) -> List[Tuple[str, str, str]]:
    """
    找到两个目录下同名音频文件，返回[(文件名, 路径A, 路径B)]
    """
    files_a = set(scan_audio_files_in_dir(dir_a))
    files_b = set(scan_audio_files_in_dir(dir_b))
    common = files_a & files_b
    return [
        (fname, os.path.join(dir_a, fname), os.path.join(dir_b, fname))
        for fname in sorted(common)
    ]
