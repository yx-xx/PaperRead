import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import numpy as np
from config import VIS_METHOD, LABEL_DENSITY, PLOT_SIZE, PLOT_FILE

def visualize_clusters(X, labels, keywords):
    """聚类结果可视化"""
    # 降维处理
    if VIS_METHOD == "tsne":
        reducer = TSNE(n_components=2, random_state=42)
        reduced = reducer.fit_transform(X.toarray())
        method_name = "t-SNE"
    else:
        reducer = PCA(n_components=2, random_state=42)
        reduced = reducer.fit_transform(X.toarray())
        method_name = "PCA"
    
    # 创建可视化
    plt.figure(figsize=PLOT_SIZE)
    scatter = plt.scatter(reduced[:,0], reduced[:,1], 
                         c=labels, cmap='viridis', 
                         alpha=0.6, edgecolors='w', 
                         s=60)
    
    # 添加部分标签
    label_indices = []
    for cluster in np.unique(labels):
        cluster_points = np.where(labels == cluster)[0]
        if len(cluster_points) > 0:
            # 选择每个簇的中心点作为代表
            centroid_idx = np.argmin(
                np.linalg.norm(reduced[cluster_points] - 
                              np.mean(reduced[cluster_points], axis=0), axis=1)
            )
            label_indices.append(cluster_points[centroid_idx])
    
    # 添加额外随机标签
    additional_samples = int(LABEL_DENSITY * len(keywords))
    random_indices = np.random.choice(len(keywords), additional_samples, replace=False)
    label_indices = list(set(label_indices).union(set(random_indices)))
    
    # 标注标签
    for i in label_indices:
        plt.annotate(keywords[i], (reduced[i,0], reduced[i,1]), 
                    fontsize=9, alpha=0.8,
                    bbox=dict(boxstyle="round,pad=0.3", 
                             fc="white", ec="gray", alpha=0.7))
    
    plt.colorbar(scatter, label='聚类簇')
    plt.title(f'关键词聚类可视化 ({method_name}降维)')
    plt.xticks([])
    plt.yticks([])
    plt.grid(alpha=0.1)
    plt.savefig(PLOT_FILE, dpi=300, bbox_inches='tight')
    plt.show()
