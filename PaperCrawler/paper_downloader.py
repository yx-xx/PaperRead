#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文下载模块
支持下载论文PDF文件
"""

import os
import requests
import re
import logging
from typing import Optional
from urllib.parse import urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class PaperDownloader:
    """论文下载器"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
        
        # 确保下载目录存在
        os.makedirs(self.config.download_dir, exist_ok=True)
    
    def download_paper(self, pdf_url: str, title: str) -> Optional[str]:
        """下载单篇论文"""
        try:
            if not pdf_url:
                logger.warning(f"论文 {title} 没有PDF链接")
                return None
            
            # 生成文件名
            filename = self._generate_filename(title)
            file_path = os.path.join(self.config.download_dir, filename)
            
            # 检查文件是否已存在
            if os.path.exists(file_path):
                logger.info(f"文件已存在: {filename}")
                return file_path
            
            # 下载文件
            logger.info(f"开始下载: {title}")
            response = self.session.get(
                pdf_url, 
                timeout=self.config.download_timeout,
                stream=True
            )
            response.raise_for_status()
            
            # 检查文件大小
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.config.max_download_size:
                logger.warning(f"文件过大，跳过下载: {title}")
                return None
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"下载完成: {filename}")
            return file_path
            
        except Exception as e:
            logger.error(f"下载论文失败 {title}: {e}")
            return None
    
    def download_multiple_papers(self, papers: list) -> list:
        """批量下载论文"""
        downloaded_files = []
        
        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=self.config.max_concurrent_downloads) as executor:
            # 提交下载任务
            future_to_paper = {}
            for paper in papers:
                if paper.get('pdf_url'):
                    future = executor.submit(
                        self.download_paper, 
                        paper['pdf_url'], 
                        paper.get('title', 'unknown')
                    )
                    future_to_paper[future] = paper
            
            # 收集结果
            for future in as_completed(future_to_paper):
                paper = future_to_paper[future]
                try:
                    file_path = future.result()
                    if file_path:
                        downloaded_files.append(file_path)
                except Exception as e:
                    logger.error(f"下载失败 {paper.get('title', 'unknown')}: {e}")
        
        return downloaded_files
    
    def _generate_filename(self, title: str) -> str:
        """生成文件名"""
        # 清理标题
        filename = title.strip()
        
        # 替换非法字符
        for old_char, new_char in self.config.replace_chars.items():
            filename = filename.replace(old_char, new_char)
        
        # 限制长度
        if len(filename) > self.config.filename_max_length:
            filename = filename[:self.config.filename_max_length]
        
        # 添加.pdf扩展名
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        return filename
    
    def _is_valid_pdf_url(self, url: str) -> bool:
        """验证PDF URL是否有效"""
        if not url:
            return False
        
        # 检查URL格式
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # 检查是否是PDF链接
        if not url.lower().endswith('.pdf'):
            return False
        
        return True
    
    def get_file_size(self, file_path: str) -> int:
        """获取文件大小"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def cleanup_invalid_files(self):
        """清理无效文件"""
        try:
            for filename in os.listdir(self.config.download_dir):
                file_path = os.path.join(self.config.download_dir, filename)
                
                # 检查文件大小
                if self.get_file_size(file_path) < 1024:  # 小于1KB的文件可能是无效的
                    try:
                        os.remove(file_path)
                        logger.info(f"删除无效文件: {filename}")
                    except OSError:
                        pass
                        
        except Exception as e:
            logger.error(f"清理文件失败: {e}")
    
    def get_download_stats(self) -> dict:
        """获取下载统计信息"""
        try:
            total_files = 0
            total_size = 0
            
            for filename in os.listdir(self.config.download_dir):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(self.config.download_dir, filename)
                    file_size = self.get_file_size(file_path)
                    total_files += 1
                    total_size += file_size
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'download_dir': self.config.download_dir
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {} 