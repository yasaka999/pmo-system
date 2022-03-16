#!/usr/bin/python
#coding=utf-8
import json
import os
import sys  
#reload(sys)  
#sys.setdefaultencoding('utf8')
file='91030001000000010000000000304480.json'
with open(file) as f:
     data = json.load(f) #读入json文件存成字典
     if data['vod']['seriesflag']=='1' and  not data['vod']['seriescode']:
          print (data['vod']['code'],data['vod']['title'])
#   series = data['series']
#   code = data['series']['code']
#   title = data['series']['title']