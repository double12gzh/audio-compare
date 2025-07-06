"""
单音频分析页面
"""

import streamlit as st
from typing import Optional

from .base_page import BasePage
from .. import AudioInfoDisplay, ChartDisplay, CSSStyler
from ...utils.exceptions import AudioAnalysisError


class SingleAudioPage(BasePage):
    """单音频分析页面"""

    def render(self):
        """渲染单音频分析页面"""
        st.header("单音频分析")

        # 文件路径输入
        audio_path = self.file_selector.render_single()

        if audio_path is not None:
            try:
                # 加载音频
                y, sr = self.analyzer.load_audio_from_path(audio_path)

                if y is not None:
                    # 显示音频信息
                    audio_info = self.analyzer.get_audio_info(y, sr)
                    AudioInfoDisplay.render_metrics(audio_info)

                    # 提取特征
                    features = self.analyzer.extract_features(y, sr)

                    if features:
                        # 显示特征表格
                        st.subheader("音频特征")
                        AudioInfoDisplay.render_features_table(features)

                    # 绘制波形图
                    waveform_fig = self.visualizer.plot_waveform(y, sr)
                    ChartDisplay.render_chart(waveform_fig, "音频波形")

                    # 绘制 Mel 频谱图
                    mel_fig = self.visualizer.plot_mel_spectrogram(y, sr)
                    ChartDisplay.render_chart(mel_fig, "Mel 频谱图")

                    # MFCC 特征
                    mfcc_fig = self.visualizer.plot_mfcc(y, sr)
                    ChartDisplay.render_chart(mfcc_fig, "MFCC 特征")

            except AudioAnalysisError as e:
                CSSStyler.error_box(f"分析错误: {str(e)}")
            except Exception as e:
                CSSStyler.error_box(f"未知错误: {str(e)}")
