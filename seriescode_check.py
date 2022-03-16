#!/usr/bin/python
#coding=utf-8
import json
import os
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
'''
#获取目录下的文件名（包括子目录下）
def get_all_path(open_file_path):
    rootdir = open_file_path
    path_list = []
    list = os.listdir(rootdir)
    for i in range(0, len(list)):
        com_path = os.path.join(rootdir, list[i])
        #print(com_path)
        if os.path.isfile(com_path):
            path_list.append(com_path)
        if os.path.isdir(com_path):
            path_list.extend(get_all_path(com_path))
    #print(path_list)
    return path_list
path=raw_input("Please input series dir: ")
if path=="":
  path = "/ut/www/default/epgwwwroot/series"
print "Please wait ... ,see the result.txt"
#file_list= get_all_path("/opt/wacos/domain/2/testepgwwwroot/series")
file_list= get_all_path(path)
'''
#写输出结果文件
#log = open('result.txt', 'w')
for i in range(len(file_list)):
 try: 
  if "json" in file_list[i]: #只对json文件进行处理 
   file=  file_list[i]
   with open(file) as f: 
       data = json.load(f) #读入json文件存成字典
   episodes=data['episodes']
   series = data['series']
   code = data['series']['code']
   title = data['series']['title']
   index=[]
   for j in range(len(episodes)):
       index.append(int(data['episodes'][j]['index']))
   lost=[]
   if len(index) == 0: #判断只有剧头
    print >> log,code,
    print >> log,title,
    print >> log,file,
    print >> log,"只有剧头"
   elif max(index) > 900: #综艺节目有把日期做集数，不处理
    #print >> log,code,title,file,"这是综艺节目"
    pass

   else:
    if index[0]!=1: #第一集不是1的处理
       for k in range(1,index[0]):
           lost.append(k)
       #找出列表中不连续的数
       lost2=sorted(list(set(range(index[0],index[-1]+1))-set(index)))
       print >> log,code,title,file,"缺少子集",(lost+lost2)
 
    else:
       lost=sorted(list(set(range(index[0],index[-1]+1))-set(index)))
       if lost !=[]:
        print >> log,code,title,file,"缺少子集",lost
 except:
  print "json format error: "+file
 continue  
print "total json file: "+str(i)
log.close()