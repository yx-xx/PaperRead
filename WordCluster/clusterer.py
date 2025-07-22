from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from config import CLUSTER_ALGORITHM, N_CLUSTERS, RANDOM_STATE
import numpy as np

def cluster_texts(X):
    """对文本向量进行聚类"""
    if CLUSTER_ALGORITHM == "kmeans":
        kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE)
        labels = kmeans.fit_predict(X)
        
        # 计算轮廓系数
        if X.shape[0] > 1000:  # 大数据集样本抽样
            sample_size = min(1000, X.shape[0])
            sample_idx = np.random.choice(X.shape[0], sample_size, replace=False)
            score = silhouette_score(X[sample_idx], labels[sample_idx])
        else:
            score = silhouette_score(X, labels)
        
        print(f"K-Means聚类完成, 轮廓系数: {score:.3f}")
        return labels
    
    elif CLUSTER_ALGORITHM == "dbscan":
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        labels = dbscan.fit_predict(X)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        print(f"DBSCAN聚类完成, 识别出 {n_clusters} 个簇")
        return labels
    
    else:
        raise ValueError(f"不支持的聚类算法: {CLUSTER_ALGORITHM}")
        