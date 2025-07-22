# 核心配置参数
INPUT_FILE = "keywords.xlsx"     # 输入Excel文件路径
COLUMN_NAME = "关键词"           # 包含关键词的列名
OUTPUT_FILE = "classified_keywords.xlsx"  # 分类结果输出
PLOT_FILE = "cluster_visualization.png"   # 可视化图像输出

# 文本处理配置
STOPWORDS_FILE = "stopwords.txt"        # 停用词文件路径
USE_CUSTOM_DICT = False                # 是否使用自定义词典
CUSTOM_DICT_PATH = "custom_dict.txt"   # 自定义词典路径

# 聚类算法配置
CLUSTER_ALGORITHM = "kmeans"          # 可选: kmeans, dbscan
N_CLUSTERS = 5                        # 聚类数量
RANDOM_STATE = 42                     # 随机种子

# 可视化配置
VIS_METHOD = "tsne"                   # 可视化方法: tsne 或 pca
LABEL_DENSITY = 0.3                   # 标签显示密度(0-1)
PLOT_SIZE = (12, 8)                   # 图像尺寸
