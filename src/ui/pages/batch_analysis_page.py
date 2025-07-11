"""
批量分析页面
"""

import streamlit as st
import os
import pandas as pd
from typing import Dict

from .base_page import BasePage
from .. import SimilarityDisplay, ChartDisplay, CSSStyler
from ...utils.exceptions import AudioAnalysisError


class BatchAnalysisPage(BasePage):
    """批量分析页面"""

    def render(self):
        """渲染批量A/B目录对比页面"""
        st.header("批量A/B目录对比")

        st.markdown("选择两个目录，将自动对比同名音频文件。")

        # 获取所有可选目录（含根目录和所有子目录）
        def get_all_dirs(root):
            dirs = [root]
            for d, subdirs, _ in os.walk(root):
                for sub in subdirs:
                    dirs.append(os.path.join(d, sub))
            return sorted(set(dirs))

        # 获取完整路径列表
        all_dirs_full = get_all_dirs("./audio_files")

        # 创建显示名称映射（去掉audio_files/前缀）
        display_names = []
        for dir_path in all_dirs_full:
            if dir_path == "./audio_files":
                display_names.append("根目录")
            else:
                # 去掉 "./audio_files/" 前缀
                rel_path = dir_path.replace("./audio_files/", "")
                display_names.append(rel_path)

        # 创建路径到显示名称的映射
        dir_to_display = dict(zip(all_dirs_full, display_names))
        display_to_dir = dict(zip(display_names, all_dirs_full))

        # 默认值
        default_a = next(
            (d for d in all_dirs_full if d.endswith("/A")),
            all_dirs_full[0] if all_dirs_full else "",
        )
        default_b = next(
            (d for d in all_dirs_full if d.endswith("/B")),
            all_dirs_full[1]
            if len(all_dirs_full) > 1
            else (all_dirs_full[0] if all_dirs_full else ""),
        )

        if "batch_dir_a" not in st.session_state:
            st.session_state.batch_dir_a = default_a
        if "batch_dir_b" not in st.session_state:
            st.session_state.batch_dir_b = default_b

        # 目录选择（下拉）
        dir_a_display = st.selectbox(
            "目录A路径",
            options=display_names,
            index=display_names.index(
                dir_to_display.get(st.session_state.batch_dir_a, display_names[0])
            )
            if st.session_state.batch_dir_a in all_dirs_full
            else 0,
            key="batch_dir_a_select",
        )
        dir_b_display = st.selectbox(
            "目录B路径",
            options=display_names,
            index=display_names.index(
                dir_to_display.get(
                    st.session_state.batch_dir_b,
                    display_names[1] if len(display_names) > 1 else display_names[0],
                )
            )
            if st.session_state.batch_dir_b in all_dirs_full
            else (1 if len(display_names) > 1 else 0),
            key="batch_dir_b_select",
        )

        # 转换回完整路径
        dir_a = display_to_dir[dir_a_display]
        dir_b = display_to_dir[dir_b_display]
        st.session_state.batch_dir_a = dir_a
        st.session_state.batch_dir_b = dir_b

        if st.button("扫描并对比同名文件"):
            from ...utils.config import find_matching_files

            matches = find_matching_files(dir_a, dir_b)
            if not matches:
                st.warning("未找到同名音频文件。")
                return
            st.success(f"共找到 {len(matches)} 对同名文件。开始批量对比...")

            # 直接进行批量对比
            if matches:
                # 检查是否有缓存的结果
                cache_key = f"batch_comparison_{dir_a}_{dir_b}"
                if cache_key not in st.session_state:
                    st.session_state[cache_key] = None
                
                if st.session_state[cache_key] is None:
                    with st.spinner("正在进行批量对比分析..."):
                        self._perform_batch_comparison(matches)
                        st.session_state[cache_key] = True
                else:
                    st.info("使用缓存的分析结果")
                    self._perform_batch_comparison(matches)

    def _perform_batch_comparison(self, matches):
        """执行批量对比分析"""
        # 为每个文件对进行完整对比分析
        results = []
        
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (fname, path_a, path_b) in enumerate(matches):
            # 更新进度
            progress = (i + 1) / len(matches)
            progress_bar.progress(progress)
            status_text.text(f"正在分析: {fname} ({i+1}/{len(matches)})")
            
            # 先计算相似度用于显示在标题中
            try:
                y1_temp, sr1_temp = self.analyzer.load_audio_from_path(path_a)
                y2_temp, sr2_temp = self.analyzer.load_audio_from_path(path_b)
                if y1_temp is not None and y2_temp is not None:
                    sim_temp = self.analyzer.calculate_similarity(
                        y1_temp, y2_temp, sr1_temp, sr2_temp
                    )
                    cosine_sim = sim_temp.get("cosine_similarity", 0)
                    title = (
                        f"文件对比 {i+1}/{len(matches)}: {fname} (相似度: {cosine_sim:.3f})"
                    )
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
                            similarity = self.analyzer.calculate_similarity(
                                y1, y2, sr1, sr2
                            )
                            if similarity:
                                st.subheader("相似度分析")
                                SimilarityDisplay.render_metrics(similarity)

                        # 显示可视化图表
                        self._render_batch_visualizations(y1, y2, sr1, fname)

                        # 收集结果用于汇总表格
                        sim = self.analyzer.calculate_similarity(y1, y2, sr1, sr2)
                        row = {"文件路径": fname}
                        row.update(sim)
                        results.append(row)

                    else:
                        st.error("音频加载失败")
                        results.append({"文件路径": fname, "错误": "音频加载失败"})

                except Exception as e:
                    st.error(f"对比分析失败: {str(e)}")
                    results.append({"文件路径": fname, "错误": str(e)})

        # 清除进度条
        progress_bar.empty()
        status_text.empty()
        
        # 显示汇总结果表格
        if results:
            st.subheader("汇总对比结果")
            df = pd.DataFrame(results)
            st.dataframe(df)
            st.download_button(
                "导出CSV",
                df.to_csv(index=False).encode("utf-8-sig"),
                file_name="batch_compare_results.csv",
            )

    def _render_batch_visualizations(self, y1, y2, sr1, fname: str):
        """渲染批量对比可视化图表"""
        tab_wave, tab_mel, tab_mel_centroid, tab_mfcc = st.tabs(
            [
                "波形对比",
                "Mel 频谱对比",
                "Mel 谱率对比",
                "MFCC 对比",
            ]
        )

        with tab_wave:
            overlay_wave_fig = self.visualizer.plot_overlay_waveform(
                y1,
                y2,
                sr1,
                title1=f"音频A ({fname})",
                title2=f"音频B ({fname})",
            )
            ChartDisplay.render_chart(overlay_wave_fig, "叠加波形对比")

            waveform_comp_fig = self.visualizer.plot_comparison_waveform(
                y1,
                y2,
                sr1,
                title1=f"音频A ({fname})",
                title2=f"音频B ({fname})",
            )
            ChartDisplay.render_chart(waveform_comp_fig, "波形对比")

        with tab_mel:
            mel_comp_fig = self.visualizer.plot_comparison_mel(
                y1,
                y2,
                sr1,
                title1=f"音频A ({fname})",
                title2=f"音频B ({fname})",
            )
            ChartDisplay.render_chart(mel_comp_fig, "Mel 频谱对比")

        with tab_mel_centroid:
            overlay_centroid_fig = self.visualizer.plot_overlay_mel_spectral_centroid(
                y1,
                y2,
                sr1,
                title1=f"音频A ({fname})",
                title2=f"音频B ({fname})",
            )
            ChartDisplay.render_chart(overlay_centroid_fig, "叠加 Mel 谱率对比")

            mel_centroid_fig = self.visualizer.plot_comparison_mel_spectral_centroid(
                y1,
                y2,
                sr1,
                title1=f"音频A ({fname})",
                title2=f"音频B ({fname})",
            )
            ChartDisplay.render_chart(mel_centroid_fig, "Mel 谱率对比")

        with tab_mfcc:
            mfcc_comp_fig = self.visualizer.plot_comparison_mfcc(
                y1,
                y2,
                sr1,
                title1=f"音频A ({fname})",
                title2=f"音频B ({fname})",
            )
            ChartDisplay.render_chart(mfcc_comp_fig, "MFCC 对比")

    def _render_audio_player(self, audio_path: str, filename: str):
        """渲染音频播放器"""
        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            # 根据文件扩展名确定MIME类型
            ext = os.path.splitext(audio_path)[1].lower()
            mime_type_map = {
                ".wav": "audio/wav",
                ".mp3": "audio/mpeg",
                ".flac": "audio/flac",
                ".ogg": "audio/ogg",
                ".m4a": "audio/mp4",
            }
            mime_type = mime_type_map.get(ext, "audio/wav")

            st.audio(audio_bytes, format=mime_type)

            # 显示音频信息（不使用expander避免嵌套）
            y, sr = self.analyzer.load_audio_from_path(audio_path)
            if y is not None:
                audio_info = self.analyzer.get_audio_info(y, sr)
                file_size = os.path.getsize(audio_path)

                st.caption("**音频信息:**")
                st.caption(
                    f"文件大小: {file_size / 1024:.1f} KB | 时长: {audio_info.get('duration', 0):.2f} 秒 | 采样率: {audio_info.get('sample_rate', 0)} Hz"
                )
                st.caption(
                    f"RMS: {audio_info.get('rms', 0):.4f} | 零交叉率: {audio_info.get('zero_crossing_rate', 0):.4f}"
                )

        except Exception as e:
            st.error(f"音频播放器加载失败: {str(e)}")

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
