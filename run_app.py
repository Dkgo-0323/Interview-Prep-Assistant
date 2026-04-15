#!/usr/bin/env python3
"""
快速启动脚本
运行: python run_app.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    app_path = Path(__file__).parent / "app" / "main.py"
    
    if not app_path.exists():
        print("❌ 错误: 找不到 app/main.py")
        sys.exit(1)
    
    print("🚀 启动 AI 面试助手...")
    print(f"📂 应用路径: {app_path}")
    print("\n" + "="*50)
    
    try:
        subprocess.run(
            ["streamlit", "run", str(app_path)],
            check=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 应用已停止")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ 错误: 未找到 streamlit 命令")
        print("请先安装依赖: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
