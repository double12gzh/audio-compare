"""
基础页面类
提供页面组件的共同依赖和初始化逻辑
"""

from ...utils.config import AppConfig
from ...core.audio_analyzer import AudioAnalyzer
from ...visualization.audio_plots import AudioVisualizer
from .. import AudioFileSelector


class BasePage:
    """基础页面类"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.analyzer = AudioAnalyzer(config.audio)
        self.visualizer = AudioVisualizer(config.visualization)
        self.file_selector = AudioFileSelector(config)
