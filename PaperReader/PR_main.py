from pdf_reader import get_pdf_files, extract_text_from_pdf, get_processed_files
# from .qwen_api import analyze_paper_with_qwen
from glm_api import analyze_paper_with_glm

from config import OUTPUT_EXCEL
from result_writer import append_result_to_excel, EXCEL_COLUMNS
import os
from tqdm import tqdm
import time

from colorama import Fore, Style, init as colorama_init
colorama_init(autoreset=True)


# 开线程显示分析动画，已经废弃
def analysis_spinner(progress_bar, idx, total, stop_event):
    spinner = '|/-\\'
    i = 0
    while not stop_event.is_set():
        progress_bar.set_postfix_str(f"[{idx}/{total}] 分析中 {spinner[i % len(spinner)]}")
        time.sleep(0.1)
        i += 1
    progress_bar.set_postfix_str("")


def main():
    processed_files = get_processed_files()
    pdf_files = get_pdf_files(processed_files=processed_files)

    # 创建进度条
    progress_bar = tqdm(pdf_files, desc="PaperReader处理论文")

    for idx, pdf_path in enumerate(progress_bar, 1):
        file_name = os.path.basename(pdf_path)

        ########### 阶段1：提取文本 ###########
        print(f"\n正在提取文本: {file_name}", flush=True)
        try:
            text = extract_text_from_pdf(pdf_path)

            ########### 阶段2：分析中 ###########
            print(f"开始分析: {file_name}", flush=True)
            # analysis = analyze_paper_with_qwen(text, pdf_filename=file_name)
            analysis = analyze_paper_with_glm(text, pdf_filename=file_name)

            if analysis is None:
                print(Fore.RED + "分析失败，结果为空" + Style.RESET_ALL, flush=True)
                analysis = {col: "" for col in EXCEL_COLUMNS}

            analysis["PDF文件名称"] = file_name

            ########### 阶段3：写入结果 ###########
            append_result_to_excel(analysis)
            print(Fore.GREEN + f"已完成，结果已保存到 {os.path.abspath(OUTPUT_EXCEL)}" + Style.RESET_ALL, flush=True)
        except Exception as e:
            print(Fore.RED + f"处理 {file_name} 时出错: {e}" + Style.RESET_ALL, flush=True)
            # 记录错误文件
            with open("error_log.txt", "a") as log:
                log.write(f"{file_name}: {str(e)}\n")


if __name__ == "__main__":
    main() 