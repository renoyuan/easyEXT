import json
import re


bad_json_str = '[{"组合名称": "开滦集团投资组合", "监督事项": "二、投资比例限制第（3）点 "投资权益类产品的比例≤组合净资产的5％", "实际值": "投资权益类产品占组合净资产的比例为5.01%", "阀值": "", "证券名称": "", "证券代码": "", "发生时间": "2025年8月6日", "持续天数": "", "计划名称": ""}]'
def fix_json_string_smart(bad_json_str: str):
    """
    尽量用标准库修复大模型输出的脏 JSON
    - 提取 JSON 主体
    - 统一引号
    - 删除尾随逗号
    - 自动补齐缺失的右括号/大括号
    - 修复漏逗号的键值对
    """

    # 提取最外层 JSON 结构
    match = re.search(r'(\{.*\}|\[.*\])', bad_json_str, re.S)
    if match:
        candidate = match.group(1)
    else:
        candidate = bad_json_str

    # 统一单引号为双引号
    candidate = re.sub(r"'", '"', candidate)

    # 删除尾随逗号
    candidate = re.sub(r",(\s*[\}\]])", r"\1", candidate)

    # 补齐缺失的右括号/右大括号
    open_braces = candidate.count("{")
    close_braces = candidate.count("}")
    if open_braces > close_braces:
        candidate += "}" * (open_braces - close_braces)

    open_brackets = candidate.count("[")
    close_brackets = candidate.count("]")
    if open_brackets > close_brackets:
        candidate += "]" * (open_brackets - close_brackets)

    # 尝试第一次解析
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # 如果失败，尝试修复漏逗号的情况: 在 }{" 之间加逗号
        candidate = re.sub(r'\}(\s*)\{', r'}, {', candidate)
        # 再次尝试解析
        return json.loads(candidate)
def fix_json_string_quotes(bad_json_str: str):
    """
    修复 JSON 中值里的未转义双引号
    """
    # 提取最外层 JSON 部分
    match = re.search(r'(\[.*\]|\{.*\})', bad_json_str, re.S)
    if match:
        candidate = match.group(1)
    else:
        candidate = bad_json_str

    # 处理值里的未转义双引号
    # 匹配 "key": "value" 中的 value，然后在 value 内部的裸双引号加上反斜杠
    def escape_inner_quotes(match):
        text = match.group(1)
        # 把里面的 " 转义为 \"
        text_escaped = text.replace('"', '\\"')
        return f'"{text_escaped}"'

    # 匹配键值对中的值部分
    candidate = re.sub(r'"([^"]*?)"', escape_inner_quotes, candidate)

    # 再次修正尾逗号
    candidate = re.sub(r",(\s*[\}\]])", r"\1", candidate)

    # 尝试解析
    return json.loads(candidate)
import ast

def fix_json_any(bad_json_str: str):
    """
    尽量修复大模型输出的非标准 JSON
    """
    # 提取最外层 JSON
    match = re.search(r'(\[.*\]|\{.*\})', bad_json_str, re.S)
    candidate = match.group(1) if match else bad_json_str

    # 统一单引号为双引号
    candidate = re.sub(r"'", '"', candidate)

    # 修复值中的裸双引号（只转义 value 内的）
    def escape_inner_quotes(m):
        text = m.group(1)
        # 仅转义内部的裸双引号
        text_escaped = text.replace('"', '\\"')
        return f'"{text_escaped}"'
    candidate = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', escape_inner_quotes, candidate)

    # 删除尾随逗号
    candidate = re.sub(r",(\s*[\}\]])", r"\1", candidate)

    # 补齐缺失的括号
    candidate += "}" * (candidate.count("{") - candidate.count("}"))
    candidate += "]" * (candidate.count("[") - candidate.count("]"))

    # 尝试解析 JSON
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass  # 尝试兜底

    # 最后兜底：用 ast.literal_eval（能解析 Python 风格）
    try:
        return ast.literal_eval(candidate)
    except Exception as e:
        raise ValueError(f"修复失败: {e}\n修复后的字符串:\n{candidate}")
if __name__ == "__main__":
    from json_repair import repair_json
    # fixed_obj = fix_json_any(bad_json_str)
    fixed_obj = repair_json(bad_json_str,ensure_ascii=False)
    aa = json.loads(fixed_obj, strict=False)
    print(aa)
    print(aa, type(aa))