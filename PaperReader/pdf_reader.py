import os
import pdfplumber
from config import PDF_FOLDER, OUTPUT_EXCEL
import pandas as pd

def get_processed_files():
    if not os.path.exists(OUTPUT_EXCEL):
        return set()
    df = pd.read_excel(OUTPUT_EXCEL)
    return set(df["PDF文件名称"].astype(str))

def get_pdf_files(folder=PDF_FOLDER, processed_files=None):
    """获取指定文件夹下所有未处理PDF文件的路径和文件名"""
    pdf_files = []
    for file in os.listdir(folder):
        if file.lower().endswith('.pdf'):
            if processed_files is not None and file in processed_files:
                continue
            pdf_files.append(os.path.join(folder, file))
    return pdf_files

def extract_text_from_pdf(pdf_path):
    """提取单个PDF文件的全部文本内容"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text 