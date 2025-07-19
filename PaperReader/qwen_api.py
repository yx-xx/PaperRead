#################################
# 免费模型太过拉跨，已经弃用
#################################

import requests
import json
import os
import re
from config import QWEN_API_URL, QWEN_API_KEY, QWEN_API_MODEL


def save_raw_output(content, pdf_filename="unknown", file_name=None):
    """
    保存大模型原始输出内容到本地txt文件，便于调试。
    :param content: 字符串或可序列化对象
    :param pdf_filename: PDF文件名，用于生成唯一的debug文件名
    :param file_name: 自定义文件名，如果提供则优先使用
    """
    save_dir = "Data/qwen_outputs"
    os.makedirs(save_dir, exist_ok=True)
    
    if file_name is None:
        # 使用PDF文件名生成debug文件名
        base_name = os.path.splitext(pdf_filename)[0]  # 去掉.pdf后缀
        file_name = f"llm_output_{base_name}.txt"
    
    file_path = os.path.join(save_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:  # 改为w模式，每次覆盖
        f.write(f"=== PDF文件: {pdf_filename} ===\n")
        f.write(f"=== 时间: {__import__('datetime').datetime.now()} ===\n\n")
        if isinstance(content, str):
            f.write(content + "\n")
        else:
            f.write(json.dumps(content, ensure_ascii=False, indent=2) + "\n")
    print(f"[调试] 已保存大模型原始输出到 {file_path}")


def analyze_paper_with_qwen(text, pdf_filename="unknown", timeout=120):
    """
    调用通义千问API（算力智链渠道）分析论文内容，返回多维度分析结果。
    支持超时设置，增强异常处理和日志。
    """
    if not QWEN_API_KEY or QWEN_API_KEY.strip() == "":
        raise ValueError("[错误] 请在config.py中填写你的API Key，否则无法调用大模型API！")

    # 自动补全API路径
    api_url = QWEN_API_URL.rstrip('/')
    if not api_url.endswith('/chat/completions'):
        api_url += '/chat/completions'

    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        "请从以下论文内容中，按如下JSON格式严格输出（所有字段都要有，关键词字段请只输出一个中文关键词）：\n"
        "{\n"
        "  \"论文标题\": \"\",\n"
        "  \"研究主题关键词\": \"\",\n"
        "  \"应用场景关键词\": \"\",\n"
        "  \"主要方法关键词\": \"\",\n"
        "  \"创新点关键词\": \"\",\n"
        "  \"主要结论关键词\": \"\"\n"
        "}\n"
        "内容：" + text
    )
    payload = {
        "model": QWEN_API_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    } 
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        result = resp.json()

        # 保存原始输出用于调试
        save_raw_output(result, pdf_filename)

        # 提取
        content = None
        if isinstance(result, dict):
            try:
                content = result['choices'][0]['message']['content']
            except Exception:
                # 打印原始返回，便于调试
                print("[警告] API返回格式异常，原始返回：", result)
                return None
        else:
            print("[错误] API返回非字典类型：", result)
            return None
        return parse_qwen_output(content)
    except requests.exceptions.RequestException as e:
        print(f"[网络错误] API请求失败: {e}")
        return None
    except Exception as e:
        print(f"[异常] 解析API响应失败: {e}")
        return None

 

def parse_qwen_output(text):
    """
    优先尝试解析为JSON，失败则回退为key:value行解析。
    关键词字段自动转为list，支持多种分隔符。
    """
    # 先尝试JSON解析
    try:
        result = json.loads(text)
        # 兼容大模型有时会多输出一层代码块
        if isinstance(result, str):
            result = json.loads(result)
    except Exception:
        # 回退为key:value行解析
        result = {}
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r"(.+?)[：:](.+)", line)
            if m:
                k, v = m.group(1).strip(), m.group(2).strip()
                result[k] = v

    # 统一处理关键词字段
    keyword_fields = [
    "研究主题关键词", "应用场景关键词", "主要方法关键词", "创新点关键词", "主要结论关键词"
    ]
    for field in keyword_fields:
        if field in result:
            val = result[field]
            if isinstance(val, list):
                # 只取第一个非空
                result[field] = str(val[0]).strip() if val and str(val[0]).strip() else ""
            elif isinstance(val, str):
                # 以逗号、分号、空格等分割，只取第一个
                first = re.split(r'[，,;；\\s]+', val)
                result[field] = first[0].strip() if first and first[0].strip() else ""
            else:
                result[field] = ""
        else:
            result[field] = ""

