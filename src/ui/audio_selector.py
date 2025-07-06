"""
音频文件选择器组件模块
提供音频文件选择和预览功能
"""

import streamlit as st
import os
import librosa
from typing import Dict, Any, List, Optional, Tuple

from ..utils.config import AppConfig


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

    def render_single(self, key: str = "single_audio_file") -> Optional[str]:
        """渲染单个音频文件选择器"""
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
    ) -> Tuple[Optional[str], Optional[str]]:
        """渲染双音频文件选择器"""
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

    def render_batch(self, key: str = "batch_audio_files") -> List[str]:
        """渲染批量音频文件选择器"""
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
