import jieba
from config import STOPWORDS_FILE, USE_CUSTOM_DICT, CUSTOM_DICT_PATH

def preprocess_texts(keywords):
    """中文文本预处理：分词和停用词过滤"""
    # 加载自定义词典
    if USE_CUSTOM_DICT:
        jieba.load_userdict(CUSTOM_DICT_PATH)
    
    # 加载停用词
    stopwords = set()
    try:
        with open(STOPWORDS_FILE, 'r', encoding='utf-8') as f:
            stopwords = set([line.strip() for line in f])
    except:
        print("警告：停用词文件未找到，使用内置停用词")
        stopwords = {"的", "了", "和", "是", "在", "也", "及", "与", "就"}
    
    # 分词和过滤
    processed = []
    for text in keywords:
        words = jieba.lcut(text.strip())
        filtered = [word for word in words if len(word) > 1 and word not in stopwords]
        processed.append(" ".join(filtered))
    
    return processed