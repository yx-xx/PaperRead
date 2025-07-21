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

def is_formula_line(line):
    # 公式/变量行通常包含大量特殊符号或变量名
    formula_symbols = r'[=+\-*/^_{}\\[\\]()<>|]'
    # 如果特殊符号比例很高，或行内有明显变量定义、编号等
    symbols = re.findall(formula_symbols, line)
    if len(symbols) / max(len(line), 1) > 0.2:
        return True
    # 行内有明显变量定义、编号等
    if re.match(r'^[A-Za-z0-9_\-]+(\s*[=,:])', line):
        return True
    # 行内有大量数字和符号，且英文字符很少
    if len(re.findall(r'[A-Za-z]', line)) < 0.3 * len(line):
        return True
    # 行很短或很长也可能是乱码/公式
    if len(line) < 8 or len(line) > 200:
        return True
    return False

def clean_extracted_text(text):
    """
    针对英文文献进一步优化：
    1. 过滤公式/变量/伪代码/编号/表格等非自然语言内容
    2. 只保留英文自然语言句子
    3. 合并多余空行
    """
    # 先做基础清理
    text = re.sub(r'<img[^>]*alt="([^"]+)"[^>]*>', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\$.*?\$', '', text)
    text = re.sub(r'\\\[.*?\\\]', '', text)
    text = re.sub(r'\\\(.*?\\\)', '', text)
    # 只保留常用英文标点和字母、数字、空格
    text = re.sub(r'[^A-Za-z0-9,.!?;:\'"\-()\[\]{}<>\s]', '', text)
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if is_formula_line(line):
            continue
        clean_lines.append(line)
    return '\n'.join(clean_lines)

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
    