# PDFGOD - Free PDF Converter

## 项目概述
免费的 Windows 桌面 PDF 转换工具，支持 6 种输出格式。后续计划移植 Mac、Android、iOS。

## 技术栈
| 层 | 技术 |
|-----|------|
| 桌面框架 | Tauri 2.x（Rust） |
| 前端 | Vue 3 + TypeScript + Vite |
| 转换引擎 | Python 3.12（子进程）|
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
  App.vue            # 主组件，状态管理和事件监听
  components/
    DropZone.vue     # 拖拽上传
    FormatPicker.vue # 6种格式选择
    ConvertPanel.vue # 转换按钮和进度条
    ResultCard.vue   # 结果展示
engine/              # Python 转换引擎
  convert.py         # CLI 入口
  pdf_to_word.py     # pdf2docx
  pdf_to_excel.py    # camelot + tabula
  pdf_to_ppt.py      # pdf2image + python-pptx
  pdf_to_txt.py      # PyMuPDF + pdfplumber
  pdf_to_image.py    # PyMuPDF
  pdf_ocr.py         # PaddleOCR + Tesseract
```

## 常用命令
```bash
npm run tauri dev      # 开发模式
npm run tauri build    # 生产构建
pip install -r engine/requirements.txt  # 安装Python依赖
```

## 重要配置
- Rust 工具链必须是 MSVC（VS Build Tools 2022），GNU 工具链缺少 MinGW 组件
- 构建前确保 `engine/` 目录与 exe 同目录
- Python stdout 用 JSON 行输出进度，Rust 逐行解析后通过事件推给前端
