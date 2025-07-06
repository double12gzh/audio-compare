"""
关于页面
"""

import streamlit as st


class AboutPage:
    """关于页面"""

    def render(self):
        """渲染关于页面"""
        st.header("关于")

        st.markdown(
            """
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
        """
        )
