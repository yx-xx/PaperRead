# PaperRead

## Project Overview

PaperRead is an academic toolbox that integrates paper crawling and intelligent analysis, featuring two core modules:

- **PaperCrawler**: Multi-source academic paper crawler and downloader, supporting RSS, arXiv, conference websites, etc.
- **PaperReader**: Structured PDF paper analysis powered by large language models (GLM/Qwen)

---

## Directory Structure

```
PaperRead/
├── PaperCrawler/         # Paper crawling module
│   ├── PC_main.py        # Main entry script
│   ├── rss_crawler.py    # RSS crawler
│   ├── arxiv_crawler.py  # arXiv crawler
│   ├── web_crawler.py    # General web crawler
│   ├── robotics_conference_crawler.py # Conference-specific crawler
│   ├── paper_downloader.py # PDF downloader
│   └── config.py         # Crawler configuration
├── PaperReader/          # Paper analysis module
│   ├── PR_main.py        # Main entry script
│   ├── pdf_reader.py     # PDF text extraction
│   ├── glm_api.py        # GLM-4 API integration
│   ├── qwen_api.py       # Qwen API integration
│   ├── result_writer.py  # Write results to Excel
│   └── config.py         # Analysis configuration
├── Data/
│   ├── PC_Data/
│   │   ├── downloads/    # Downloaded PDFs
│   │   ├── output/       # Crawled results (json)
│   │   └── logs/         # Crawler logs
│   └── PR_Data/
│       ├── paper/        # PDFs to be analyzed
│       ├── glm_outputs/  # GLM analysis outputs
│       ├── qwen_outputs/ # Qwen analysis outputs
│       └── PaperRead_result.xlsx # Analysis results
├── requirements.txt      # Dependencies
└── README.md
```

---

## Installation & Environment

- Python 3.8 or above
- It is recommended to use `venv` or `conda` for a virtual environment

Install dependencies:

```bash
pip install -r requirements.txt
```

**Main dependencies:**
- pdfplumber, requests, pandas, openpyxl, tqdm, zhipuai, feedparser, beautifulsoup4

---

## 1. Paper Crawling (PaperCrawler)

### Features
- Crawl paper information from RSS, arXiv, conference websites, etc.
- Automatically download PDFs, with concurrency and deduplication
- Save results as JSON, with automatic logging

### Usage

```bash
cd PaperCrawler
python PC_main.py           # Crawl all configured sources and download PDFs
python PC_main.py rss       # Only crawl RSS sources
python PC_main.py arxiv     # Only crawl arXiv
```

**Configuration:**
- Edit `config.py` to customize RSS sources, arXiv categories, web sources, download parameters, etc.

**Output files:**
- `Data/PC_Data/output/crawled_papers.json`: Paper metadata
- `Data/PC_Data/downloads/`: Downloaded PDFs
- `Data/PC_Data/logs/crawler.log`: Logs

---

## 2. Paper Analysis (PaperReader)

### Features
- Automatically scan all PDFs in the specified folder
- Extract full text and analyze with GLM-4/Qwen or other LLMs
- Save results to Excel, support resume and error logging

### Usage

1. Configure API keys  
   Edit `PaperReader/config.py` and fill in your GLM/Qwen API Key

2. Run analysis

```bash
cd PaperReader
python PR_main.py
```

**Output files:**
- `Data/PR_Data/PaperRead_result.xlsx`: Analysis results
- `Data/PR_Data/glm_outputs/`, `qwen_outputs/`: Raw model outputs
- `error_log.txt`: Error log

**Analysis dimensions:**
- Paper title, research topic, application scenario, main methods, innovations, main conclusions, etc.

---

## Configuration Details

- `PaperCrawler/config.py`: Customize crawling sources, download parameters, filtering rules, etc.
- `PaperReader/config.py`: API keys, PDF directory, output paths, etc.

---

## Extension & Development

- **Add new crawling sources**: Add RSS/web sources in `config.py` or extend crawler scripts
- **Add new analysis models**: Create new API modules like `glm_api.py`/`qwen_api.py` and call them in `PR_main.py`

---

## Notes

1. Some academic sites may require VPN/scientific internet access
2. You need to apply for your own GLM/Qwen API keys
3. Please comply with copyright and terms of use of each site
4. For large-scale downloads, adjust crawling intervals to avoid IP bans

---

## License

This project is for academic research and learning only. Commercial use is prohibited.

---

For more detailed instructions or if you encounter any issues, please refer to the source code of each module or contact the author. 