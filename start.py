#!/usr/bin/env python3
"""
TTS音频验收工具启动脚本
支持通过命令行参数指定配置文件路径
"""

import argparse
import sys
import os
import subprocess
from src.utils.config import AppConfig


def validate_config_file(config_path: str) -> bool:
    """验证配置文件"""
    try:
        config = AppConfig.from_yaml(config_path)
        print(f"✅ 配置文件验证成功: {config_path}")
        return True
    except Exception as e:
        print(f"❌ 配置文件验证失败: {e}")
        return False


def start_streamlit_app(config_path: str = None, port: int = None, host: str = None):
    """启动Streamlit应用"""

    # 构建streamlit命令
    cmd = ["streamlit", "run", "app.py"]

    # 如果指定了配置文件，设置环境变量
    if config_path:
        os.environ["AUDIO_COMPARE_CONFIG"] = config_path
        print(f"📁 使用配置文件: {config_path}")

    # 如果指定了端口
    if port:
        cmd.extend(["--server.port", str(port)])
        print(f"🌐 服务端口: {port}")

    # 如果指定了主机
    if host:
        cmd.extend(["--server.address", host])
        print(f"🏠 服务地址: {host}")

    print("🚀 启动TTS音频验收工具...")
    print(f"📋 执行命令: {' '.join(cmd)}")
    print("=" * 50)

    try:
        # 启动streamlit应用
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ 未找到streamlit命令，请确保已安装streamlit")
        print("💡 安装命令: pip install streamlit")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="TTS音频验收工具启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python start.py                                    # 使用默认配置启动
  python start.py -c config.yaml                     # 使用指定配置文件
  python start.py -c config.yaml -p 8502             # 指定端口
  python start.py -c config.yaml -p 8502 -H 0.0.0.0  # 指定端口和主机
  python start.py --validate config.yaml             # 仅验证配置文件
        """,
    )

    parser.add_argument(
        "-c", "--config", default="config.yaml", help="配置文件路径 (默认: config.yaml)"
    )

    parser.add_argument("-p", "--port", type=int, help="服务端口 (默认: 8501)")

    parser.add_argument("-H", "--host", help="服务主机地址 (默认: localhost)")

    parser.add_argument("--validate", action="store_true", help="仅验证配置文件，不启动应用")

    parser.add_argument("config_file", nargs="?", help="要验证的配置文件路径 (仅用于--validate模式)")

    parser.add_argument("--no-config", action="store_true", help="不使用配置文件，使用默认配置")

    args = parser.parse_args()

    # 如果只是验证配置文件
    if args.validate:
        config_to_validate = args.config_file or args.config
        if validate_config_file(config_to_validate):
            sys.exit(0)
        else:
            sys.exit(1)

    # 如果不使用配置文件
    if args.no_config:
        config_path = None
    else:
        config_path = args.config
        # 验证配置文件
        if not validate_config_file(config_path):
            print("❌ 配置文件验证失败，退出")
            sys.exit(1)

    # 启动应用
    start_streamlit_app(config_path=config_path, port=args.port, host=args.host)


if __name__ == "__main__":
    main()
