# PaperHelper

## Project Overview

PaperHelper is a paper analysis toolbox that integrates paper acquisition and intelligent analysis:

- **PaperCrawler**: Multi-source paper crawler supporting RSS, arXiv, and conference websites
- **PaperReader**: Keyword extraction from papers based on large language models
- **WordCluster**: Paper clustering and visualization module based on keywords

## Directory Structure

```
PaperHelper/
├── PaperCrawler/                 ###### Paper crawling module
│   ├── PC_main.py                # Main entry
│   ├── arxiv_crawler.py          # arXiv crawler
│   ├── web_crawler.py            # General web crawler
│   ├── rss_crawler.py            # RSS crawler
│   ├── paper_downloader.py       # PDF downloader
│   └── config.py                 # Configuration
├── PaperReader/                  ###### Paper analysis module
│   ├── PR_main.py                # Main entry
│   ├── pdf_reader.py             # PDF parser
│   ├── glm_api.py                # GLM model interface
│   ├── qwen_api.py               # Qwen model interface
│   ├── result_writer.py          # Result writer
│   └── config.py                 # Configuration
├── WordCluster/                  ###### Keyword clustering module
│   ├── WC_main.py                # Main entry
│   ├── preprocessor.py           # Data preprocessing
│   ├── vectorizer.py             # Feature vectorization
│   ├── clusterer.py              # Clustering analysis
│   ├── visualizer.py             # Visualization
│   └── config.py                 # Configuration
├── Data/
│   ├── PC_Data/
│   │   ├── downloads/            # Downloaded PDFs
│   │   ├── output/               # Crawling results (json)
│   │   └── logs/                 # Crawler logs
│   ├── PR_Data/
│   │   ├── paper/                # PDFs to analyze
│   │   ├── glm_outputs/          # GLM analysis outputs
│   │   ├── qwen_outputs/         # Qwen analysis outputs
│   │   └── PaperRead_result.xlsx # Analysis results
│   └── WC_Data/
│       ├── keywords.xlsx         # Processing results
│       ├── visualization.png     # Static visualization
│       └── visualization.html    # Dynamic visualization
├── requirements.txt      # Dependencies
├── README_en.md   
└── README.md    
```

## Features

### 1. Paper Crawling (PaperCrawler)
- Multi-source crawling: RSS, arXiv, conference websites
- Automatic PDF download with deduplication
- Customizable filtering rules

### 2. Paper Analysis (PaperReader)
- Full-text PDF extraction
- Structured analysis using large models
- Support for GLM-4/Qwen and other models
- Analysis dimensions: research topics, application scenarios, methodological innovations, etc.

### 3. Knowledge Clustering (WordCluster)
- Keyword extraction and vectorization
- Adaptive clustering analysis
- Interactive visualization
- Support for 2D/3D dynamic display

## Usage

### Installation
```bash
# Create virtual environment
conda create -n paperhelper python=3.8
conda activate paperhelper

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Copy and rename configuration files:
```bash
cp PaperReader/config_example.py PaperReader/config.py
```

2. Edit configuration files with necessary parameters:
- API keys (GLM/Qwen)
- Input/output paths
- Other customization settings

### Running

**Paper Crawling:**
```bash
python PaperCrawler/PC_main.py
```

**Paper Analysis:**
```bash
python PaperReader/PR_main.py
```

**Knowledge Clustering:**
```bash
python WordCluster/WC_main.py
```

## Notes

1. VPN/scientific internet access may be required
2. Apply for your own GLM/Qwen API keys
3. Comply with website terms of use and download limits
4. Configure reasonable crawling intervals to avoid IP bans

## License

This project is for academic research only. Commercial use is prohibited.

## Contact

For questions or suggestions, please raise an issue or contact the author.