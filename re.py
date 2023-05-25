import re

def remove_parentheses(text):
    pattern = r'^([\u4e00-\u9fa5]{5})\(([\u4e00-\u9fa5]+)\)$'  # 匹配规则的正则表达式模式
    result = re.sub(pattern, r'\1\2', text)
    return result

# 测试
text = "骑劫地下铁(上)"
result = remove_parentheses(text)
print(result)
