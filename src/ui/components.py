"""
UI 组件模块
提供各种可复用的界面组件
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List
import plotly.graph_objects as go
import os
import librosa

from ..utils.config import AppConfig


class SidebarConfig:
    """侧边栏配置组件"""

    def __init__(self, config: AppConfig):
        self.config = config

    def render(self) -> Dict[str, Any]:
        """渲染侧边栏配置"""
        st.sidebar.header("⚙️ 配置参数")

        # 音频参数设置
        st.sidebar.subheader("音频参数")
        sample_rate = st.sidebar.selectbox(
            "采样率", [8000, 16000, 22050, 44100], index=2
        )

        n_mels = st.sidebar.slider("Mel 滤波器组数量", 64, 256, 128)

        # 更新配置
        self.config.audio.default_sample_rate = sample_rate
        self.config.audio.n_mels = n_mels

        return {"sample_rate": sample_rate, "n_mels": n_mels}


class AudioFileSelector:
    """音频文件选择器组件（自动扫描目录）"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.audio_root = getattr(config, "audio_root", "./audio_files")
        self.supported_exts = tuple("." + ext for ext in config.file.supported_formats)

    def _scan_files(self):
        if not os.path.exists(self.audio_root):
            return []
        files = [
            f
            for f in os.listdir(self.audio_root)
            if os.path.isfile(os.path.join(self.audio_root, f))
            and f.lower().endswith(self.supported_exts)
        ]
        return sorted(files)

    def _get_audio_format(self, filename: str) -> str:
        """根据文件扩展名获取音频格式"""
        ext = os.path.splitext(filename)[1].lower()
        format_map = {
            ".wav": "audio/wav",
            ".mp3": "audio/mp3",
            ".flac": "audio/flac",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4",
        }
        return format_map.get(ext, "audio/wav")

    def _get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """获取音频文件的基本信息"""
        try:
            # 文件基本信息
            file_size = os.path.getsize(audio_path)
            file_size_mb = file_size / (1024 * 1024)

            # 音频信息
            y, sr = librosa.load(audio_path, sr=None)  # 不重采样，获取原始采样率
            duration = len(y) / sr

            return {
                "file_size_mb": file_size_mb,
                "duration": duration,
                "sample_rate": sr,
                "channels": 1 if len(y.shape) == 1 else y.shape[1],
                "format": os.path.splitext(audio_path)[1].upper()[1:],  # 去掉点号
            }
        except Exception as e:
            return {
                "file_size_mb": os.path.getsize(audio_path) / (1024 * 1024),
                "duration": "N/A",
                "sample_rate": "N/A",
                "channels": "N/A",
                "format": os.path.splitext(audio_path)[1].upper()[1:],
            }

    def _render_audio_details(
        self, audio_path: str, filename: str, key_prefix: str = ""
    ):
        """渲染音频详细信息（可折叠）"""
        with st.expander(f"📋 {filename} 详细信息", expanded=False):
            info = self._get_audio_info(audio_path)

            # 使用更小的字号显示详细信息
            st.markdown(f"**文件大小:** {info['file_size_mb']:.2f} MB")
            if info["duration"] != "N/A":
                st.markdown(f"**时长:** {info['duration']:.2f} 秒")
            else:
                st.markdown("**时长:** N/A")
            if info["sample_rate"] != "N/A":
                st.markdown(f"**采样率:** {info['sample_rate']} Hz")
            else:
                st.markdown("**采样率:** N/A")
            st.markdown(f"**格式:** {info['format']}")

            # 显示通道信息
            if info["channels"] != "N/A":
                channels_text = (
                    "单声道" if info["channels"] == 1 else f'{info["channels"]} 声道'
                )
                st.markdown(f"**音频通道:** {channels_text}")

    def render_single(self, key: str = "single_audio_file") -> str:
        files = self._scan_files()
        if not files:
            st.warning(f"目录 {self.audio_root} 下没有可用音频文件")
            return None
        selected = st.selectbox("选择音频文件", files, key=key)
        if selected:
            audio_path = os.path.join(self.audio_root, selected)
            # 显示音频播放器
            audio_format = self._get_audio_format(selected)
            st.audio(audio_path, format=audio_format)
            # 显示音频详细信息
            self._render_audio_details(audio_path, selected, key)
            return audio_path
        return None

    def render_dual(
        self, key1: str = "audio1_file", key2: str = "audio2_file"
    ) -> tuple:
        files = self._scan_files()
        if not files:
            st.warning(f"目录 {self.audio_root} 下没有可用音频文件")
            return None, None
        col1, col2 = st.columns(2)
        with col1:
            audio1 = st.selectbox("选择第一个音频文件", files, key=key1)
            if audio1:
                audio_path1 = os.path.join(self.audio_root, audio1)
                audio_format1 = self._get_audio_format(audio1)
                st.audio(audio_path1, format=audio_format1)
                # 显示音频详细信息
                self._render_audio_details(audio_path1, audio1, key1)
        with col2:
            audio2 = st.selectbox("选择第二个音频文件", files, key=key2)
            if audio2:
                audio_path2 = os.path.join(self.audio_root, audio2)
                audio_format2 = self._get_audio_format(audio2)
                st.audio(audio_path2, format=audio_format2)
                # 显示音频详细信息
                self._render_audio_details(audio_path2, audio2, key2)
        path1 = os.path.join(self.audio_root, audio1) if audio1 else None
        path2 = os.path.join(self.audio_root, audio2) if audio2 else None
        return path1, path2

    def render_batch(self, key: str = "batch_audio_files") -> list:
        files = self._scan_files()
        if not files:
            st.warning(f"目录 {self.audio_root} 下没有可用音频文件")
            return []
        selected = st.multiselect("选择多个音频文件", files, key=key)
        if selected:
            st.subheader("音频试听")
            # 为每个选中的文件显示播放器
            for i, file in enumerate(selected):
                audio_path = os.path.join(self.audio_root, file)
                audio_format = self._get_audio_format(file)
                st.write(f"**{file}**")
                st.audio(audio_path, format=audio_format)
                # 显示音频详细信息
                self._render_audio_details(audio_path, file, f"{key}_{i}")
                if i < len(selected) - 1:  # 不是最后一个文件时添加分隔线
                    st.divider()
        return [os.path.join(self.audio_root, f) for f in selected]


