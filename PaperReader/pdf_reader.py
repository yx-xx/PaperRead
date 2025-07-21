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
    只做基础清理，保留纯文本：
    1. 移除图片标签
    2. 移除URL
    3. 移除引用标记
    4. 移除公式
    5. 合并多余空行
    """
    # 移除图片标签
    text = re.sub(r'<img[^>]*alt="([^"]+)"[^>]*>', '', text)
    # 移除URL
    text = re.sub(r'https?://\S+', '', text)
    # 移除引用标记
    text = re.sub(r'\[\d+\]', '', text)
    # 移除公式
    text = re.sub(r'\$(.*?)\$', '', text)
    # 合并多余空行
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def extract_text_from_pdf(pdf_path):
    """仅用PyMuPDF提取PDF文本，保证最大化提取纯文本"""
    text = ""
    filename = os.path.basename(pdf_path)
    try:
        doc = fitz.open(pdf_path)
        for i in range(doc.page_count):
            page = doc.load_page(i)
            text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"{filename} PyMuPDF提取失败: {e}")
        return ""
    return clean_extracted_text(text)