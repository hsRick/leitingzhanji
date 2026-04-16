# 雷霆战机：集结 - 自动按键精灵

## 项目简介

这是一个用于自动执行雷霆战机小程序中操作的脚本工具，支持自动点击广告、关闭广告、领取奖励等功能。

## 目录结构

```
leitingzhanji/
├── src/             # 源代码目录
│   ├── scripts/     # 脚本文件
│   └── utils/       # 工具函数
├── static/          # 静态资源
│   └── images/      # 图片文件
├── tests/           # 测试文件
├── README.md        # 项目说明
└── requirements.txt # 依赖项
```

## 功能特性

- 自动查找并点击指定图片
- 支持基于 macOS OCR 的文本查找
- 处理 Retina 显示器的坐标问题
- 支持多轮循环执行
- 可配置的动作列表

## 环境要求

- Python 3.7+
- macOS（OCR 功能仅支持 macOS）
- 依赖项：
  - pyautogui
  - Pillow
  - pyobjc（用于 OCR 功能）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 确保微信小程序 "雷霆战机：集结" 已打开
2. 运行脚本：

```bash
# 运行点击循环脚本
python src/scripts/click_loop.py

# 运行 powerplus 脚本
python src/scripts/powerplus.py

# 运行 storeguanggao 脚本
python src/scripts/storeguanggao.py
```

## 配置说明

每个脚本文件都有以下配置项：

- `LOOP_TIMES`：循环次数（0 表示无限循环）
- `SKIP_ICON_FIND`：是否跳过 icon 查找阶段
- `AFTER_WAIT`：每一步等待时间（秒）
- `ACTIONS`：动作列表，支持以下动作：
  - `["find", "图片路径"]`：自动找图并点击
  - `["find_text", "文本"]`：根据文本查找并点击（使用 macOS OCR）
  - `["key", "按键"]`：按键盘
  - `["wait", 秒数]`：等待
  - `["click", x, y]`：手动点击坐标
- `CONFIDENCE`：找图精度（0.8~0.99，越接近1越严格）

## 注意事项

1. 确保微信小程序窗口在屏幕上可见
2. 确保图片文件与脚本中指定的路径一致
3. 对于 Retina 显示器，脚本会自动处理坐标问题
4. OCR 功能仅在 macOS 上可用，需要安装 pyobjc

## 调试

- 脚本会在执行过程中输出详细的日志信息
- OCR 功能会保存截图到 `static/images/debug_ocr_screenshot.png` 用于调试
