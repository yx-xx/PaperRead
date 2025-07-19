#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaperCrawler - 学术论文爬取工具
支持从多个学术网站和RSS源爬取论文信息
"""

import os
import sys
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional

from rss_crawler import RSSCrawler
from arxiv_crawler import ArxivCrawler
from paper_downloader import PaperDownloader
from web_crawler import WebCrawler
from robotics_conference_crawler import RoboticsConferenceCrawler
from config import Config

# 配置日志
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 回到项目根目录
log_dir = os.path.join(project_root, 'Data', 'PC_Data', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'crawler.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PaperCrawler:
    """论文爬取主类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.rss_crawler = RSSCrawler(config)
        self.arxiv_crawler = ArxivCrawler(config)
        self.web_crawler = WebCrawler(config)
        self.robotics_crawler = RoboticsConferenceCrawler(config)
        self.downloader = PaperDownloader(config)
        
    def crawl_rss_sources(self) -> List[Dict[str, Any]]:
        """爬取RSS源的论文信息"""
        logger.info("开始爬取RSS源...")
        papers = []
        
        for rss_url in self.config.rss_sources:
            try:
                logger.info(f"爬取RSS源: {rss_url}")
                papers.extend(self.rss_crawler.crawl_rss(rss_url))
            except Exception as e:
                logger.error(f"爬取RSS源 {rss_url} 失败: {e}")
                
        logger.info(f"RSS爬取完成，共获取 {len(papers)} 篇论文信息")
        return papers
    
    def crawl_arxiv(self, query: Optional[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """爬取arXiv论文"""
        logger.info("开始爬取arXiv...")
        try:
            papers = self.arxiv_crawler.search_papers(query, max_results)
            logger.info(f"arXiv爬取完成，共获取 {len(papers)} 篇论文信息")
            return papers
        except Exception as e:
            logger.error(f"爬取arXiv失败: {e}")
            return []
    
    def crawl_webpage(self, url: str) -> List[Dict[str, Any]]:
        """爬取单个网页的论文"""
        logger.info(f"开始爬取网页: {url}")
        try:
            papers = self.web_crawler.crawl_webpage(url)
            logger.info(f"网页爬取完成，共获取 {len(papers)} 篇论文信息")
            return papers
        except Exception as e:
            logger.error(f"爬取网页失败: {e}")
            return []
    
    def crawl_web_sources(self) -> List[Dict[str, Any]]:
        """爬取配置的网页源"""
        logger.info("开始爬取配置的网页源...")
        papers = []
        
        for url in self.config.web_sources:
            try:
                logger.info(f"爬取网页: {url}")
                
                # 检查是否是roboticsconference.org
                if 'roboticsconference.org' in url:
                    # 使用专门的爬取器
                    papers.extend(self.robotics_crawler.crawl_conference_papers(url))
                else:
                    # 使用通用网页爬取器
                    papers.extend(self.crawl_webpage(url))
                    
            except Exception as e:
                logger.error(f"爬取网页 {url} 失败: {e}")
                continue
                
        logger.info(f"网页源爬取完成，共获取 {len(papers)} 篇论文信息")
        return papers
    
    def download_papers(self, papers: List[Dict[str, Any]]) -> List[str]:
        """下载论文PDF文件"""
        logger.info("开始下载论文PDF...")
        downloaded_files = []
        
        for paper in papers:
            try:
                if paper.get('pdf_url'):
                    file_path = self.downloader.download_paper(
                        paper['pdf_url'], 
                        paper.get('title', 'unknown')
                    )
                    if file_path:
                        downloaded_files.append(file_path)
                        logger.info(f"成功下载: {paper.get('title', 'unknown')}")
            except Exception as e:
                logger.error(f"下载论文失败 {paper.get('title', 'unknown')}: {e}")
        
        logger.info(f"下载完成，共下载 {len(downloaded_files)} 个PDF文件")
        return downloaded_files
    
    def run(self, source_type: str = 'all', target_url: Optional[str] = None):
        """运行爬取程序"""
        logger.info("开始运行PaperCrawler...")
        
        all_papers = []
        
        if target_url:
            # 爬取指定网页
            web_papers = self.crawl_webpage(target_url)
            all_papers.extend(web_papers)
        else:
            # 爬取配置的源
            if source_type in ['rss', 'all']:
                rss_papers = self.crawl_rss_sources()
                all_papers.extend(rss_papers)
            
            if source_type in ['arxiv', 'all']:
                arxiv_papers = self.crawl_arxiv()
                all_papers.extend(arxiv_papers)
            
            if source_type in ['web', 'all']:
                web_papers = self.crawl_web_sources()
                all_papers.extend(web_papers)
        
        # 去重
        unique_papers = self._remove_duplicates(all_papers)
        logger.info(f"去重后共有 {len(unique_papers)} 篇论文")
        
        # 保存论文信息
        self._save_paper_info(unique_papers)
        
        # 下载PDF文件
        if self.config.auto_download:
            downloaded_files = self.download_papers(unique_papers)
            logger.info(f"下载完成，文件保存在: {self.config.download_dir}")
        
        logger.info("PaperCrawler运行完成！")
        return unique_papers
    
    def _remove_duplicates(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去除重复论文"""
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            title = paper.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)
        
        return unique_papers
    
    def _save_paper_info(self, papers: List[Dict[str, Any]]):
        """保存论文信息到文件"""
        import json
        
        output_file = os.path.join(self.config.output_dir, 'crawled_papers.json')
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        
        logger.info(f"论文信息已保存到: {output_file}")


def main():
    """主函数"""
    try:
        config = Config()
        crawler = PaperCrawler(config)
        
        # 可以通过命令行参数指定爬取源或目标URL
        source_type = 'all'  # 'rss', 'arxiv', 'all'
        target_url = None
        
        if len(sys.argv) > 1:
            if sys.argv[1].startswith('http'):
                # 如果第一个参数是URL，则爬取指定网页
                target_url = sys.argv[1]
                source_type = 'web'
            else:
                # 否则使用指定的源类型
                source_type = sys.argv[1]
        
        papers = crawler.run(source_type, target_url)
        print(f"\n爬取完成！共获取 {len(papers)} 篇论文信息")
        
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 