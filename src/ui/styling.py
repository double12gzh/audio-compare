"""
CSS样式组件模块
提供自定义样式和UI美化功能
"""

import streamlit as st


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
