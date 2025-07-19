#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门针对roboticsconference.org的爬取器
"""

import requests
import re
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class RoboticsConferenceCrawler:
    """专门针对roboticsconference.org的爬取器"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
    
    def crawl_conference_papers(self, base_url: str) -> List[Dict[str, Any]]:
        """爬取会议论文"""
        papers = []
        
        try:
            logger.info(f"开始爬取会议论文: {base_url}")
            
            # 获取主页面
            response = self.session.get(base_url, timeout=30)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找论文链接
            paper_links = self._find_paper_links(soup, base_url)
            
            logger.info(f"找到 {len(paper_links)} 个论文链接")
            
            # 访问每个论文页面获取详细信息
            for i, paper_link in enumerate(paper_links):
                try:
                    logger.info(f"处理论文 {i+1}/{len(paper_links)}: {paper_link}")
                    
                    paper_info = self._extract_paper_info(paper_link)
                    if paper_info and self._is_valid_paper(paper_info):
                        papers.append(paper_info)
                    
                    # 添加延迟避免请求过快
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"处理论文链接失败 {paper_link}: {e}")
                    continue
            
            logger.info(f"会议论文爬取完成，获取 {len(papers)} 篇论文")
            
        except Exception as e:
            logger.error(f"爬取会议论文失败: {e}")
        
        return papers
    
    def _find_paper_links(self, soup, base_url: str) -> List[str]:
        """查找论文链接"""
        paper_links = []
        
        # 查找所有可能的论文链接
        # 根据roboticsconference.org的结构调整
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            
            # 检查是否是论文链接
            if self._is_paper_link(href):
                full_url = urljoin(base_url, href)
                if full_url not in paper_links:
                    paper_links.append(full_url)
        
        return paper_links
    
    def _is_paper_link(self, href: str) -> bool:
        """判断是否是论文链接"""
        # 根据roboticsconference.org的URL模式调整
        patterns = [
            r'/program/papers/\d+/',  # 论文详情页
            r'/papers/\d+/',          # 论文页面
            r'paper\.pdf',            # 直接PDF链接
            r'\.pdf$',                # PDF文件
        ]
        
        for pattern in patterns:
            if re.search(pattern, href):
                return True
        
        return False
    
    def _extract_paper_info(self, paper_url: str) -> Optional[Dict[str, Any]]:
        """从论文页面提取信息"""
        try:
            response = self.session.get(paper_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title = self._extract_title(soup)
            
            # 提取作者
            authors = self._extract_authors(soup)
            
            # 提取PDF链接
            pdf_url = self._extract_pdf_url(soup, paper_url)
            
            # 提取摘要
            summary = self._extract_summary(soup)
            
            if title:
                return {
                    'title': title,
                    'authors': authors,
                    'summary': summary,
                    'link': paper_url,
                    'pdf_url': pdf_url,
                    'source': paper_url,
                    'crawl_time': datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.warning(f"提取论文信息失败 {paper_url}: {e}")
        
        return None
    
    def _extract_title(self, soup) -> str:
        """提取论文标题"""
        # 尝试多种方式提取标题
        title_selectors = [
            'h1', 'h2', 'h3',
            '.title', '.paper-title',
            '[class*="title"]', '[class*="paper"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 10:
                    return title
        
        return ""
    
    def _extract_authors(self, soup) -> List[str]:
        """提取作者信息"""
        authors = []
        
        # 尝试多种方式提取作者
        author_selectors = [
            '.author', '.authors',
            '[class*="author"]',
            'span[class*="author"]'
        ]
        
        for selector in author_selectors:
            author_elems = soup.select(selector)
            for elem in author_elems:
                author = elem.get_text(strip=True)
                if author and author not in authors:
                    authors.append(author)
        
        return authors
    
    def _extract_pdf_url(self, soup, base_url: str) -> Optional[str]:
        """提取PDF链接"""
        # 查找PDF链接
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$'))
        
        for link in pdf_links:
            href = link.get('href', '')
            if href.lower().endswith('.pdf'):
                return urljoin(base_url, href)
        
        # 查找包含"pdf"的链接
        pdf_links = soup.find_all('a', href=re.compile(r'pdf', re.IGNORECASE))
        
        for link in pdf_links:
            href = link.get('href', '')
            if 'pdf' in href.lower():
                return urljoin(base_url, href)
        
        return None
    
    def _extract_summary(self, soup) -> str:
        """提取论文摘要"""
        # 尝试多种方式提取摘要
        summary_selectors = [
            '.abstract', '.summary',
            '[class*="abstract"]', '[class*="summary"]'
        ]
        
        for selector in summary_selectors:
            summary_elem = soup.select_one(selector)
            if summary_elem:
                summary = summary_elem.get_text(strip=True)
                if summary and len(summary) > 20:
                    return summary
        
        return ""
    
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