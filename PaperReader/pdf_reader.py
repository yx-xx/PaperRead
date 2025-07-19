import os
import pdfplumber
import fitz
import re
import pandas as pd
from config import PDF_FOLDER, OUTPUT_EXCEL

def get_processed_files():
    """获取已处理文件列表"""
    if os.path.exists(OUTPUT_EXCEL):
        try:
            df = pd.read_excel(OUTPUT_EXCEL)
            return set(df["PDF文件名称"].astype(str))
        except:
            return set()
    return set()

def get_pdf_files(folder=PDF_FOLDER, processed_files=None):
    """获取未处理PDF文件列表"""
    return [
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.lower().endswith('.pdf') 
        and (processed_files is None or f not in processed_files)
    ]

def clean_extracted_text(text):
    """
    文本净化处理：
    1. 移除图片标签保留caption
    2. 过滤元数据
    3. 公式标准化
    """
    # 提取并保留图片描述
    text = re.sub(r'<img[^>]*alt="([^"]+)"[^>]*>', r'[Image: \1]', text)
    
    # 移除URL和作者列表
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'^[\w\s]+,(\s*[\w\s]+,){5,}', '', text, flags=re.MULTILINE)
    
    # 过滤引用标记
    text = re.sub(r'\[\d+\]', '', text)
    
    # 标准化公式标记
    text = re.sub(r'\$(.*?)\$', r'[MATH: \1]', text)
    
    return text.strip()

def extract_text_from_pdf(pdf_path):
    """优化版PDF文本提取"""
    text = ""
    filename = os.path.basename(pdf_path)
    
    try:
        # 优先使用pdfplumber逐页提取
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
                except Exception as e:
                    print(f"{filename} 第{i+1}页pdfplumber解析失败: {e}")
                    # 失败时切换PyMuPDF提取当前页
                    try:
                        doc = fitz.open(pdf_path)
                        page = doc.load_page(i)
                        page_text = page.get_text("text") or ""
                        text += page_text + "\n"
                    except:
                        print(f"{filename} 第{i+1}页PyMuPDF也解析失败")
    except Exception as e:
        print(f"{filename} pdfplumber整体失败: {e}")
        # 整体失败时使用PyMuPDF
        try:
            doc = fitz.open(pdf_path)
            for i in range(doc.page_count):
                page = doc.load_page(i)
                text += page.get_text("text") + "\n"
        except Exception as fitz_e:
            print(f"{filename} PyMuPDF提取失败: {fitz_e}")
            return ""  # 双重失败返回空文本
    
    return clean_extracted_text(text)