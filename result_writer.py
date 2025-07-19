import pandas as pd
from config import OUTPUT_EXCEL
import os

EXCEL_COLUMNS = [
    "PDF文件名称", "论文标题", "研究主题关键词", "应用场景关键词", "主要方法关键词", "创新点关键词", "主要结论关键词"
]

def append_result_to_excel(result, output_file=OUTPUT_EXCEL):
    """
    将单篇论文的分析结果追加为Excel的一行。
    :param result: Dict 单篇论文的分析结果
    :param output_file: 输出Excel文件名
    """
    import openpyxl
    # 检查文件是否存在
    if not os.path.exists(output_file):
        # 新建文件并写入表头和第一行
        df = pd.DataFrame([result])
        df = df.reindex(columns=EXCEL_COLUMNS)
        df.to_excel(output_file, index=False)
    else:
        # 追加一行
        wb = openpyxl.load_workbook(output_file)
        ws = wb.active
        row = [result.get(col, "") for col in EXCEL_COLUMNS]
        if ws is not None:
            ws.append(row)
            wb.save(output_file) 


