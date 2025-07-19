#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页爬取模块
支持从特定网页爬取论文信息
"""

import requests
import re
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

logger = logging.getLogger(__name__)


class WebCrawler:
    """网页爬取器"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
    
    def crawl_webpage(self, url: str) -> List[Dict[str, Any]]:
        """爬取单个网页的论文信息"""
        papers = []
        
        try:
            logger.info(f"开始爬取网页: {url}")
            
            # 获取网页内容
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 根据网页结构提取论文信息
            papers = self._extract_papers_from_html(soup, url)
            
            logger.info(f"网页爬取完成，获取 {len(papers)} 篇论文")
            
        except Exception as e:
            logger.error(f"爬取网页 {url} 失败: {e}")
        
        return papers
    
    def _extract_papers_from_html(self, soup, base_url: str) -> List[Dict[str, Any]]:
        """从HTML中提取论文信息"""
        papers = []
        
        # 这里需要根据具体网页结构来编写提取逻辑
        # 以下是通用示例，您需要根据实际网页调整
        
        # 示例1: 查找所有论文链接
        paper_links = soup.find_all('a', href=re.compile(r'\.pdf$|paper|article'))
        
        for link in paper_links:
            try:
                title = link.get_text(strip=True)
                if not title:
                    title = link.get('title', '')
                
                href = link.get('href')
                if href:
                    paper_url = urljoin(base_url, href)
                    
                    # 尝试提取PDF链接
                    pdf_url = self._extract_pdf_url(link, base_url)
                    
                    paper_info = {
                        'title': title,
                        'authors': [],  # 需要根据网页结构提取
                        'summary': '',  # 需要根据网页结构提取
                        'link': paper_url,
                        'pdf_url': pdf_url,
                        'source': base_url,
                        'crawl_time': datetime.now().isoformat()
                    }
                    
                    if self._is_valid_paper(paper_info):
                        papers.append(paper_info)
                        
            except Exception as e:
                logger.warning(f"提取论文信息失败: {e}")
                continue
        
        return papers
    
    def _extract_pdf_url(self, link_element, base_url: str) -> Optional[str]:
        """提取PDF链接"""
        # 检查链接本身是否是PDF
        href = link_element.get('href', '')
        if href.lower().endswith('.pdf'):
            return urljoin(base_url, href)
        
        # 检查是否有PDF相关的链接
        pdf_links = link_element.find_all('a', href=re.compile(r'\.pdf$'))
        if pdf_links:
            return urljoin(base_url, pdf_links[0].get('href'))
        
        return None
    
    def _is_valid_paper(self, paper_info: Dict[str, Any]) -> bool:
        """验证论文信息是否有效"""
        title = paper_info.get('title', '')
        
        # 检查标题长度
        if len(title) < self.config.min_title_length:
            return False
        
        # 检查是否包含排除关键词
        title_lower = title.lower()
        for keyword in self.config.exclude_keywords:
            if keyword.lower() in title_lower:
                return False
        
        return True


# 如果您知道具体的网页结构，可以创建专门的爬取器
class SpecificWebCrawler(WebCrawler):
    """特定网站的爬取器"""
    
    def _extract_papers_from_html(self, soup, base_url: str) -> List[Dict[str, Any]]:
        """根据特定网站结构提取论文信息"""
        papers = []
        
        # 在这里添加针对特定网站的提取逻辑
        # 例如：
        
        # 查找论文容器
        paper_containers = soup.find_all('div', class_='paper-item')  # 根据实际class调整
        
        for container in paper_containers:
            try:
                # 提取标题
                title_elem = container.find('h3')  # 根据实际标签调整
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # 提取作者
                author_elem = container.find('span', class_='author')  # 根据实际class调整
                authors = [author_elem.get_text(strip=True)] if author_elem else []
                
                # 提取链接
                link_elem = container.find('a')
                link = urljoin(base_url, link_elem.get('href')) if link_elem else ''
                
                # 提取PDF链接
                pdf_elem = container.find('a', href=re.compile(r'\.pdf$'))
                pdf_url = urljoin(base_url, pdf_elem.get('href')) if pdf_elem else None
                
                paper_info = {
                    'title': title,
                    'authors': authors,
                    'summary': '',
                    'link': link,
                    'pdf_url': pdf_url,
                    'source': base_url,
                    'crawl_time': datetime.now().isoformat()
                }
                
                if self._is_valid_paper(paper_info):
                    papers.append(paper_info)
                    
            except Exception as e:
                logger.warning(f"提取论文信息失败: {e}")
                continue
        
        return papers 