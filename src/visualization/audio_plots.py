"""
音频可视化模块
提供各种音频图表的绘制功能
"""

import librosa
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, Tuple, Dict, Any

from ..utils.config import VisualizationConfig


class AudioVisualizer:
    """音频可视化器"""

    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        初始化可视化器

        Args:
            config: 可视化配置参数
        """
        self.config = config or VisualizationConfig()

    def plot_waveform(
        self, y: np.ndarray, sr: int, title: str = "音频波形"
    ) -> Optional[go.Figure]:
        """
        绘制音频波形图

        Args:
            y: 音频数据
            sr: 采样率
            title: 图表标题

        Returns:
            Plotly 图表对象
        """
        if y is None:
            return None

        time = np.linspace(0, len(y) / sr, len(y))

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=time,
                y=y,
                mode="lines",
                name="波形",
                line=dict(color=self.config.waveform_color, width=1),
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="时间 (秒)",
            yaxis_title="振幅",
            height=self.config.waveform_height,
            showlegend=False,
            margin=dict(t=60, b=40, l=40, r=40),
        )

        return fig

    def plot_mel_spectrogram(
        self, y: np.ndarray, sr: int, title: str = "Mel 频谱图"
    ) -> Optional[go.Figure]:
        """
        绘制 Mel 频谱图

        Args:
            y: 音频数据
            sr: 采样率
            title: 图表标题

        Returns:
            Plotly 图表对象
        """
        if y is None:
            return None

        mel_spect = librosa.feature.melspectrogram(
            y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=128
        )
        mel_spect_db = librosa.power_to_db(mel_spect, ref=np.max)

        fig = go.Figure(
            data=go.Heatmap(
                z=mel_spect_db,
                colorscale=self.config.mel_colorscale,
                x=np.linspace(0, len(y) / sr, mel_spect_db.shape[1]),
                y=np.linspace(0, sr / 2, mel_spect_db.shape[0]),
                colorbar=dict(title="dB"),
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="时间 (秒)",
            yaxis_title="频率 (Hz)",
            height=self.config.spectrogram_height,
            margin=dict(t=60, b=40, l=40, r=40),
        )

        return fig

    def plot_mfcc(
        self, y: np.ndarray, sr: int, title: str = "MFCC 特征"
    ) -> Optional[go.Figure]:
        """
        绘制 MFCC 特征图

        Args:
            y: 音频数据
            sr: 采样率
            title: 图表标题

        Returns:
            Plotly 图表对象
        """
        if y is None:
            return None

        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        fig = go.Figure(
            data=go.Heatmap(
                z=mfcc,
                colorscale=self.config.mfcc_colorscale,
                x=np.linspace(0, len(y) / sr, mfcc.shape[1]),
                y=list(range(mfcc.shape[0])),
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="时间 (秒)",
            yaxis_title="MFCC 系数",
            height=self.config.spectrogram_height,
            margin=dict(t=60, b=40, l=40, r=40),
        )

        return fig

    def plot_comparison_waveform(
        self,
        y1: np.ndarray,
        y2: np.ndarray,
        sr: int,
        title1: str = "音频1",
        title2: str = "音频2",
    ) -> Optional[go.Figure]:
        """
        绘制波形对比图

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据
            sr: 采样率
            title1: 第一个音频标题
            title2: 第二个音频标题

        Returns:
            Plotly 图表对象
        """
        if y1 is None or y2 is None:
            return None

        time1 = np.linspace(0, len(y1) / sr, len(y1))
        time2 = np.linspace(0, len(y2) / sr, len(y2))

        fig = make_subplots(
            rows=2, cols=1, subplot_titles=(title1, title2), vertical_spacing=0.15
        )

        fig.add_trace(
            go.Scatter(
                x=time1,
                y=y1,
                mode="lines",
                name=title1,
                line=dict(color=self.config.comparison_color1),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=time2,
                y=y2,
                mode="lines",
                name=title2,
                line=dict(color=self.config.comparison_color2),
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            title="波形对比",
            height=self.config.comparison_height,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1,
            ),
            margin=dict(t=80, b=40, l=40, r=40),
        )

        fig.update_xaxes(title_text="时间 (秒)", row=1, col=1)
        fig.update_xaxes(title_text="时间 (秒)", row=2, col=1)
        fig.update_yaxes(title_text="振幅", row=1, col=1)
        fig.update_yaxes(title_text="振幅", row=2, col=1)

        # 调整子图标题位置
        fig.update_annotations(dict(font_size=14, font_color="black"))

        return fig

    def plot_comparison_mel(
        self,
        y1: np.ndarray,
        y2: np.ndarray,
        sr: int,
        title1: str = "音频1",
        title2: str = "音频2",
    ) -> Optional[go.Figure]:
        """
        绘制 Mel 频谱对比图

        Args:
            y1: 第一个音频数据
            y2: 第二个音频数据
            sr: 采样率
            title1: 第一个音频标题
            title2: 第二个音频标题

        Returns:
            Plotly 图表对象
        """
        if y1 is None or y2 is None:
            return None

        mel_spect1 = librosa.feature.melspectrogram(
            y=y1, sr=sr, n_fft=2048, hop_length=512, n_mels=128
        )
        mel_spect_db1 = librosa.power_to_db(mel_spect1, ref=np.max)

        mel_spect2 = librosa.feature.melspectrogram(
            y=y2, sr=sr, n_fft=2048, hop_length=512, n_mels=128
        )
        mel_spect_db2 = librosa.power_to_db(mel_spect2, ref=np.max)

        fig = make_subplots(
            rows=2, cols=1, subplot_titles=(title1, title2), vertical_spacing=0.15
        )

        fig.add_trace(
            go.Heatmap(
                z=mel_spect_db1,
                colorscale=self.config.mel_colorscale,
                x=np.linspace(0, len(y1) / sr, mel_spect_db1.shape[1]),
                y=np.linspace(0, sr / 2, mel_spect_db1.shape[0]),
                colorbar=dict(title="dB", x=0.45),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Heatmap(
                z=mel_spect_db2,
                colorscale=self.config.mel_colorscale,
                x=np.linspace(0, len(y2) / sr, mel_spect_db2.shape[1]),
                y=np.linspace(0, sr / 2, mel_spect_db2.shape[0]),
                colorbar=dict(title="dB", x=1.0),
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            title="Mel 频谱对比",
            height=self.config.comparison_height,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1,
            ),
            margin=dict(t=80, b=40, l=40, r=40),
        )

        return fig



    def plot_overlay_waveform(
        self,
        y1: np.ndarray,
        y2: np.ndarray,
        sr: int,
        title1: str = "音频1",
        title2: str = "音频2",
    ) -> Optional[go.Figure]:
        """
        绘制叠加波形对比图
        """
        if y1 is None or y2 is None:
            return None
        min_len = min(len(y1), len(y2))
        y1 = y1[:min_len]
        y2 = y2[:min_len]
        time = np.linspace(0, min_len / sr, min_len)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=time,
                y=y1,
                mode="lines",
                name=title1,
                line=dict(color=self.config.comparison_color1, width=1.5),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=time,
                y=y2,
                mode="lines",
                name=title2,
                line=dict(color=self.config.comparison_color2, width=1.5),
            )
        )
        fig.update_layout(
            title="叠加波形对比",
            xaxis_title="时间 (秒)",
            yaxis_title="振幅",
            height=self.config.waveform_height,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1,
            ),
            margin=dict(t=80, b=40, l=40, r=40),
        )
        return fig



    def plot_comparison_mel_spectral_centroid(
        self,
        y1: np.ndarray,
        y2: np.ndarray,
        sr: int,
        title1: str = "音频1",
        title2: str = "音频2",
    ) -> Optional[go.Figure]:
        """
        绘制 Mel 谱率对比图（上下分图）
        """
        if y1 is None or y2 is None:
            return None
        mel_spect1 = librosa.feature.melspectrogram(
            y=y1, sr=sr, n_fft=2048, hop_length=512, n_mels=128
        )
        spectral_centroid1 = librosa.feature.spectral_centroid(S=mel_spect1, sr=sr)[0]
        mel_spect2 = librosa.feature.melspectrogram(
            y=y2, sr=sr, n_fft=2048, hop_length=512, n_mels=128
        )
        spectral_centroid2 = librosa.feature.spectral_centroid(S=mel_spect2, sr=sr)[0]
        time1 = np.linspace(0, len(y1) / sr, len(spectral_centroid1))
        time2 = np.linspace(0, len(y2) / sr, len(spectral_centroid2))
        fig = make_subplots(
            rows=2, cols=1, subplot_titles=(title1, title2), vertical_spacing=0.15
        )
        fig.add_trace(
            go.Scatter(
                x=time1,
                y=spectral_centroid1,
                mode="lines",
                name=title1,
                line=dict(color=self.config.comparison_color1),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=time2,
                y=spectral_centroid2,
                mode="lines",
                name=title2,
                line=dict(color=self.config.comparison_color2),
            ),
            row=2,
            col=1,
        )
        fig.update_layout(
            title="Mel 谱率对比",
            height=self.config.comparison_height,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1,
            ),
            margin=dict(t=80, b=40, l=40, r=40),
        )
        fig.update_xaxes(title_text="时间 (秒)", row=1, col=1)
        fig.update_xaxes(title_text="时间 (秒)", row=2, col=1)
        fig.update_yaxes(title_text="频率 (Hz)", row=1, col=1)
        fig.update_yaxes(title_text="频率 (Hz)", row=2, col=1)

        # 调整子图标题位置
        fig.update_annotations(dict(font_size=14, font_color="black"))
        return fig

    def plot_overlay_mel_spectral_centroid(
        self,
        y1: np.ndarray,
        y2: np.ndarray,
        sr: int,
        title1: str = "音频1",
        title2: str = "音频2",
    ) -> Optional[go.Figure]:
        """
        绘制叠加 Mel 谱率对比图
        """
        if y1 is None or y2 is None:
            return None
        mel_spect1 = librosa.feature.melspectrogram(
            y=y1, sr=sr, n_fft=2048, hop_length=512, n_mels=128
        )
        spectral_centroid1 = librosa.feature.spectral_centroid(S=mel_spect1, sr=sr)[0]
        mel_spect2 = librosa.feature.melspectrogram(
            y=y2, sr=sr, n_fft=2048, hop_length=512, n_mels=128
        )
        spectral_centroid2 = librosa.feature.spectral_centroid(S=mel_spect2, sr=sr)[0]
        min_len = min(len(spectral_centroid1), len(spectral_centroid2))
        spectral_centroid1 = spectral_centroid1[:min_len]
        spectral_centroid2 = spectral_centroid2[:min_len]
        time = np.linspace(0, min_len * 512 / sr, min_len)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=time,
                y=spectral_centroid1,
                mode="lines",
                name=title1,
                line=dict(color=self.config.comparison_color1, width=2),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=time,
                y=spectral_centroid2,
                mode="lines",
                name=title2,
                line=dict(color=self.config.comparison_color2, width=2),
            )
        )
        fig.update_layout(
            title="叠加 Mel 谱率对比",
            xaxis_title="时间 (秒)",
            yaxis_title="频率 (Hz)",
            height=self.config.waveform_height,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1,
            ),
            margin=dict(t=80, b=40, l=40, r=40),
        )
        return fig

    def plot_comparison_mfcc(
        self,
        y1: np.ndarray,
        y2: np.ndarray,
        sr: int,
        title1: str = "音频1",
        title2: str = "音频2",
    ) -> Optional[go.Figure]:
        """
        绘制 MFCC 对比图
        """
        if y1 is None or y2 is None:
            return None

        # 提取MFCC特征
        mfcc1 = librosa.feature.mfcc(y=y1, sr=sr, n_mfcc=13)
        mfcc2 = librosa.feature.mfcc(y=y2, sr=sr, n_mfcc=13)

        fig = make_subplots(
            rows=2, cols=1, subplot_titles=(title1, title2), vertical_spacing=0.15
        )

        fig.add_trace(
            go.Heatmap(
                z=mfcc1,
                colorscale=self.config.mfcc_colorscale,
                x=np.linspace(0, len(y1) / sr, mfcc1.shape[1]),
                y=list(range(mfcc1.shape[0])),
                colorbar=dict(title="MFCC", x=0.45),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Heatmap(
                z=mfcc2,
                colorscale=self.config.mfcc_colorscale,
                x=np.linspace(0, len(y2) / sr, mfcc2.shape[1]),
                y=list(range(mfcc2.shape[0])),
                colorbar=dict(title="MFCC", x=1.0),
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            title="MFCC 对比",
            height=self.config.comparison_height,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1,
            ),
            margin=dict(t=80, b=40, l=40, r=40),
        )

        return fig
