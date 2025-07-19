#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv爬取模块
支持从arXiv搜索和爬取论文信息
"""

import requests
import re
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class ArxivCrawler:
    """arXiv爬取器"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
        self.base_url = "http://export.arxiv.org/api/query"
    
    def search_papers(self, query: Optional[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """搜索arXiv论文"""
        papers = []
        
        try:
            # 如果没有指定查询，使用默认分类
            if not query:
                for category in self.config.arxiv_categories:
                    papers.extend(self._search_by_category(category, max_results // len(self.config.arxiv_categories)))
            else:
                papers = self._search_by_query(query, max_results)
            
            logger.info(f"arXiv搜索完成，共获取 {len(papers)} 篇论文")
            
        except Exception as e:
            logger.error(f"arXiv搜索失败: {e}")
        
        return papers
    
    def _search_by_category(self, category: str, max_results: int) -> List[Dict[str, Any]]:
        """按分类搜索论文"""
        papers = []
        
        try:
            # 构建查询参数
            params = {
                'search_query': f'cat:{category}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            
            logger.info(f"搜索arXiv分类: {category}")
            
            # 发送请求
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析XML响应
            papers = self._parse_arxiv_xml(response.content)
            
            # 添加延迟
            time.sleep(self.config.crawl_delay)
            
        except Exception as e:
            logger.error(f"搜索arXiv分类 {category} 失败: {e}")
        
        return papers
    
    def _search_by_query(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """按关键词搜索论文"""
        papers = []
        
        try:
            # 构建查询参数
            params = {
                'search_query': query,
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            logger.info(f"搜索arXiv关键词: {query}")
            
            # 发送请求
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析XML响应
            papers = self._parse_arxiv_xml(response.content)
            
        except Exception as e:
            logger.error(f"搜索arXiv关键词 {query} 失败: {e}")
        
        return papers
    
    def _parse_arxiv_xml(self, xml_content: bytes) -> List[Dict[str, Any]]:
        """解析arXiv XML响应"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # 查找所有entry元素
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                try:
                    paper_info = self._parse_arxiv_entry(entry)
                    if paper_info and self._is_valid_paper(paper_info):
                        papers.append(paper_info)
                except Exception as e:
                    logger.warning(f"解析arXiv条目失败: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"解析arXiv XML失败: {e}")
        
        return papers
    
    def _parse_arxiv_entry(self, entry) -> Optional[Dict[str, Any]]:
        """解析arXiv条目"""
        try:
            # 提取标题
            title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
            title = self._clean_text(title_elem.text) if title_elem is not None else ""
            
            if not title:
                return None
            
            # 提取摘要
            summary_elem = entry.find('.//{http://www.w3.org/2005/Atom}summary')
            summary = self._clean_text(summary_elem.text) if summary_elem is not None else ""
            
            # 提取作者
            authors = []
            for author_elem in entry.findall('.//{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name'):
                if author_elem.text:
                    authors.append(author_elem.text.strip())
            
            # 提取ID (arXiv ID)
            id_elem = entry.find('.//{http://www.w3.org/2005/Atom}id')
            arxiv_id = ""
            if id_elem is not None and id_elem.text:
                arxiv_id = id_elem.text.split('/')[-1]
            
            # 提取发布时间
            published_elem = entry.find('.//{http://www.w3.org/2005/Atom}published')
            published_date = datetime.now()
            if published_elem is not None and published_elem.text:
                try:
                    published_date = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
                except:
                    pass
            
            # 提取分类
            categories = []
            for category_elem in entry.findall('.//{http://arxiv.org/schemas/atom}primary_category'):
                if category_elem.get('term'):
                    categories.append(category_elem.get('term'))
            
            # 构建PDF链接
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else None
            
            # 构建网页链接
            link = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None
            
            paper_info = {
                'title': title,
                'authors': authors,
                'summary': summary,
                'arxiv_id': arxiv_id,
                'categories': categories,
                'link': link,
                'pdf_url': pdf_url,
                'published_date': published_date.isoformat(),
                'source': 'arxiv',
                'crawl_time': datetime.now().isoformat()
            }
            
            return paper_info
            
        except Exception as e:
            logger.warning(f"解析arXiv条目失败: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
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
    
    def get_paper_by_id(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """根据arXiv ID获取论文信息"""
        try:
            params = {
                'id_list': arxiv_id,
                'start': 0,
                'max_results': 1
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            papers = self._parse_arxiv_xml(response.content)
            return papers[0] if papers else None
            
        except Exception as e:
            logger.error(f"获取arXiv论文 {arxiv_id} 失败: {e}")
            return None 