#!/usr/bin/python
# coding=utf-8
import json
import os
import sys

reload(sys)
sys.setdefaultencoding("utf8")

# 获取目录下的文件名（包括子目录下）
def get_all_path(open_file_path):
    rootdir = open_file_path
    path_list = []
    list = os.listdir(rootdir)
    for i in range(0, len(list)):
        com_path = os.path.join(rootdir, list[i])
        # print(com_path)
        if os.path.isfile(com_path):
            path_list.append(com_path)
        if os.path.isdir(com_path):
            path_list.extend(get_all_path(com_path))
    # print(path_list)
    return path_list


path = raw_input("Please input  dir: ")
if path == "":
    path = "/opt/wacos/epgwwwroot/epgcategory"
print("Please wait ... ,see the result.txt")
# file_list= get_all_path("/opt/wacos/domain/2/testepgwwwroot/series")
file_list = get_all_path(path)

# 写输出结果文件
# log = open('result.txt', 'w')
for i in range(len(file_list)):
    try:
        if "json" in file_list[i]:  # 只对json文件进行处理
            file = file_list[i]
            with open (file) as data:
                json_data = json.load(data)
                codes_with_empty_pictures = []

                for item in json_data['epgCategorydtl']:
                    if item['type'] == 'outlink' and not item['pictures']:
                        codes_with_empty_pictures.append(item['title'])

                if  codes_with_empty_pictures:
                    print ("missing picture: %s" %file)
                    for i in codes_with_empty_pictures:
                        print(i)
                else:
                    print ("no missing picture")
    except:
        print ("json format error: " + file)
    continue
print ("total json file: " + str(i))
log.close()
