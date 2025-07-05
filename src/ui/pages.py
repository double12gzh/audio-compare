"""
页面模块
提供不同功能的页面组件
"""

import streamlit as st
import os
from typing import Optional, Dict, Any, List

from ..core.audio_analyzer import AudioAnalyzer
from ..visualization.audio_plots import AudioVisualizer
from ..ui.components import (
    AudioFileSelector, AudioInfoDisplay, SimilarityDisplay, 
    ChartDisplay, BatchResultsDisplay, CSSStyler
)
from ..utils.config import AppConfig
from ..utils.exceptions import AudioAnalysisError


class SingleAudioPage:
    """单音频分析页面"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.analyzer = AudioAnalyzer(config.audio)
        self.visualizer = AudioVisualizer(config.visualization)
        self.file_selector = AudioFileSelector(config)
    
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


class ComparisonPage:
    """音频对比分析页面"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.analyzer = AudioAnalyzer(config.audio)
        self.visualizer = AudioVisualizer(config.visualization)
        self.file_selector = AudioFileSelector(config)
    
    def render(self):
        """渲染音频对比分析页面"""
        st.header("音频对比分析")
        
        # 选择输入方式
        input_method = st.radio(
            "选择输入方式",
            ["文件选择器", "路径输入", "文件上传"],
            horizontal=True
        )
        
        if input_method == "文件选择器":
            audio1_path, audio2_path = self.file_selector.render_dual()
        elif input_method == "路径输入":
            # 路径输入方式
            from src.utils.config import scan_audio_files_in_dir
            
            # 初始化session_state
            if "audio1_path" not in st.session_state:
                st.session_state.audio1_path = "./audio_files/audio1.wav"
            if "audio2_path" not in st.session_state:
                st.session_state.audio2_path = "./audio_files/audio2.wav"
            
            col1, col2 = st.columns(2)
            with col1:
                audio1_path = st.text_input("音频1路径", value=st.session_state.audio1_path, key="audio1_input")
            with col2:
                audio2_path = st.text_input("音频2路径", value=st.session_state.audio2_path, key="audio2_input")
            
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
            audio1_path = st.session_state.audio1_path
            audio2_path = st.session_state.audio2_path
        else:
            # 文件上传方式
            col1, col2 = st.columns(2)
            with col1:
                uploaded_file1 = st.file_uploader("上传音频1", type=['wav', 'mp3', 'flac', 'ogg', 'm4a'], key="upload1")
            with col2:
                uploaded_file2 = st.file_uploader("上传音频2", type=['wav', 'mp3', 'flac', 'ogg', 'm4a'], key="upload2")
            
            # 处理上传的文件
            if uploaded_file1 and uploaded_file2:
                # 保存上传的文件到临时目录
                import tempfile
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file1.name.split('.')[-1]}") as tmp_file1:
                    tmp_file1.write(uploaded_file1.getvalue())
                    audio1_path = tmp_file1.name
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file2.name.split('.')[-1]}") as tmp_file2:
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
                                help="标准对比：重采样到统一频率后对比；多尺度对比：同时显示原始特征对比和重采样对比"
                            )
                            
                            if comparison_mode == "多尺度对比":
                                multi_scale_results = self.analyzer.calculate_multi_scale_similarity(y1, y2, sr1, sr2)
                                
                                # 显示原始特征对比
                                if 'original' in multi_scale_results:
                                    st.subheader("原始特征对比")
                                    self._render_feature_similarities(multi_scale_results['original'])
                                
                                # 显示重采样对比
                                if 'resampled' in multi_scale_results:
                                    st.subheader("重采样对比")
                                    SimilarityDisplay.render_metrics(multi_scale_results['resampled'])
                            else:
                                similarity = self.analyzer.calculate_similarity(y1, y2, sr1, sr2)
                                if similarity:
                                    st.subheader("相似度分析")
                                    SimilarityDisplay.render_metrics(similarity)
                        else:
                            similarity = self.analyzer.calculate_similarity(y1, y2, sr1, sr2)
                            if similarity:
                                st.subheader("相似度分析")
                                SimilarityDisplay.render_metrics(similarity)
                        
                        audio1_name = os.path.basename(audio1_path)
                        audio2_name = os.path.basename(audio2_path)
                        tab_wave, tab_mel, tab_mel_centroid, tab_mfcc = st.tabs([
                            "波形对比", "Mel 频谱对比", "Mel 谱率对比", "MFCC 对比"
                        ])
                        with tab_wave:
                            overlay_wave_fig = self.visualizer.plot_overlay_waveform(
                                y1, y2, sr1,
                                title1=f"音频1 ({audio1_name})",
                                title2=f"音频2 ({audio2_name})"
                            )
                            ChartDisplay.render_chart(overlay_wave_fig, "叠加波形对比")
                            
                            waveform_comp_fig = self.visualizer.plot_comparison_waveform(
                                y1, y2, sr1, 
                                title1=f"音频1 ({audio1_name})",
                                title2=f"音频2 ({audio2_name})"
                            )
                            ChartDisplay.render_chart(waveform_comp_fig, "波形对比")
                        with tab_mel:
                            mel_comp_fig = self.visualizer.plot_comparison_mel(
                                y1, y2, sr1,
                                title1=f"音频1 ({audio1_name})",
                                title2=f"音频2 ({audio2_name})"
                            )
                            ChartDisplay.render_chart(mel_comp_fig, "Mel 频谱对比")
                        with tab_mel_centroid:
                            overlay_centroid_fig = self.visualizer.plot_overlay_mel_spectral_centroid(
                                y1, y2, sr1,
                                title1=f"音频1 ({audio1_name})",
                                title2=f"音频2 ({audio2_name})"
                            )
                            ChartDisplay.render_chart(overlay_centroid_fig, "叠加 Mel 谱率对比")
                            
                            mel_centroid_fig = self.visualizer.plot_comparison_mel_spectral_centroid(
                                y1, y2, sr1,
                                title1=f"音频1 ({audio1_name})",
                                title2=f"音频2 ({audio2_name})"
                            )
                            ChartDisplay.render_chart(mel_centroid_fig, "Mel 谱率对比")
                        
                        with tab_mfcc:
                            mfcc_comp_fig = self.visualizer.plot_comparison_mfcc(
                                y1, y2, sr1,
                                title1=f"音频1 ({audio1_name})",
                                title2=f"音频2 ({audio2_name})"
                            )
                            ChartDisplay.render_chart(mfcc_comp_fig, "MFCC 对比")
                    else:
                        st.error("无法加载音频文件，请检查文件路径是否正确")
                except AudioAnalysisError as e:
                    CSSStyler.error_box(f"分析错误: {str(e)}")
                except Exception as e:
                    CSSStyler.error_box(f"未知错误: {str(e)}")
            else:
                st.info("请点击\"开始对比\"按钮开始音频对比分析")

    def _render_feature_similarities(self, similarities: Dict[str, float]):
        """渲染特征相似度"""
        if not similarities:
            return
        
        # 按特征类型分组显示
        spectral_features = {k: v for k, v in similarities.items() if 'spectral' in k}
        mfcc_features = {k: v for k, v in similarities.items() if 'mfcc' in k}
        tempo_features = {k: v for k, v in similarities.items() if 'tempo' in k}
        
        if spectral_features:
            st.write("**频谱特征相似度:**")
            for feature, value in spectral_features.items():
                feature_name = feature.replace('_similarity', '').replace('_', ' ').title()
                st.write(f"- {feature_name}: {value:.4f}")
        
        if mfcc_features:
            st.write("**MFCC特征相似度:**")
            for feature, value in mfcc_features.items():
                feature_name = feature.replace('_similarity', '').replace('_', ' ').title()
                st.write(f"- {feature_name}: {value:.4f}")
        
        if tempo_features:
            st.write("**节奏特征相似度:**")
            for feature, value in tempo_features.items():
                feature_name = feature.replace('_similarity', '').replace('_', ' ').title()
                st.write(f"- {feature_name}: {value:.4f}")


