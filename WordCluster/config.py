# 核心配置参数
INPUT_FILE = "Data/PR_Data/PaperRead_RSS2025.xlsx"     # 输入Excel文件路径
COLUMN_NAME = "研究主题关键词"           # 包含关键词的列名
OUTPUT_FILE = "Data/WC_Data/classified_keywords.xlsx"  # 分类结果输出
PLOT_FILE = "Data/WC_Data/cluster_visualization.png"   # 可视化图像输出


# 文本处理配置
STOPWORDS_FILE = "stopwords.txt"        # 停用词文件路径
USE_CUSTOM_DICT = False                # 是否使用自定义词典
CUSTOM_DICT_PATH = "custom_dict.txt"   # 自定义词典路径


# 聚类算法配置
CLUSTER_ALGORITHM = "kmeans"          # 可选: kmeans, dbscan
N_CLUSTERS = 5                        # 聚类数量
RANDOM_STATE = 42                     # 随机种子


# 可视化配置
REDUCE_METHOD = "pca"                   # 降维方法: tsne 或 pca
DIMSIONS = 3                            # 降维后的维度(3维仅支持可交互)
INTERACTIVE = True                      # 是否使用交互式可视化


LABEL_DENSITY = 0.2                     # 标签显示密度(0-1)
PLOT_SIZE = (24, 16)                    # 图像尺寸
