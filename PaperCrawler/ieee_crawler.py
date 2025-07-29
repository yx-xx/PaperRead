#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
针对IEEE会议的爬取器（ICRA、IROS等）
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class IEEEConferenceCrawler:
    """IEEE会议论文爬取器"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        if hasattr(config, 'ieee_api_key'):
            self.session.headers.update({
                'Authorization': config.ieee_api_key
            })
    
    def crawl_conference_papers(self, conference: str, year: int) -> List[Dict[str, Any]]:
        """爬取指定会议和年份的论文"""
        papers = []
        
        try:
            # IEEE Xplore API的基础URL
            base_url = "http://ieeexploreapi.ieee.org/api/v1/search/articles"
            
            # 构建查询参数
            params = {
                'queryText': f'"{conference} {year}"',
                'content_type': 'Conferences',
                'max_records': 200,  # 每页返回的最大记录数
                'start_record': 1
            }
            
            while True:
                response = self.session.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'articles' not in data:
                    break
                
                for article in data['articles']:
                    paper = {
                        'title': article.get('title', ''),
                        'authors': [author.get('full_name', '') for author in article.get('authors', [])],
                        'abstract': article.get('abstract', ''),
                        'doi': article.get('doi', ''),
                        'url': f"https://doi.org/{article.get('doi', '')}",
                        'conference': conference,
                        'year': year,
                        'publication_date': article.get('publication_date', ''),
                        'keywords': article.get('index_terms', {}).get('ieee_terms', []),
                    }
                    papers.append(paper)
                
                # 检查是否还有更多记录
                if len(papers) >= data.get('total_records', 0):
                    break
                    
                params['start_record'] += params['max_records']
                
            logger.info(f"成功爬取 {conference} {year} 的 {len(papers)} 篇论文")
            
        except Exception as e:
            logger.error(f"爬取 {conference} {year} 论文时出错: {str(e)}")
        
        return papers
