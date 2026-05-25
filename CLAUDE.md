# PDFGOD - Free PDF Converter

## 项目概述
免费的 Windows 桌面 PDF 转换工具，支持 6 种输出格式。后续计划移植 Mac、Android、iOS。

## 技术栈
| 层 | 技术 |
|-----|------|
| 桌面框架 | Tauri 2.x（Rust） |
| 前端 | Vue 3 + TypeScript + Vite |
| 转换引擎 | Python 3.12（子进程，优先使用 PaddleOCR/.venv） |
| Rust 工具链 | MSVC（stable-x86_64-pc-windows-msvc）|
| UI 风格 | 纯黑主题，无第三方组件库 |

## 项目结构
```
src-tauri/           # Rust 后端
  src/lib.rs         # Tauri 命令：convert_pdf
  Cargo.toml         # 依赖：tauri-plugin-dialog, opener
  tauri.conf.json    # 窗口 620x700，不可调整大小
  capabilities/
src/                 # Vue 3 前端
  App.vue            # 主组件：格式优先 → 多文件管理 → 批量转换
  components/
    DropZone.vue     # 拖拽上传（Tauri onDragDropEvent）
    FormatPicker.vue # 6种格式选择
    ConvertPanel.vue # 转换按钮和进度条
    ResultCard.vue   # 结果列表（成功/失败分别显示）
engine/              # Python 转换引擎
  convert.py         # CLI 入口，UTF-8 stdout 输出 JSON 进度
  pdf_to_word.py     # pdf2docx
  pdf_to_excel.py    # camelot + tabula + openpyxl 后备
  pdf_to_ppt.py      # pdf2image + python-pptx
  pdf_to_txt.py      # PyMuPDF + pdfplumber
  pdf_to_image.py    # PyMuPDF
  pdf_ocr.py         # PaddleOCR (v3.x) + Tesseract 后备
PaddleOCR/           # OCR 环境（Git 忽略，需本地搭建）
  .venv/             # Python venv（所有引擎依赖 + PaddleOCR）
  models/            # OCR 模型文件 (~210 MB)
```

## 常用命令
```bash
npm run tauri dev      # 开发模式（自动编译 Rust + 热更新前端）
npm run tauri build    # 生产构建

# Python 引擎测试（使用 venv）
./PaddleOCR/.venv/Scripts/python engine/convert.py --input test.pdf --format word
```

## 重要配置
- Rust 工具链必须是 MSVC（VS Build Tools 2022），GNU 工具链缺少 MinGW 组件
- 构建前确保 `engine/` 目录与 exe 同目录
- Python stdout 用 JSON 行输出进度，Rust 逐行解析后通过事件推给前端
- **Python 编码**：Windows 上 Python 默认 GBK 输出，`convert.py` 设置 `sys.stdout.reconfigure(encoding="utf-8")`
- **Rust 编码**：使用 `read_to_end()` + `from_utf8_lossy()` 处理中文路径
- **Python 查找**：Rust 优先使用 `PaddleOCR/.venv/Scripts/python.exe`（D 盘），不存在则回退系统 python

## 已完成的关键修复
- **中文文件名乱码**：Python stdout UTF-8 + Rust 宽松 UTF-8 解析
- **OCR 内容错误**：PaddleOCR v3 API 返回 dict（用 `rec_texts` 字段），不是旧版嵌套列表
- **OCR 速度**：关闭文档方向检测/去扭曲/文本行方向，使用 mobile 模型
- **oneDNN bug**：PaddlePaddle 3.3.1 Windows 上有 oneDNN PIR 属性转换 bug，需 `enable_mkldnn=False`
- **模型存储**：设置 `PADDLE_PDX_CACHE_HOME` 到 D 盘，不占 C 盘

## 已知限制
- pdf2docx 不保留原始字体（PDF 存储位置字形，不存储字体名）
- Excel 表格提取需 Java (tabula) 或 Ghostscript (camelot)，否则仅创建空 Excel
- OCR 首次运行需下载模型（~15 MB mobile，~200 MB server）
- @tauri-apps/plugin-dialog `save()` 可能有问题，目前使用动态 import

## 输出路径选择问题
- 已从静态 import 改为动态 import：`const { save } = await import("@tauri-apps/plugin-dialog")`
- 权限：`capabilities/default.json` 包含 `dialog:default`, `dialog:allow-save`, `dialog:allow-open`
- 如果 save dialog 仍然不工作，考虑用 `open` dialog 选目录替代
