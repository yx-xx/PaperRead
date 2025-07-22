import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import numpy as np
from config import VIS_METHOD, LABEL_DENSITY, PLOT_SIZE, PLOT_FILE
import matplotlib.font_manager as fm
import os

# 找不到字体就很头疼，被迫添加丑陋函数
def get_system_chinese_font():
    """获取系统中文字体（优化版）"""
    try:
        # 首选方法：使用Matplotlib的语言选择
        return fm.FontProperties(family='sans-serif', language='zh')
    except Exception as e:
        print(f"警告：无法获取系统中文默认字体 ({e})")
    
    # 备选方法：尝试已知字体路径
    fallback_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/arphic-uming/uming.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    ]
    
    for path in fallback_paths:
        if os.path.exists(path):
            return fm.FontProperties(fname=path)
    
    # 最终回退
    print("警告：未找到合适的中文字体，使用默认字体")
    return fm.FontProperties()

def visualize_clusters(X, labels, keywords):
    """聚类结果可视化 - 安全版本（不影响系统字体设置）"""
    # 获取系统自带的中文字体（不下载新字体）
    chinese_font = get_system_chinese_font()
    
    # 降维处理
    if VIS_METHOD == "tsne":
        reducer = TSNE(n_components=2, random_state=42)
        reduced = reducer.fit_transform(X.toarray() if hasattr(X, 'toarray') else X)
        method_name = "t-SNE"
    else:
        reducer = PCA(n_components=2, random_state=42)
        reduced = reducer.fit_transform(X.toarray() if hasattr(X, 'toarray') else X)
        method_name = "PCA"
    
    # 创建可视化
    plt.figure(figsize=PLOT_SIZE)
    scatter = plt.scatter(
        reduced[:, 0], reduced[:, 1],
        c=labels, cmap='viridis', 
        alpha=0.6, edgecolors='w', 
        s=60
    )
    
    # 标注策略：簇中心点 + 随机样本
    label_points = []
    label_texts = []
    
    # 1. 标注每个簇的中心点
    for cluster_id in np.unique(labels):
        cluster_mask = (labels == cluster_id)
        cluster_points = reduced[cluster_mask]
        
        if len(cluster_points) > 0:
            centroid = np.mean(cluster_points, axis=0)
            dists = np.linalg.norm(cluster_points - centroid, axis=1)
            centroid_idx = np.argmin(dists)
            
            # 获取原始数据中的全局索引
            global_idx = np.where(cluster_mask)[0][centroid_idx]
            label_points.append(reduced[global_idx])
            label_texts.append(keywords[global_idx])
    
    # 2. 添加额外随机标签
    n_additional = int(LABEL_DENSITY * len(keywords))
    additional_indices = np.random.choice(len(keywords), n_additional, replace=False)
    
    for idx in additional_indices:
        label_points.append(reduced[idx])
        label_texts.append(keywords[idx])
    
    # 创建标注对象（避免重复）
    unique_texts = {}
    points_to_plot = []
    texts_to_plot = []
    for point, text in zip(label_points, label_texts):
        if text not in unique_texts:
            unique_texts[text] = True
            points_to_plot.append(point)
            texts_to_plot.append(text)
    
    # 添加标注 - 仅在此处应用字体（不影响系统）
    for point, text in zip(points_to_plot, texts_to_plot):
        plt.annotate(
            text, 
            point, 
            fontsize=9, 
            alpha=0.8,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7),
            fontproperties=chinese_font  # 应用选择的字体
        )
    
    # 标题 - 也应用选择的字体
    title = f'关键词聚类可视化 ({method_name}降维)'
    plt.title(title, fontproperties=chinese_font)
    
    plt.colorbar(scatter, label='聚类簇')
    plt.xticks([])
    plt.yticks([])
    plt.grid(alpha=0.1)
    
    # 保存结果（不会修改系统设置）
    plt.savefig(PLOT_FILE, dpi=300, bbox_inches='tight')
    print(f"可视化结果已保存至: {PLOT_FILE}")
    plt.show()
