import time
import pandas as pd
from config import OUTPUT_FILE, PLOT_FILE
from data_loader import load_keywords
from preprocessor import preprocess_texts
from vectorizer import vectorize_texts
from clusterer import cluster_texts
from visualizer import visualize_clusters

def main():
    print("=== 关键词聚类分析 ===")
    start_time = time.time()
    
    # 1. 加载数据
    print("加载关键词数据...")
    raw_keywords = load_keywords()
    print(f"成功加载 {len(raw_keywords)} 个关键词")
    
    # 2. 文本预处理
    print("文本预处理(分词+去停用词)...")
    processed_texts = preprocess_texts(raw_keywords)
    
    # 3. 向量化
    print("文本向量化...")
    X, vectorizer = vectorize_texts(processed_texts)
    
    # 4. 聚类
    print("执行聚类算法...")
    labels = cluster_texts(X)
    
    # 5. 结果可视化
    print("生成可视化图表...")
    visualize_clusters(X, labels, raw_keywords)
    
    # 6. 保存结果
    result_df = pd.DataFrame({
        '关键词': raw_keywords,
        '类别': labels,
        '处理后的文本': processed_texts
    })
    result_df.to_excel(OUTPUT_FILE, index=False)
    
    # 完成统计
    elapsed = time.time() - start_time
    print(f"处理完成! 耗时: {elapsed:.2f}秒")
    print(f"- 结果文件: {OUTPUT_FILE}")
    print(f"- 可视化图: {PLOT_FILE}")

if __name__ == "__main__":
    main()