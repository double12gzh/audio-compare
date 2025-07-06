"""
页面模块
提供不同功能的页面组件
"""

# 从拆分后的页面模块导入所有页面类
from .pages import (
    SingleAudioPage,
    ComparisonPage,
    BatchAnalysisPage,
    AboutPage,
)

__all__ = ["SingleAudioPage", "ComparisonPage", "BatchAnalysisPage", "AboutPage"]
