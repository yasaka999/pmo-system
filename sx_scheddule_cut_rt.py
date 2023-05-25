#!/usr/bin/python3 -u
# coding=utf-8
# 为避免死循环，对文件处理时间做了记录，10秒内的修改不处理；避免字典过大，每小时清空一次
import os
import sys
import time
import pyinotify
import json
import re

class JSONEventHandler(pyinotify.ProcessEvent):
    def __init__(self):
        super().__init__()
        self.last_modified_times = {}
        self.last_clear_time = time.time()

    def process_IN_CREATE(self, event):
        self.process_file(event.pathname)

    def process_IN_MODIFY(self, event):
        self.process_file(event.pathname)

    def replace_roman_numerals(self,text):
        roman_numerals = {'Ⅰ': 1, 'Ⅱ': 2, 'Ⅲ': 3, 'Ⅳ': 4, 'Ⅴ': 5, 'Ⅵ': 6, 'Ⅶ': 7, 'Ⅷ': 8, 'Ⅸ': 9}
        for roman_numeral, arabic_numeral in roman_numerals.items():
            text = text.replace(roman_numeral, str(arabic_numeral))
        return text

    def deal_json(self, jsonfile):
        with open(jsonfile, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for schedule in data['schedules']:
            print ('原始：',schedule['title'])
            schedule['title'] = self.replace_roman_numerals(re.sub(r'\([^)]*[：]([^)]*)\)', '', schedule['title']))
            
            # 如果是5个汉字加()，且括号内为中文，则去掉括号;比如"骑劫地下铁(上)"转成"骑劫地下铁上"
            pattern = r'^([\u4e00-\u9fa5]{5})\(([\u4e00-\u9fa5]+)\)$'  # 匹配规则的正则表达式模式
            schedule['title'] = re.sub(pattern, r'\1\2', schedule['title'])
        
            title_bytes = schedule['title'].encode('utf-8')
            if len(title_bytes) > 18:
                schedule['title'] = title_bytes[:18].decode('utf-8', errors='ignore')

            else:
                schedule['title'] = title_bytes.decode('utf-8', errors='ignore')
                
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

    def process_file(self, filepath):
        #清空字典
        current_time = time.time()
        if current_time - self.last_clear_time > 3600:  # 清空时间间隔为1小时
            self.last_modified_times.clear()
            self.last_clear_time = current_time

        file_name, extension = os.path.splitext(filepath)
        # 判断文件是否是JSON文件
        if extension.lower() == ".json":
            current_time = time.time()
            last_modified_time = self.last_modified_times.get(filepath, 0)
            if current_time - last_modified_time >= 10:  # 更新时间在10秒内的不处理
                print('Process file:',filepath)
                # 调用方法处理JSON文件，将文件内容修改后写入文件中
                self.deal_json(filepath)
                self.last_modified_times[filepath] = current_time
            else:
                print('Skip file:',filepath)

if __name__ == '__main__':
    # 创建inotify实例，并添加要监听的事件类型
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY
#    mask = pyinotify.IN_CREATE
    # 要监控的目录路径
    watch_dir = "/opt/wacos/epgwwwroot/schedules/"
    #watch_dir = "/opt/xhan/"
    # 创建事件处理器实例
    handler = JSONEventHandler()
    # 添加要监听的事件类型（创建、修改）
    notifier = pyinotify.Notifier(wm, handler)
    # 添加要监控的目录
    wdd = wm.add_watch(watch_dir, mask, rec=True)
    # 启动事件监听循环
    notifier.loop()
