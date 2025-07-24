# PaperHelper

## 项目简介

PaperHelper 是一个论文分析工具箱,集成了论文获取、智能分析等功能:

- **PaperCrawler**: 支持 RSS、arXiv、会议官网等多源论文爬取与下载
- **PaperReader**: 基于大语言模型对论文进行关键词提取
- **WordCluster**: 基于关键词的论文聚类与可视化的模块

## 目录结构

```
PaperHelper/
├── PaperCrawler/                 ###### 论文爬取模块
│   ├── PC_main.py                # 主入口
│   ├── arxiv_crawler.py          # arXiv爬虫
│   ├── web_crawler.py            # 通用网页爬虫
│   ├── rss_crawler.py            # RSS爬虫
│   ├── paper_downloader.py       # PDF下载器
│   └── config.py                 # 配置文件
├── PaperReader/                  ###### 论文分析模块
│   ├── PR_main.py                # 主入口
│   ├── pdf_reader.py             # PDF解析
│   ├── glm_api.py                # GLM模型接口
│   ├── qwen_api.py               # Qwen模型接口
│   ├── result_writer.py          # 结果写入
│   └── config.py                 # 配置文件
├── WordCluster/                  ###### 关键词聚类模块
│   ├── WC_main.py                # 主入口
│   ├── preprocessor.py           # 数据预处理
│   ├── vectorizer.py             # 特征向量化
│   ├── clusterer.py              # 聚类分析
│   ├── visualizer.py             # 可视化
│   └── config.py                 # 配置文件
├── Data/
│   ├── PC_Data/
│   │   ├── downloads/            # 下载的PDF
│   │   ├── output/               # 爬取结果json
│   │   └── logs/                 # 爬虫日志
│   ├── PR_Data/
│   │   ├── paper/                # 待分析PDF
│   │   ├── glm_outputs/          # GLM分析输出
│   │   ├── qwen_outputs/         # Qwen分析输出
│   │   └── PaperRead_result.xlsx # 分析结果
│   └── WC_Data/
│       ├── keywords.xlsx         # 处理结果
│       ├── visualization.png     # 可视化静态
│       └── visualization.html    # 可视化动态
├── requirements.txt      # 依赖库
├── README_en.md   
└── README.md    
```

## 功能特性

### 1. 论文爬取 (PaperCrawler)
- 多源爬取：RSS、arXiv、会议官网
- 自动下载 PDF 并去重
- 支持自定义过滤规则

### 2. 论文分析 (PaperReader) 
- PDF 全文提取
- 基于大模型的结构化分析
- 支持 GLM-4/Qwen 等多种模型
- 分析维度包括:研究主题、应用场景、方法创新等

### 3. 知识聚类 (WordCluster)
- 关键词提取与向量化
- 自适应聚类分析
- 交互式可视化
- 支持 2D/3D 动态展示

## 使用方法

### 安装
```bash
# 创建虚拟环境
conda create -n paperhelper python=3.8
conda activate paperhelper

# 安装依赖
pip install -r requirements.txt
```

### 配置
1. 复制并重命名配置文件:
```bash
cp PaperReader/config_example.py PaperReader/config.py
```

2. 编辑配置文件,填入必要参数:
- API keys (GLM/Qwen)
- 输入输出路径
- 其他个性化设置

### 运行

**论文爬取:**
```bash
python PaperCrawler/PC_main.py
```

**论文分析:**
```bash
python PaperReader/PR_main.py
```

**知识聚类:**
```bash
python WordCluster/WC_main.py
```

## 注意事项

1. 需要科学上网访问部分学术网站
2. 请自行申请 GLM/Qwen API key
3. 注意遵守网站使用条款和下载限制
4. 建议合理配置爬取间隔,避免 IP 封禁

## License

本项目仅供学术研究使用,禁止商业用途。

## 联系方式

如有问题或建议,欢迎提 issue 或联系作者。
