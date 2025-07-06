"""
音频对比分析页面
"""

import streamlit as st
import os
import tempfile
from typing import Dict

from .base_page import BasePage
from .. import SimilarityDisplay, ChartDisplay, CSSStyler
from ...utils.exceptions import AudioAnalysisError


class ComparisonPage(BasePage):
    """音频对比分析页面"""

    def render(self):
        """渲染音频对比分析页面"""
        st.header("音频对比分析")

        # 选择输入方式
        input_method = st.radio("选择输入方式", ["文件选择器", "路径输入", "文件上传"], horizontal=True)

        if input_method == "文件选择器":
            audio1_path, audio2_path = self.file_selector.render_dual()
        elif input_method == "路径输入":
            audio1_path, audio2_path = self._render_path_input()
        else:
            audio1_path, audio2_path = self._render_file_upload()

        if audio1_path is not None and audio2_path is not None:
            # 显示音频文件信息
            st.subheader("选择的音频文件")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**音频1:** {os.path.basename(audio1_path)}")
                st.write(f"路径: {audio1_path}")
            with col2:
                st.write(f"**音频2:** {os.path.basename(audio2_path)}")
                st.write(f"路径: {audio2_path}")

            # 开始对比按钮
            if st.button("开始对比", type="primary", key="start_comparison"):
                self._perform_comparison(audio1_path, audio2_path)
        else:
            st.info('请点击"开始对比"按钮开始音频对比分析')

    def _render_path_input(self):
        """渲染路径输入方式"""
        from ...utils.config import scan_audio_files_in_dir

        # 初始化session_state
        if "audio1_path" not in st.session_state:
            st.session_state.audio1_path = "./audio_files/audio1.wav"
        if "audio2_path" not in st.session_state:
            st.session_state.audio2_path = "./audio_files/audio2.wav"

        col1, col2 = st.columns(2)
        with col1:
            audio1_path = st.text_input(
                "音频1路径", value=st.session_state.audio1_path, key="audio1_input"
            )
        with col2:
            audio2_path = st.text_input(
                "音频2路径", value=st.session_state.audio2_path, key="audio2_input"
            )

        # 显示可用的音频文件
        if st.checkbox("显示可用音频文件", key="show_available_files"):
            available_files = scan_audio_files_in_dir("./audio_files")
            if available_files:
                st.write("**可用的音频文件:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**音频1选择:**")
                    for file in available_files:
                        if st.button(f"选择: {file}", key=f"select1_{file}"):
                            st.session_state.audio1_path = f"./audio_files/{file}"
                            st.rerun()
                with col2:
                    st.write("**音频2选择:**")
                    for file in available_files:
                        if st.button(f"选择: {file}", key=f"select2_{file}"):
                            st.session_state.audio2_path = f"./audio_files/{file}"
                            st.rerun()
            else:
                st.warning("未找到音频文件")

        # 使用session_state中的路径
        return st.session_state.audio1_path, st.session_state.audio2_path

    def _render_file_upload(self):
        """渲染文件上传方式"""
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file1 = st.file_uploader(
                "上传音频1",
                type=["wav", "mp3", "flac", "ogg", "m4a"],
                key="upload1",
            )
        with col2:
            uploaded_file2 = st.file_uploader(
                "上传音频2",
                type=["wav", "mp3", "flac", "ogg", "m4a"],
                key="upload2",
            )

        # 处理上传的文件
        if uploaded_file1 and uploaded_file2:
            # 保存上传的文件到临时目录
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{uploaded_file1.name.split('.')[-1]}"
            ) as tmp_file1:
                tmp_file1.write(uploaded_file1.getvalue())
                audio1_path = tmp_file1.name

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{uploaded_file2.name.split('.')[-1]}"
            ) as tmp_file2:
                tmp_file2.write(uploaded_file2.getvalue())
                audio2_path = tmp_file2.name
        else:
            audio1_path = None
            audio2_path = None

        # 检查文件是否存在
        if audio1_path and audio2_path:
            if not os.path.exists(audio1_path):
                st.error(f"音频1文件不存在: {audio1_path}")
                audio1_path = None
            if not os.path.exists(audio2_path):
                st.error(f"音频2文件不存在: {audio2_path}")
                audio2_path = None

        return audio1_path, audio2_path

    def _perform_comparison(self, audio1_path: str, audio2_path: str):
        """执行音频对比分析"""
        try:
            y1, sr1 = self.analyzer.load_audio_from_path(audio1_path)
            y2, sr2 = self.analyzer.load_audio_from_path(audio2_path)
            if y1 is not None and y2 is not None:
                # 检查采样率是否不同
                use_multi_scale = sr2 is not None and sr1 != sr2

                if use_multi_scale:
                    st.info(f"检测到不同采样率: 音频1 ({sr1} Hz) vs 音频2 ({sr2} Hz)")

                    # 选择对比模式
                    comparison_mode = st.selectbox(
                        "选择对比模式",
                        ["标准对比", "多尺度对比"],
                        help="标准对比：重采样到统一频率后对比；多尺度对比：同时显示原始特征对比和重采样对比",
                    )

                    if comparison_mode == "多尺度对比":
                        multi_scale_results = (
                            self.analyzer.calculate_multi_scale_similarity(
                                y1, y2, sr1, sr2
                            )
                        )

                        # 显示原始特征对比
                        if "original" in multi_scale_results:
                            st.subheader("原始特征对比")
                            self._render_feature_similarities(
                                multi_scale_results["original"]
                            )

                        # 显示重采样对比
                        if "resampled" in multi_scale_results:
                            st.subheader("重采样对比")
                            SimilarityDisplay.render_metrics(
                                multi_scale_results["resampled"]
                            )
                    else:
                        similarity = self.analyzer.calculate_similarity(
                            y1, y2, sr1, sr2
                        )
                        if similarity:
                            st.subheader("相似度分析")
                            SimilarityDisplay.render_metrics(similarity)
                else:
                    similarity = self.analyzer.calculate_similarity(y1, y2, sr1, sr2)
                    if similarity:
                        st.subheader("相似度分析")
                        SimilarityDisplay.render_metrics(similarity)

                self._render_comparison_visualizations(
                    y1, y2, sr1, audio1_path, audio2_path
                )
            else:
                st.error("无法加载音频文件，请检查文件路径是否正确")
        except AudioAnalysisError as e:
            CSSStyler.error_box(f"分析错误: {str(e)}")
        except Exception as e:
            CSSStyler.error_box(f"未知错误: {str(e)}")

    def _render_comparison_visualizations(
        self, y1, y2, sr1, audio1_path: str, audio2_path: str
    ):
        """渲染对比可视化图表"""
        audio1_name = os.path.basename(audio1_path)
        audio2_name = os.path.basename(audio2_path)

        tab_wave, tab_mel, tab_mel_centroid, tab_mfcc = st.tabs(
            ["波形对比", "Mel 频谱对比", "Mel 谱率对比", "MFCC 对比"]
        )

        with tab_wave:
            overlay_wave_fig = self.visualizer.plot_overlay_waveform(
                y1,
                y2,
                sr1,
                title1=f"音频1 ({audio1_name})",
                title2=f"音频2 ({audio2_name})",
            )
            ChartDisplay.render_chart(overlay_wave_fig, "叠加波形对比")

            waveform_comp_fig = self.visualizer.plot_comparison_waveform(
                y1,
                y2,
                sr1,
                title1=f"音频1 ({audio1_name})",
                title2=f"音频2 ({audio2_name})",
            )
            ChartDisplay.render_chart(waveform_comp_fig, "波形对比")

        with tab_mel:
            mel_comp_fig = self.visualizer.plot_comparison_mel(
                y1,
                y2,
                sr1,
                title1=f"音频1 ({audio1_name})",
                title2=f"音频2 ({audio2_name})",
            )
            ChartDisplay.render_chart(mel_comp_fig, "Mel 频谱对比")

        with tab_mel_centroid:
            overlay_centroid_fig = self.visualizer.plot_overlay_mel_spectral_centroid(
                y1,
                y2,
                sr1,
                title1=f"音频1 ({audio1_name})",
                title2=f"音频2 ({audio2_name})",
            )
            ChartDisplay.render_chart(overlay_centroid_fig, "叠加 Mel 谱率对比")

            mel_centroid_fig = self.visualizer.plot_comparison_mel_spectral_centroid(
                y1,
                y2,
                sr1,
                title1=f"音频1 ({audio1_name})",
                title2=f"音频2 ({audio2_name})",
            )
            ChartDisplay.render_chart(mel_centroid_fig, "Mel 谱率对比")

        with tab_mfcc:
            mfcc_comp_fig = self.visualizer.plot_comparison_mfcc(
                y1,
                y2,
                sr1,
                title1=f"音频1 ({audio1_name})",
                title2=f"音频2 ({audio2_name})",
            )
            ChartDisplay.render_chart(mfcc_comp_fig, "MFCC 对比")

    def _render_feature_similarities(self, similarities: Dict[str, float]):
        """渲染特征相似度"""
        if not similarities:
            return

        # 按特征类型分组显示
        spectral_features = {k: v for k, v in similarities.items() if "spectral" in k}
        mfcc_features = {k: v for k, v in similarities.items() if "mfcc" in k}
        tempo_features = {k: v for k, v in similarities.items() if "tempo" in k}

        if spectral_features:
            st.write("**频谱特征相似度:**")
            for feature, value in spectral_features.items():
                feature_name = (
                    feature.replace("_similarity", "").replace("_", " ").title()
                )
                st.write(f"- {feature_name}: {value:.4f}")

        if mfcc_features:
            st.write("**MFCC特征相似度:**")
            for feature, value in mfcc_features.items():
                feature_name = (
                    feature.replace("_similarity", "").replace("_", " ").title()
                )
                st.write(f"- {feature_name}: {value:.4f}")

        if tempo_features:
            st.write("**节奏特征相似度:**")
            for feature, value in tempo_features.items():
                feature_name = (
                    feature.replace("_similarity", "").replace("_", " ").title()
                )
                st.write(f"- {feature_name}: {value:.4f}")
