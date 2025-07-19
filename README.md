 # PaperRead

## 项目简介

PaperRead 是一个集论文爬取与智能分析于一体的学术工具箱，包含两个核心模块：

- **PaperCrawler**：多源学术论文爬取与下载，支持RSS、arXiv、会议官网等
- **PaperReader**：基于大语言模型（GLM/Qwen）的PDF论文结构化分析

---

## 目录结构

```
PaperRead/
├── PaperCrawler/         # 论文爬取模块
│   ├── PC_main.py        # 主程序，命令行入口
│   ├── rss_crawler.py    # RSS源爬虫
│   ├── arxiv_crawler.py  # arXiv爬虫
│   ├── web_crawler.py    # 通用网页爬虫
│   ├── robotics_conference_crawler.py # 会议专用爬虫
│   ├── paper_downloader.py # PDF下载器
│   └── config.py         # 爬取参数配置
├── PaperReader/          # 论文分析模块
│   ├── PR_main.py        # 主程序，命令行入口
│   ├── pdf_reader.py     # PDF文本提取
│   ├── glm_api.py        # 智谱GLM-4 API
│   ├── qwen_api.py       # 通义千问API
│   ├── result_writer.py  # 结果写入Excel
│   └── config.py         # 分析参数配置
├── Data/
│   ├── PC_Data/
│   │   ├── downloads/    # 下载的PDF
│   │   ├── output/       # 爬取结果json
│   │   └── logs/         # 爬虫日志
│   └── PR_Data/
│       ├── paper/        # 待分析PDF
│       ├── glm_outputs/  # GLM分析输出
│       ├── qwen_outputs/ # Qwen分析输出
│       └── PaperRead_result.xlsx # 分析结果
├── requirements.txt      # 依赖库
└── README.md
```

---

## 安装与环境

- Python 3.8 及以上
- 推荐使用 `venv` 或 `conda` 创建虚拟环境

安装依赖：

```bash
pip install -r requirements.txt
```

**主要依赖：**
- pdfplumber、requests、pandas、openpyxl、tqdm、zhipuai、feedparser、beautifulsoup4

---

## 1. 论文爬取（PaperCrawler）

### 功能
- 支持RSS、arXiv、会议官网等多源论文信息抓取
- 自动下载PDF，支持并发与去重
- 爬取结果保存为json，日志自动记录

### 使用方法

```bash
cd PaperCrawler
python PC_main.py           # 爬取所有配置源并下载PDF
python PC_main.py rss       # 仅爬取RSS
python PC_main.py arxiv     # 仅爬取arXiv
```

**配置说明：**
- 编辑 `config.py` 可自定义RSS源、arXiv分类、网页源、下载参数等

**输出文件：**
- `Data/PC_Data/output/crawled_papers.json`：论文元数据
- `Data/PC_Data/downloads/`：下载的PDF
- `Data/PC_Data/logs/crawler.log`：日志

---

## 2. 论文分析（PaperReader）

### 功能
- 自动扫描指定文件夹下所有PDF
- 提取全文，调用GLM-4/Qwen等大模型结构化分析
- 结果保存为Excel，支持断点续跑与错误日志

### 使用方法

1. 配置API密钥  
   编辑 `PaperReader/config.py`，填写你的 GLM/Qwen API Key

2. 运行分析

```bash
cd PaperReader
python PR_main.py
```

**输出文件：**
- `Data/PR_Data/PaperRead_result.xlsx`：分析结果
- `Data/PR_Data/glm_outputs/`、`qwen_outputs/`：模型原始输出
- `error_log.txt`：错误日志

**分析维度：**
- 论文标题、研究主题、应用场景、主要方法、创新点、主要结论等

---

## 配置详解

- `PaperCrawler/config.py`：自定义爬取源、下载参数、过滤规则等
- `PaperReader/config.py`：API密钥、PDF目录、输出路径等

---

## 扩展开发

- **新增爬取源**：在 `config.py` 添加RSS/网页源，或扩展爬虫脚本
- **新增分析模型**：仿照 `glm_api.py`、`qwen_api.py` 新增API模块，并在 `PR_main.py` 调用

---

## 注意事项

1. 需科学上网以访问部分学术站点
2. 需自行申请GLM/Qwen等API Key
3. 请遵守各站点版权与使用条款
4. 大批量下载建议适当调整爬取间隔，避免IP被封

---

## 许可证

本项目仅供学术研究与学习使用，禁止用于商业用途。

---

如需更详细的使用说明或遇到问题，欢迎查阅各模块源码或联系作者。 