class AudioInfoDisplay:
    """音频信息显示组件"""

    @staticmethod
    def render_metrics(audio_info: Dict[str, Any]):
        """渲染音频指标"""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("时长", f"{audio_info.get('duration', 0):.2f}秒")
        with col2:
            st.metric("采样率", f"{audio_info.get('sample_rate', 0)}Hz")
        with col3:
            st.metric("RMS", f"{audio_info.get('rms', 0):.4f}")
        with col4:
            st.metric("零交叉率", f"{audio_info.get('zero_crossing_rate', 0):.4f}")

    @staticmethod
    def render_features_table(features: Dict[str, Any]):
        """渲染特征表格"""
        if not features:
            return

        feature_df = pd.DataFrame(
            [
                ["时长", f"{features.get('duration', 0):.2f}秒"],
                ["RMS", f"{features.get('rms', 0):.4f}"],
                ["零交叉率", f"{features.get('zero_crossing_rate', 0):.4f}"],
                ["频谱质心", f"{features.get('spectral_centroid', 0):.2f}Hz"],
                ["频谱带宽", f"{features.get('spectral_bandwidth', 0):.2f}Hz"],
                ["频谱滚降", f"{features.get('spectral_rolloff', 0):.2f}Hz"],
            ],
            columns=["特征", "值"],
        )

        st.dataframe(feature_df, use_container_width=True)


class SimilarityDisplay:
    """相似度显示组件"""

    @staticmethod
    def render_metrics(similarity: Dict[str, float]):
        """渲染相似度指标"""
        if not similarity:
            return

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("相关系数", f"{similarity.get('correlation', 0):.4f}")
        with col2:
            st.metric("均方误差", f"{similarity.get('mse', 0):.6f}")
        with col3:
            snr_value = similarity.get("snr", 0)
            if snr_value == float("inf"):
                st.metric("信噪比", "∞")
            else:
                st.metric("信噪比", f"{snr_value:.2f}dB")
        with col4:
            st.metric("余弦相似度", f"{similarity.get('cosine_similarity', 0):.4f}")
        with col5:
            st.metric("MFCC相似度", f"{similarity.get('mfcc_similarity', 0):.4f}")

        # 显示对比采样率信息
        if "comparison_sr" in similarity:
            st.info(f"对比采样率: {similarity['comparison_sr']} Hz")


class ChartDisplay:
    """图表显示组件"""

    @staticmethod
    def render_chart(fig: Optional[go.Figure], title: str = ""):
        """渲染图表"""
        if fig is not None:
            # 优化图例配置，避免覆盖
            fig.update_layout(
                legend=dict(
                    orientation="h",  # 水平图例
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor="rgba(255,255,255,0.8)",  # 半透明背景
                    bordercolor="rgba(0,0,0,0.1)",
                    borderwidth=1,
                ),
                margin=dict(t=80, b=40, l=40, r=40),  # 增加顶部边距给图例
            )
            if title:
                st.subheader(title)
            st.plotly_chart(
                fig, use_container_width=True, config={"displayModeBar": False}
            )

    @staticmethod
    def render_charts(charts: List[tuple]):
        """渲染多个图表"""
        for title, fig in charts:
            ChartDisplay.render_chart(fig, title)


class BatchResultsDisplay:
    """批量结果显示组件"""

    @staticmethod
    def render_table(results: List[Dict[str, Any]]):
        """渲染结果表格"""
        if not results:
            st.warning("没有可显示的结果")
            return

        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

    @staticmethod
    def render_export_button(
        results: List[Dict[str, Any]], filename: str = "audio_analysis_results.csv"
    ):
        """渲染导出按钮"""
        if not results:
            return

        df = pd.DataFrame(results)
        csv = df.to_csv(index=False)

        st.download_button(
            label="下载分析结果 (CSV)", data=csv, file_name=filename, mime="text/csv"
        )


class CSSStyler:
    """CSS 样式组件"""

    @staticmethod
    def inject_css():
        """注入自定义CSS样式"""
        st.markdown(
            """
        <style>
            .main-header {
                font-size: 2.5rem;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 2rem;
            }
            .metric-card {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
            }
            .upload-section {
                border: 2px dashed #ccc;
                border-radius: 10px;
                padding: 2rem;
                text-align: center;
                margin: 1rem 0;
            }
            .info-box {
                background-color: #e8f4fd;
                border-left: 4px solid #1f77b4;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0 5px 5px 0;
            }
            .warning-box {
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0 5px 5px 0;
            }
            .error-box {
                background-color: #f8d7da;
                border-left: 4px solid #dc3545;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0 5px 5px 0;
            }
        </style>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def info_box(message: str):
        """显示信息框"""
        st.markdown(f'<div class="info-box">{message}</div>', unsafe_allow_html=True)

    @staticmethod
    def warning_box(message: str):
        """显示警告框"""
        st.markdown(f'<div class="warning-box">{message}</div>', unsafe_allow_html=True)

    @staticmethod
    def error_box(message: str):
        """显示错误框"""
        st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)
