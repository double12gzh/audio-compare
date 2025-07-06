"""
侧边栏配置组件模块
提供音频参数配置界面
"""

import streamlit as st
from typing import Dict, Any

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
