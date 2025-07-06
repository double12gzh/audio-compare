"""
信息显示组件模块
提供音频信息、相似度和图表的显示功能
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List
import plotly.graph_objects as go


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
