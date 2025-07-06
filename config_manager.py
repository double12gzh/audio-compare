#!/usr/bin/env python3
"""
配置管理工具
用于生成、验证和管理TTS音频验收工具的配置文件
"""

import argparse
import sys
import os
from src.utils.config import AppConfig


def generate_default_config(output_path: str = "config.yaml"):
    """生成默认配置文件"""
    try:
        config = AppConfig()
        config.to_yaml(output_path)
        print(f"✅ 默认配置文件已生成: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 生成配置文件失败: {e}")
        return False


def validate_config(config_path: str):
    """验证配置文件"""
    try:
        config = AppConfig.from_yaml(config_path)
        print(f"✅ 配置文件验证成功: {config_path}")

        # 显示配置摘要
        print("\n📋 配置摘要:")
        print(f"  音频根目录: {config.audio_root}")
        print(f"  服务器端口: {config.server.port}")
        print(f"  调试模式: {config.debug_mode}")
        print(f"  日志级别: {config.log_level}")
        print(f"  支持格式: {', '.join(config.file.supported_formats)}")
        print(f"  最大文件大小: {config.file.max_file_size}MB")
        print(f"  最大批量文件数: {config.file.max_batch_files}")

        return True
    except Exception as e:
        print(f"❌ 配置文件验证失败: {e}")
        return False


def show_config_diff(config_path: str):
    """显示当前配置与默认配置的差异"""
    try:
        current_config = AppConfig.from_yaml(config_path)
        default_config = AppConfig()

        print(f"📊 配置文件差异分析: {config_path}")
        print("=" * 50)

        # 比较关键配置项
        diff_items = []

        if current_config.audio_root != default_config.audio_root:
            diff_items.append(
                f"音频根目录: {default_config.audio_root} -> {current_config.audio_root}"
            )

        if current_config.server.port != default_config.server.port:
            diff_items.append(
                f"服务器端口: {default_config.server.port} -> {current_config.server.port}"
            )

        if current_config.debug_mode != default_config.debug_mode:
            diff_items.append(
                f"调试模式: {default_config.debug_mode} -> {current_config.debug_mode}"
            )

        if current_config.log_level != default_config.log_level:
            diff_items.append(
                f"日志级别: {default_config.log_level} -> {current_config.log_level}"
            )

        if current_config.file.max_file_size != default_config.file.max_file_size:
            diff_items.append(
                f"最大文件大小: {default_config.file.max_file_size}MB -> {current_config.file.max_file_size}MB"
            )

        if current_config.file.max_batch_files != default_config.file.max_batch_files:
            diff_items.append(
                f"最大批量文件数: {default_config.file.max_batch_files} -> {current_config.file.max_batch_files}"
            )

        if diff_items:
            print("🔧 已修改的配置项:")
            for item in diff_items:
                print(f"  • {item}")
        else:
            print("📝 所有配置项均为默认值")

        return True
    except Exception as e:
        print(f"❌ 配置差异分析失败: {e}")
        return False


def backup_config(config_path: str, backup_path: str = None):
    """备份配置文件"""
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False

    if backup_path is None:
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{config_path}.backup_{timestamp}"

    try:
        import shutil

        shutil.copy2(config_path, backup_path)
        print(f"✅ 配置文件已备份: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ 备份配置文件失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="TTS音频验收工具配置管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python config_manager.py generate                    # 生成默认配置
  python config_manager.py validate config.yaml        # 验证配置文件
  python config_manager.py diff config.yaml           # 显示配置差异
  python config_manager.py backup config.yaml         # 备份配置文件
        """,
    )

    parser.add_argument(
        "action", choices=["generate", "validate", "diff", "backup"], help="要执行的操作"
    )

    parser.add_argument(
        "config_path", nargs="?", default="config.yaml", help="配置文件路径 (默认: config.yaml)"
    )

    parser.add_argument("--backup-path", help="备份文件路径 (仅用于backup操作)")

    args = parser.parse_args()

    if args.action == "generate":
        success = generate_default_config(args.config_path)
    elif args.action == "validate":
        success = validate_config(args.config_path)
    elif args.action == "diff":
        success = show_config_diff(args.config_path)
    elif args.action == "backup":
        success = backup_config(args.config_path, args.backup_path)
    else:
        parser.print_help()
        return

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
