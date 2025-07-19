#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS爬取模块
支持从各种RSS源爬取论文信息
"""

import requests
import feedparser
import re
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import html

logger = logging.getLogger(__name__)


class RSSCrawler:
    """RSS爬取器"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
    
    def crawl_rss(self, rss_url: str) -> List[Dict[str, Any]]:
        """爬取单个RSS源"""
        papers = []
        
        try:
            logger.info(f"开始爬取RSS: {rss_url}")
            
            # 获取RSS内容
            response = self.session.get(rss_url, timeout=30)
            response.raise_for_status()
            
            # 解析RSS
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries[:self.config.max_papers_per_source]:
                try:
                    paper_info = self._parse_rss_entry(entry, rss_url)
                    if paper_info and self._is_valid_paper(paper_info):
                        papers.append(paper_info)
                except Exception as e:
                    logger.warning(f"解析RSS条目失败: {e}")
                    continue
            
            logger.info(f"RSS {rss_url} 爬取完成，获取 {len(papers)} 篇论文")
            
        except Exception as e:
            logger.error(f"爬取RSS {rss_url} 失败: {e}")
        
        return papers
    
    def _parse_rss_entry(self, entry, rss_url: str) -> Optional[Dict[str, Any]]:
        """解析RSS条目"""
        try:
            # 提取基本信息
            title = self._clean_text(entry.get('title', ''))
            if not title:
                return None
            
            # 提取链接
            link = entry.get('link', '')
            if not link:
                return None
            
            # 提取摘要
            summary = self._clean_text(entry.get('summary', ''))
            
            # 提取发布时间
            published = entry.get('published', '')
            if published:
                try:
                    published_date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')
                except:
                    published_date = datetime.now()
            else:
                published_date = datetime.now()
            
            # 提取作者
            authors = []
            if hasattr(entry, 'authors'):
                authors = [author.get('name', '') for author in entry.authors]
            elif hasattr(entry, 'author'):
                authors = [entry.author]
            
            # 尝试提取PDF链接
            pdf_url = self._extract_pdf_url(entry, link)
            
            # 提取DOI
            doi = self._extract_doi(entry, link)
            
            paper_info = {
                'title': title,
                'authors': authors,
                'summary': summary,
                'link': link,
                'pdf_url': pdf_url,
                'doi': doi,
                'published_date': published_date.isoformat(),
                'source': rss_url,
                'crawl_time': datetime.now().isoformat()
            }
            
            return paper_info
            
        except Exception as e:
            logger.warning(f"解析RSS条目失败: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # HTML解码
        text = html.unescape(text)
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_pdf_url(self, entry, link: str) -> Optional[str]:
        """提取PDF链接"""
        # 方法1: 从链接中查找
        if 'arxiv.org' in link:
            # arXiv链接转换为PDF链接
            arxiv_id = link.split('/')[-1]
            return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        # 方法2: 从摘要中查找PDF链接
        summary = entry.get('summary', '')
        pdf_match = re.search(r'href=["\']([^"\']*\.pdf)["\']', summary)
        if pdf_match:
            pdf_url = pdf_match.group(1)
            if not pdf_url.startswith('http'):
                pdf_url = urljoin(link, pdf_url)
            return pdf_url
        
        # 方法3: 从链接中查找PDF
        if link.endswith('.pdf'):
            return link
        
        return None
    
    def _extract_doi(self, entry, link: str) -> Optional[str]:
        """提取DOI"""
        # 从链接中提取DOI
        doi_match = re.search(r'doi\.org/([^/\s]+)', link)
        if doi_match:
            return doi_match.group(1)
        
        # 从摘要中提取DOI
        summary = entry.get('summary', '')
        doi_match = re.search(r'doi\.org/([^/\s]+)', summary)
        if doi_match:
            return doi_match.group(1)
        
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
    
    def crawl_multiple_rss(self, rss_urls: List[str]) -> List[Dict[str, Any]]:
        """爬取多个RSS源"""
        all_papers = []
        
        for rss_url in rss_urls:
            try:
                papers = self.crawl_rss(rss_url)
                all_papers.extend(papers)
                
                # 添加延迟避免请求过快
                time.sleep(self.config.crawl_delay)
                
            except Exception as e:
                logger.error(f"爬取RSS源 {rss_url} 失败: {e}")
                continue
        
        return all_papers 