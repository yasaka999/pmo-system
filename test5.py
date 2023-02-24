import pinyin
import re

def get_initials(name):
    # 去除字符串中的不必要的符号
    name = re.sub(r'[^\w\u4e00-\u9fff]+', '', name)
    # 获取名称的拼音
    pinyin_name = pinyin.get(name, format='strip', delimiter=" ")
    # 获取拼音的首字母
    initials = "".join([word[0] for word in pinyin_name.split()])
    return initials

names = ["张三", "<李四>!", "王五@"]
for name in names:
    print(get_initials(name))