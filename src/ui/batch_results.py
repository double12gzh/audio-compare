"""
批量结果显示组件模块
提供批量分析结果的表格显示和导出功能
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any


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
