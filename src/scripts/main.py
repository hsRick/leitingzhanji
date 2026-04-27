#!/usr/bin/env python3
"""
主程序

简化版本：
- 仅运行 powerplus 模块与 storeguanggao 模块
- 其他模块待后续加入
- 不需要交互式程序
- 不需要启动参数
- 按顺序直接运行
"""

import sys
import os
import traceback

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.scripts import powerplus
from src.scripts import storeguanggao


def main():
    """
    主函数
    """
    print("🎮 雷霆战机自动脚本")
    print("=" * 60)
    print("开始运行 powerplus 和 storeguanggao 模块")
    print("=" * 60)
    
    # 运行 storeguanggao 模块
    try:
        print("\n🚀 正在运行模块: storeguanggao")
        print("=" * 50)
        storeguanggao.run_main_loop(
            storeguanggao.LOOP_TIMES, 
            storeguanggao.ACTIONS, 
            storeguanggao.SKIP_ICON_FIND, 
            storeguanggao.post_icon_action
        )
        print("=" * 50)
        print("✅ 模块 storeguanggao 运行完成")
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
    except Exception as e:
        print(f"\n❌ 运行模块 storeguanggao 时出错: {e}")
        print(traceback.format_exc())
    
    print("\n" + "=" * 60)
    print("✅ 所有模块运行完成")
    print("=" * 60)

    # 运行 powerplus 模块
    try:
        print("\n🚀 正在运行模块: powerplus")
        print("=" * 50)
        powerplus.run_main_loop(
            powerplus.LOOP_TIMES, 
            powerplus.ACTIONS, 
            powerplus.SKIP_ICON_FIND, 
            powerplus.post_icon_action
        )
        print("=" * 50)
        #点击首页
        find_and_click("static/images/首页.png")
        print("✅ 模块 powerplus 运行完成")
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
    except Exception as e:
        print(f"\n❌ 运行模块 powerplus 时出错: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 程序已停止")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        print(traceback.format_exc())
    finally:
        print("\n🔧 程序已退出")
