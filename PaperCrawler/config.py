#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaperCrawler配置文件
"""

import os
from typing import List

class Config:
    """配置类"""
    
    def __init__(self):
        # 基础路径配置
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # 使用项目根目录的Data/PC_Data文件夹
        project_root = os.path.dirname(self.base_dir)  # 回到项目根目录
        self.output_dir = os.path.join(project_root, 'Data', 'PC_Data', 'output')
        self.download_dir = os.path.join(project_root, 'Data', 'PC_Data', 'downloads')
        self.log_dir = os.path.join(project_root, 'Data', 'PC_Data', 'logs')
        
        # 创建必要的目录
        for dir_path in [self.output_dir, self.download_dir, self.log_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # RSS源配置
        self.rss_sources = [
            # # arXiv RSS源
            # 'http://export.arxiv.org/rss/cs.AI',  # 人工智能
            # 'http://export.arxiv.org/rss/cs.CV',  # 计算机视觉
            # 'http://export.arxiv.org/rss/cs.LG',  # 机器学习
            # 'http://export.arxiv.org/rss/cs.RO',  # 机器人学
            # 'http://export.arxiv.org/rss/cs.CL',  # 计算语言学
            
            # # Nature RSS源
            # 'https://www.nature.com/subjects/computer-science.rss',
            # 'https://www.nature.com/subjects/artificial-intelligence.rss',
            
            # # Science RSS源
            # 'https://www.science.org/rss/news_current.xml',
            
            # # IEEE RSS源
            # 'https://ieeexplore.ieee.org/rss/TOC18836.xml',  # IEEE Transactions on Pattern Analysis and Machine Intelligence
            
            # # ACM RSS源
            # 'https://dl.acm.org/rss/feed_ccs.xml',
            
        ]
        
        # 网页爬取配置
        self.web_sources = [
            # 'https://roboticsconference.org/program/papers/',
            'https://roboticsconference.org/2024/program/papers/',

        ]
        
        # arXiv配置
        self.arxiv_categories = [
            # 'cs.AI',    # 人工智能
            # 'cs.CV',    # 计算机视觉
            # 'cs.LG',    # 机器学习
            # 'cs.RO',    # 机器人学
            # 'cs.CL',    # 计算语言学
            # 'cs.NE',    # 神经计算
            # 'cs.SE',    # 软件工程
        ]
        
        # 下载配置
        self.auto_download = True  # 是否自动下载PDF
        self.max_download_size = 500 * 1024 * 1024  # 最大下载文件大小 (500MB)
        self.download_timeout = 30  # 下载超时时间 (秒)
        self.max_concurrent_downloads = 3  # 最大并发下载数
        
        # 爬取配置
        self.max_papers_per_source = 100  # 每个源最大爬取论文数
        self.crawl_delay = 1  # 爬取间隔 (秒)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        # 过滤配置
        self.min_title_length = 10  # 最小标题长度
        self.exclude_keywords = [
            'correction', 'erratum', 'addendum', 'retraction',
            '勘误', '更正', '撤回', '补充'
        ]
        
        # 文件命名配置
        self.filename_max_length = 100  # 文件名最大长度
        self.replace_chars = {
            '<': '', '>': '', ':': '', '"': '', '/': '', '\\': '', 
            '|': '', '?': '', '*': '', '\n': ' ', '\r': ' ', '\t': ' '
        } 