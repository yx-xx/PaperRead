from zhipuai import ZhipuAI
from config import GLM_API_KEY,GLM_API_MODEL
import os
import re
import json


def save_raw_output(content, pdf_filename="unknown", file_name=None):
    """
    保存大模型原始输出内容到本地txt文件，便于调试。
    :param content: 字符串或可序列化对象
    :param pdf_filename: PDF文件名，用于生成唯一的debug文件名
    :param file_name: 自定义文件名，如果提供则优先使用
    """
    save_dir = "glm_outputs"
    os.makedirs(save_dir, exist_ok=True)
    
    if file_name is None:
        # 使用PDF文件名生成debug文件名
        base_name = os.path.splitext(pdf_filename)[0]  # 去掉.pdf后缀
        file_name = f"{base_name}.txt"
    
    file_path = os.path.join(save_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:  # 改为w模式，每次覆盖
        f.write(f"=== PDF文件: {pdf_filename} ===\n")
        f.write(f"=== 时间: {__import__('datetime').datetime.now()} ===\n\n")
        if isinstance(content, str):
            f.write(content + "\n")
        else:
            f.write(json.dumps(content, ensure_ascii=False, indent=2) + "\n")
    print(f"[调试] 已保存大模型原始输出到 {file_path}")



def analyze_paper_with_glm(text, pdf_filename="unknown"):
    """
    调用GLM-4-Flash-250414分析论文内容,返回多维度分析结果。
    """
    client = ZhipuAI(api_key=GLM_API_KEY)
    prompt = (
        "请从以下论文内容中，按如下JSON格式严格输出（所有字段都要有，关键词字段请只输出一个中文关键词，要中文关键词）：\n"
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
    try:
        response = client.chat.completions.create(
            model = GLM_API_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            stream = False,
        )
        
        # 傻逼编辑器，明明没错非要报错！！！
        content = response.choices[0].message.content
        
        # print(content)
        save_raw_output(content, pdf_filename)


        return parse_glm_output(content)
    except Exception as e:
        print(f"[GLM-4-Flash] API请求或解析失败: {e}")
        return None 



def parse_glm_output(content):
    """鲁棒地解析GLM返回的各种格式JSON内容"""
    # 预定义结果模板
    result = {
        "论文标题": "",
        "研究主题关键词": "",
        "应用场景关键词": "",
        "主要方法关键词": "",
        "创新点关键词": "",
        "主要结论关键词": ""
    }
    
    try:
        # 尝试1：直接解析JSON（适用于无标记的纯JSON）
        try:
            data = json.loads(content)
            for key in result:
                if key in data:
                    result[key] = str(data[key]).strip()
            return result
        except json.JSONDecodeError:
            pass
        
        # 尝试2：匹配带标记的JSON块（处理```json标记）
        json_match = re.search(
            r'```(?:json)?\s*({.*?})\s*```', 
            content, 
            flags=re.DOTALL | re.IGNORECASE
        )
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                for key in result:
                    if key in data:
                        result[key] = str(data[key]).strip()
                return result
            except json.JSONDecodeError:
                pass
        
        # 尝试3：提取所有花括号内的内容（处理无标记或部分标记）
        brace_match = re.search(r'\{.*\}', content, flags=re.DOTALL)
        if brace_match:
            try:
                data = json.loads(brace_match.group(0))
                for key in result:
                    if key in data:
                        result[key] = str(data[key]).strip()
                return result
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"[JSON解析] 解析失败: {e}")
    
    # 最后尝试：逐行解析键值对
    print("[JSON解析] 使用备选解析方案")
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        # 匹配键值对格式（支持中文和英文冒号）
        m = re.match(r'[\'"\s]*([^"\':：]+)[\s]*[:：][\s]*([^"\',]+)[\s,]*', line)
        if m:
            key = m.group(1).strip().replace('"', '').replace("'", "")
            value = m.group(2).strip().replace('"', '').replace("'", "")
            
            # 特殊处理键名匹配
            if "论文标题" in key:
                result["论文标题"] = value
            elif "研究主题" in key:
                result["研究主题关键词"] = value
            elif "应用场景" in key:
                result["应用场景关键词"] = value
            elif "主要方法" in key:
                result["主要方法关键词"] = value
            elif "创新点" in key:
                result["创新点关键词"] = value
            elif "主要结论" in key:
                result["主要结论关键词"] = value
    
    return result

# def parse_glm_output(text):
#     """
#     解析GLM输出的JSON字符串，保证每个字段为字符串，异常时返回空字符串。
#     """
#     fields = [
#         "论文标题", "研究主题关键词", "应用场景关键词", "主要方法关键词", "创新点关键词", "主要结论关键词"
#     ]
#     result = {field: "" for field in fields}
#     try:
#         data = json.loads(text)
#         for field in fields:
#             val = data.get(field, "")
#             if isinstance(val, str):
#                 result[field] = val.strip()
#             elif isinstance(val, list) and val:
#                 result[field] = str(val[0]).strip()
#             else:
#                 result[field] = ""
#     except Exception:
#         # 若不是标准JSON，尝试逐行解析
#         for line in text.splitlines():
#             line = line.strip()
#             if not line:
#                 continue
#             m = re.match(r"(.+?)[：:](.+)", line)
#             if m:
#                 k, v = m.group(1).strip(), m.group(2).strip()
#                 if k in fields:
#                     result[k] = v
#     return result
