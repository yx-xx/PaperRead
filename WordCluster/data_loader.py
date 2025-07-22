import pandas as pd
from config import INPUT_FILE, COLUMN_NAME

def load_keywords():
    """从Excel文件中读取关键词列"""
    try:
        df = pd.read_excel(INPUT_FILE)
        return df[COLUMN_NAME].tolist()
    except Exception as e:
        print(f"数据加载错误: {e}")
        return []