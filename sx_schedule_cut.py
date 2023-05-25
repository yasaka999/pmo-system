#! /usr/bin/python3 -u
# encoding:utf-8
# 去掉括号里带引号的内容，转换罗马字符，截取剩下的18个字节。
import json
import re
import sys
def replace_roman_numerals(text):
    roman_numerals = {'Ⅰ': 1, 'Ⅱ': 2, 'Ⅲ': 3, 'Ⅳ': 4, 'Ⅴ': 5, 'Ⅵ': 6, 'Ⅶ': 7, 'Ⅷ': 8, 'Ⅸ': 9}
    for roman_numeral, arabic_numeral in roman_numerals.items():
        text = text.replace(roman_numeral, str(arabic_numeral))
    return text

def deal_json(jsonfile):
    with open(jsonfile, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for schedule in data['schedules']:
        print ('原始：',schedule['title'])
        schedule['title'] = replace_roman_numerals(re.sub(r'\([^)]*[：]([^)]*)\)', '', schedule['title']))
        
        # 如果是5个汉字加()，且括号内为中文，则去掉括号;比如"骑劫地下铁(上)"转成"骑劫地下铁上"
        pattern = r'^([\u4e00-\u9fa5]{5})\(([\u4e00-\u9fa5]+)\)$'  # 匹配规则的正则表达式模式
        schedule['title'] = re.sub(pattern, r'\1\2', schedule['title'])

        title_bytes = schedule['title'].encode('utf-8')
        if len(title_bytes) > 18:
            schedule['title'] = title_bytes[:18].decode('utf-8', errors='ignore')
        else:
            schedule['title'] = title_bytes.decode('utf-8', errors='ignore')
        print ('截取后：',schedule['title'])
        # 如果结果是"新燕子李三(25"这种，转换成“"新燕子李三25";海底小纵队6(2，转换成海底小纵队6-2
        pattern1 = r"[\u4e00-\u9fa5]{5}\([0-9]"
        pattern2 = r"[\u4e00-\u9fa5]{5}[0-9]\("
        match1 = re.match(pattern1, schedule['title'])
        match2 = re.match(pattern2, schedule['title'])

        if match1:
            schedule['title'] = schedule['title'].replace("(", "").replace(")", "") 
        if match2:
            schedule['title'] = schedule['title'].replace("(", "-")               
        print ('修改：',schedule['title'])

    with open(jsonfile, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    deal_json(sys.argv[1])
