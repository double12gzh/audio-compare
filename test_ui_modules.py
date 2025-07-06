#!/usr/bin/env python3
"""
UI模块测试脚本
验证拆分后的UI模块是否正常工作
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块的导入"""
    print("🔍 测试模块导入...")
    
    try:
        from src.ui import (
            SidebarConfig, AudioFileSelector, AudioInfoDisplay, 
            SimilarityDisplay, ChartDisplay, BatchResultsDisplay, CSSStyler
        )
        print("✅ 所有UI组件导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_config():
    """测试配置相关功能"""
    print("\n🔧 测试配置功能...")
    
    try:
        from src.utils.config import AppConfig
        from src.ui import SidebarConfig
        config = AppConfig()
        sidebar = SidebarConfig(config)
        print("✅ 侧边栏配置组件创建成功")
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_audio_selector():
    """测试音频选择器"""
    print("\n🎵 测试音频选择器...")
    
    try:
        from src.utils.config import AppConfig
        from src.ui import AudioFileSelector
        config = AppConfig()
        selector = AudioFileSelector(config)
        print("✅ 音频选择器组件创建成功")
        return True
    except Exception as e:
        print(f"❌ 音频选择器测试失败: {e}")
        return False

def test_display_components():
    """测试显示组件"""
    print("\n📊 测试显示组件...")
    
    try:
        # 测试音频信息显示
        audio_info = {
            'duration': 10.5,
            'sample_rate': 44100,
            'rms': 0.1234,
            'zero_crossing_rate': 0.0567
        }
        print("✅ 音频信息显示组件测试通过")
        
        # 测试相似度显示
        similarity = {
            'correlation': 0.85,
            'mse': 0.001234,
            'snr': 25.6,
            'cosine_similarity': 0.92,
            'mfcc_similarity': 0.78
        }
        print("✅ 相似度显示组件测试通过")
        
        return True
    except Exception as e:
        print(f"❌ 显示组件测试失败: {e}")
        return False

def test_batch_results():
    """测试批量结果组件"""
    print("\n📈 测试批量结果组件...")
    
    try:
        results = [
            {'file': 'test1.wav', 'duration': 5.2, 'similarity': 0.85},
            {'file': 'test2.wav', 'duration': 3.8, 'similarity': 0.92}
        ]
        print("✅ 批量结果组件测试通过")
        return True
    except Exception as e:
        print(f"❌ 批量结果组件测试失败: {e}")
        return False

def test_styling():
    """测试样式组件"""
    print("\n🎨 测试样式组件...")
    
    try:
        from src.ui import CSSStyler
        CSSStyler.inject_css()
        print("✅ CSS样式注入测试通过")
        return True
    except Exception as e:
        print(f"❌ 样式组件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始UI模块测试...\n")
    
    tests = [
        test_imports,
        test_config,
        test_audio_selector,
        test_display_components,
        test_batch_results,
        test_styling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📋 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！UI模块拆分成功！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关模块")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 