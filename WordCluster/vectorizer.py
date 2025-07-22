from sklearn.feature_extraction.text import TfidfVectorizer
from config import N_CLUSTERS

def vectorize_texts(texts):
    """使用TF-IDF将文本转换为向量"""
    # 设置最大特征数以优化性能
    max_features = min(5000, max(len(texts)*2, 2000))
    
    vectorizer = TfidfVectorizer(max_features=max_features)
    X = vectorizer.fit_transform(texts)
    
    # 输出特征统计
    print(f"文本向量化完成：{X.shape[0]}个关键词, {X.shape[1]}个特征")
    return X, vectorizer