class BatchAnalysisPage:
    """批量分析页面"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.analyzer = AudioAnalyzer(config.audio)
        self.visualizer = AudioVisualizer(config.visualization)
        self.file_selector = AudioFileSelector(config)
    
    def render(self):
        """渲染批量A/B目录对比页面"""
        st.header("批量A/B目录对比")
        
        st.markdown("选择两个目录，将自动对比同名音频文件。")
        
        # 目录选择
        dir_a = st.text_input("目录A路径", value="./audio_files/A")
        dir_b = st.text_input("目录B路径", value="./audio_files/B")
        
        if st.button("扫描并对比同名文件"):
            from src.utils.config import find_matching_files
            matches = find_matching_files(dir_a, dir_b)
            if not matches:
                st.warning("未找到同名音频文件。")
                return
            st.success(f"共找到 {len(matches)} 对同名文件。开始批量对比...")
            
            # 直接进行批量对比
            if matches:
                # 为每个文件对进行完整对比分析
                results = []
                for i, (fname, path_a, path_b) in enumerate(matches):
                    # 先计算相似度用于显示在标题中
                    try:
                        y1_temp, sr1_temp = self.analyzer.load_audio_from_path(path_a)
                        y2_temp, sr2_temp = self.analyzer.load_audio_from_path(path_b)
                        if y1_temp is not None and y2_temp is not None:
                            sim_temp = self.analyzer.calculate_similarity(y1_temp, y2_temp, sr1_temp, sr2_temp)
                            cosine_sim = sim_temp.get('cosine_similarity', 0)
                            title = f"文件对比 {i+1}/{len(matches)}: {fname} (相似度: {cosine_sim:.3f})"
                        else:
                            title = f"文件对比 {i+1}/{len(matches)}: {fname} (加载失败)"
                    except:
                        title = f"文件对比 {i+1}/{len(matches)}: {fname}"
                    
                    with st.expander(title, expanded=False):
                        try:
                            # 加载音频
                            y1, sr1 = self.analyzer.load_audio_from_path(path_a)
                            y2, sr2 = self.analyzer.load_audio_from_path(path_b)
                            
                            if y1 is not None and y2 is not None:
                                # 显示音频播放器
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.subheader("音频A")
                                    self._render_audio_player(path_a, fname)
                                with col2:
                                    st.subheader("音频B")
                                    self._render_audio_player(path_b, fname)
                                
                                # 检查采样率是否不同
                                use_multi_scale = sr2 is not None and sr1 != sr2
                                
                                if use_multi_scale:
                                    st.info(f"检测到不同采样率: 音频A ({sr1} Hz) vs 音频B ({sr2} Hz)")
                                    
                                    # 选择对比模式
                                    comparison_mode = st.selectbox(
                                        f"选择对比模式 - {fname}",
                                        ["标准对比", "多尺度对比"],
                                        key=f"comparison_mode_{i}",
                                        help="标准对比：重采样到统一频率后对比；多尺度对比：同时显示原始特征对比和重采样对比"
                                    )
                                    
                                    if comparison_mode == "多尺度对比":
                                        multi_scale_results = self.analyzer.calculate_multi_scale_similarity(y1, y2, sr1, sr2)
                                        
                                        # 显示原始特征对比
                                        if 'original' in multi_scale_results:
                                            st.subheader("原始特征对比")
                                            self._render_feature_similarities(multi_scale_results['original'])
                                        
                                        # 显示重采样对比
                                        if 'resampled' in multi_scale_results:
                                            st.subheader("重采样对比")
                                            SimilarityDisplay.render_metrics(multi_scale_results['resampled'])
                                    else:
                                        similarity = self.analyzer.calculate_similarity(y1, y2, sr1, sr2)
                                        if similarity:
                                            st.subheader("相似度分析")
                                            SimilarityDisplay.render_metrics(similarity)
                                else:
                                    similarity = self.analyzer.calculate_similarity(y1, y2, sr1, sr2)
                                    if similarity:
                                        st.subheader("相似度分析")
                                        SimilarityDisplay.render_metrics(similarity)
                                
                                # 显示可视化图表
                                tab_wave, tab_mel, tab_mel_centroid, tab_mfcc = st.tabs([
                                    "波形对比", "Mel 频谱对比", "Mel 谱率对比", "MFCC 对比"
                                ])
                                
                                with tab_wave:
                                    overlay_wave_fig = self.visualizer.plot_overlay_waveform(
                                        y1, y2, sr1,
                                        title1=f"音频A ({fname})",
                                        title2=f"音频B ({fname})"
                                    )
                                    ChartDisplay.render_chart(overlay_wave_fig, "叠加波形对比")
                                    
                                    waveform_comp_fig = self.visualizer.plot_comparison_waveform(
                                        y1, y2, sr1,
                                        title1=f"音频A ({fname})",
                                        title2=f"音频B ({fname})"
                                    )
                                    ChartDisplay.render_chart(waveform_comp_fig, "波形对比")
                                
                                with tab_mel:
                                    mel_comp_fig = self.visualizer.plot_comparison_mel(
                                        y1, y2, sr1,
                                        title1=f"音频A ({fname})",
                                        title2=f"音频B ({fname})"
                                    )
                                    ChartDisplay.render_chart(mel_comp_fig, "Mel 频谱对比")
                                
                                with tab_mel_centroid:
                                    overlay_centroid_fig = self.visualizer.plot_overlay_mel_spectral_centroid(
                                        y1, y2, sr1,
                                        title1=f"音频A ({fname})",
                                        title2=f"音频B ({fname})"
                                    )
                                    ChartDisplay.render_chart(overlay_centroid_fig, "叠加 Mel 谱率对比")
                                    
                                    mel_centroid_fig = self.visualizer.plot_comparison_mel_spectral_centroid(
                                        y1, y2, sr1,
                                        title1=f"音频A ({fname})",
                                        title2=f"音频B ({fname})"
                                    )
                                    ChartDisplay.render_chart(mel_centroid_fig, "Mel 谱率对比")
                                
                                with tab_mfcc:
                                    mfcc_comp_fig = self.visualizer.plot_comparison_mfcc(
                                        y1, y2, sr1,
                                        title1=f"音频A ({fname})",
                                        title2=f"音频B ({fname})"
                                    )
                                    ChartDisplay.render_chart(mfcc_comp_fig, "MFCC 对比")
                                
                                # 收集结果用于汇总表格
                                sim = self.analyzer.calculate_similarity(y1, y2, sr1, sr2)
                                row = {"文件名": fname}
                                row.update(sim)
                                results.append(row)
                                
                            else:
                                st.error("音频加载失败")
                                results.append({"文件名": fname, "错误": "音频加载失败"})
                                
                        except Exception as e:
                            st.error(f"对比分析失败: {str(e)}")
                            results.append({"文件名": fname, "错误": str(e)})
                
                # 显示汇总结果表格
                if results:
                    st.subheader("汇总对比结果")
                    import pandas as pd
                    df = pd.DataFrame(results)
                    st.dataframe(df)
                    st.download_button("导出CSV", df.to_csv(index=False).encode("utf-8-sig"), file_name="batch_compare_results.csv")
    
    def _render_audio_player(self, audio_path: str, filename: str):
        """渲染音频播放器"""
        try:
            with open(audio_path, 'rb') as f:
                audio_bytes = f.read()
            
            # 根据文件扩展名确定MIME类型
            ext = os.path.splitext(audio_path)[1].lower()
            mime_type_map = {
                '.wav': 'audio/wav',
                '.mp3': 'audio/mpeg',
                '.flac': 'audio/flac',
                '.ogg': 'audio/ogg',
                '.m4a': 'audio/mp4'
            }
            mime_type = mime_type_map.get(ext, 'audio/wav')
            
            st.audio(audio_bytes, format=mime_type)
            
            # 显示音频信息（不使用expander避免嵌套）
            y, sr = self.analyzer.load_audio_from_path(audio_path)
            if y is not None:
                audio_info = self.analyzer.get_audio_info(y, sr)
                file_size = os.path.getsize(audio_path)
                
                st.caption("**音频信息:**")
                st.caption(f"文件大小: {file_size / 1024:.1f} KB | 时长: {audio_info.get('duration', 0):.2f} 秒 | 采样率: {audio_info.get('sample_rate', 0)} Hz")
                st.caption(f"RMS: {audio_info.get('rms', 0):.4f} | 零交叉率: {audio_info.get('zero_crossing_rate', 0):.4f}")
                    
        except Exception as e:
            st.error(f"音频播放器加载失败: {str(e)}")
    
    def _render_feature_similarities(self, similarities: Dict[str, float]):
        """渲染特征相似度"""
        if not similarities:
            return
        
        # 按特征类型分组显示
        spectral_features = {k: v for k, v in similarities.items() if 'spectral' in k}
        mfcc_features = {k: v for k, v in similarities.items() if 'mfcc' in k}
        tempo_features = {k: v for k, v in similarities.items() if 'tempo' in k}
        
        if spectral_features:
            st.write("**频谱特征相似度:**")
            for feature, value in spectral_features.items():
                feature_name = feature.replace('_similarity', '').replace('_', ' ').title()
                st.write(f"- {feature_name}: {value:.4f}")
        
        if mfcc_features:
            st.write("**MFCC特征相似度:**")
            for feature, value in mfcc_features.items():
                feature_name = feature.replace('_similarity', '').replace('_', ' ').title()
                st.write(f"- {feature_name}: {value:.4f}")
        
        if tempo_features:
            st.write("**节奏特征相似度:**")
            for feature, value in tempo_features.items():
                feature_name = feature.replace('_similarity', '').replace('_', ' ').title()
                st.write(f"- {feature_name}: {value:.4f}")


class AboutPage:
    """关于页面"""
    
    def render(self):
        """渲染关于页面"""
        st.header("关于")
        
        st.markdown("""
        ## TTS 音频验收工具
        
        ### 主要功能
        
        - **单音频分析**: 详细的音频特征提取和可视化
        - **音频对比**: 两个音频文件的对比分析
        - **批量分析**: 多个音频文件的批量处理
        
        ### 支持的音频格式
        
        - WAV
        - MP3  
        - FLAC
        - OGG
        - M4A
        """) 