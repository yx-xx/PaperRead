from pdf_reader import get_pdf_files, extract_text_from_pdf, get_processed_files

# from qwen_api import analyze_paper_with_qwen
from glm_api import analyze_paper_with_glm

from result_writer import append_result_to_excel, EXCEL_COLUMNS
import os
from tqdm import tqdm


def main():
    processed_files = get_processed_files()
    pdf_files = get_pdf_files(processed_files=processed_files)

    # 创建进度条
    progress_bar = tqdm(pdf_files, desc="处理论文PDF")

    for pdf_path in progress_bar:
        file_name = os.path.basename(pdf_path)
        progress_bar.set_description(f"处理: {file_name[:20]}...")

        try:
            text = extract_text_from_pdf(pdf_path)
            progress_bar.set_description(f"分析: {file_name[:20]}...")
            print("\n" + "-"*50)
            print(f"开始分析: {file_name}")


            # analysis = analyze_paper_with_qwen(text, pdf_filename=file_name)
            analysis = analyze_paper_with_glm(text, pdf_filename=file_name)


            if analysis is None:
                print("分析失败，结果为空")
                analysis = {col: "" for col in EXCEL_COLUMNS}

            analysis["PDF文件名称"] = file_name
            append_result_to_excel(analysis)
            print(f"已完成，结果已保存到 {os.path.abspath('PaperRead_result.xlsx')}")

        except Exception as e:
            print(f"处理 {file_name} 时出错: {e}")
            # 记录错误文件
            with open("error_log.txt", "a") as log:
                log.write(f"{file_name}: {str(e)}\n")


if __name__ == "__main__":
    main() 
