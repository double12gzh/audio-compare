"""
TTS 音频验收工具主应用
使用模块化架构重构
"""

import streamlit as st
import os
from src.utils.config import AppConfig
from src.ui import CSSStyler, SidebarConfig
from src.ui.pages import SingleAudioPage, ComparisonPage, BatchAnalysisPage, AboutPage


def setup_page_config(config: AppConfig):
    """设置页面配置"""
    st.set_page_config(
        page_title=config.ui.page_title,
        page_icon=config.ui.page_icon,
        layout=config.ui.layout,
        initial_sidebar_state=config.ui.initial_sidebar_state,
    )


def main():
    """主函数"""
    # 初始化配置
    config_path = os.environ.get("AUDIO_COMPARE_CONFIG", "config.yaml")

    try:
        # 尝试从YAML文件加载配置
        config = AppConfig.from_yaml(config_path)
        print(f"✅ 成功从配置文件加载: {config_path}")
    except (FileNotFoundError, ValueError) as e:
        # 如果配置文件不存在或加载失败，使用默认配置
        print(f"⚠️  配置文件加载失败: {e}")
        print("使用默认配置启动应用")
        config = AppConfig()

    # 设置页面配置
    setup_page_config(config)

    # 注入CSS样式
    CSSStyler.inject_css()

    # 显示主标题
    st.markdown('<h1 class="main-header">🎵 TTS 音频验收工具</h1>', unsafe_allow_html=True)

    # 侧边栏配置
    sidebar_config = SidebarConfig(config)
    sidebar_params = sidebar_config.render()

    # 主界面标签页
    tab1, tab2, tab3, tab4 = st.tabs(["📊 单音频分析", "🔄 音频对比", "📈 批量分析", "ℹ️ 关于"])

    # 单音频分析页面
    with tab1:
        single_page = SingleAudioPage(config)
        single_page.render()

    # 音频对比页面
    with tab2:
        comparison_page = ComparisonPage(config)
        comparison_page.render()

    # 批量分析页面
    with tab3:
        batch_page = BatchAnalysisPage(config)
        batch_page.render()

    # 关于页面
    with tab4:
        about_page = AboutPage()
        about_page.render()


if __name__ == "__main__":
    main()
