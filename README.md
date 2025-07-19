# PaperRead

## 项目简介

PaperRead 是一个用于批量分析学术论文 PDF 文件的自动化工具。它能够自动读取指定文件夹下的 PDF 论文，利用大语言模型（如 GLM-4）对论文内容进行结构化分析，并将结果保存为 Excel 文件，便于后续整理和检索。

## 主要功能

- 自动扫描指定文件夹下的所有 PDF 文件（支持跳过已处理文件）
- 提取 PDF 全文内容
- 调用大语言模型（GLM-4）对论文进行多维度结构化分析，包括：
  - 论文标题
  - 研究主题关键词
  - 应用场景关键词
  - 主要方法关键词
  - 创新点关键词
  - 主要结论关键词
- 分析结果自动追加保存到 Excel 文件
- 错误日志记录，便于排查问题

## 依赖环境

- Python 3.8 及以上
- 推荐使用 conda 或 venv 创建独立环境
- 依赖库（可通过 `pip install -r requirements.txt` 一键安装）：

  ```
  pdfplumber
  requests
  pandas
  openpyxl
  tqdm
  zhipuai
  ```

## 快速开始

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

2. **配置参数**

   - 在 `config.py` 中配置你的 PDF 文件夹路径、输出 Excel 路径，以及 GLM API Key 等信息。

3. **准备论文 PDF**

   - 将所有需要分析的 PDF 文件放入 `paper/` 文件夹（或你在配置中指定的文件夹）。

4. **运行主程序**

   ```bash
   python main.py
   ```

   程序会自动处理所有未分析过的 PDF 文件，并将结果保存到 `PaperRead_result.xlsx`。

## 结果说明

- 分析结果保存在 Excel 文件中，每篇论文一行，包含论文标题、关键词等结构化信息。
- 若分析失败或出错，会在 `error_log.txt` 记录详细信息，便于后续排查。

## 目录结构

```
PaperRead/
  ├── main.py                # 主程序入口
  ├── pdf_reader.py          # PDF 读取与文本提取
  ├── glm_api.py             # GLM-4 LLM 调用与分析
  ├── result_writer.py       # 结果写入 Excel
  ├── config.py              # 配置文件
  ├── paper/                 # 存放待分析的 PDF 文件
  ├── debug_outputs/         # 存放 LLM 原始输出（调试用）
  ├── qwen_outputs/          # 其他模型输出（可选）
  ├── requirements.txt       # 依赖列表
```

## 注意事项

- 需提前申请 GLM-4 API Key 并正确配置。
- 若需支持其他 LLM，可扩展 `glm_api.py` 或新增类似模块。
- 仅支持文本型 PDF，扫描件或图片型 PDF 需先 OCR 处理。
- 推荐在 Linux 或 macOS 下运行，Windows 需注意编码和依赖兼容性。

## 联系方式

如有问题或建议，欢迎 issue 或联系作者。 