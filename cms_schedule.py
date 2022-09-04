#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import urllib.request
from http import cookiejar
from urllib import parse
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def login(username, password, url):
    login_form_data = {
    "userID": username,
    "password": password,
    "x": '26',
    "y": '10'
    }
 #发送登录请求POST
    cook_jar = cookiejar.CookieJar()
#定义有添加 cook 功能的 处理器
    cook_hanlder = urllib.request.HTTPCookieProcessor(cook_jar)
#根据处理器 生成 opener
    global opener
    opener = urllib.request.build_opener(cook_hanlder)

#带着参数 发送post请求
#添加请求头
    headers ={
        "User-Agent": "Chrome/70.0.3538.25"
        }
    login_str = parse.urlencode(login_form_data).encode('utf-8')
    login_request = urllib.request.Request(url,headers=headers,data=login_str)
#如果登录成功，cookjar自动保存cookie
#    print (login_str)
    opener.open(login_request)
    print ("%s: login OK" %now)

def query(url,pageid=1,rownum=100):
    tomorrow=datetime.datetime.now()+ datetime.timedelta(days=1)
    start_time = tomorrow.strftime('%Y-%m-%d') + "00:00:00"
    end_time = tomorrow.strftime('%Y-%m-%d') + "23:59:59"
    headers ={
        "User-Agent": "Chrome/70.0.3538.25",
        "Referer": "http://192.168.5.1:5050/CMS/channel/scheduleAssortQueryInit?moduleId=52" 
        }
    data = {
        "channelIds":"", 
        "channelNames":"", 
        "startTime": start_time,
        "endTime": end_time,
        "programAssort":"", 
        "_search": "false",
        "nd": "1662195577928",
        "rows": rownum,
        "page": pageid,
        "sidx": "1",
        "sord": "asc"
        }
    post_data = parse.urlencode(data).encode('utf-8')
    # print (post_data)
    print (url)
    center_request = urllib.request.Request(url,data=post_data,headers=headers)
    response = opener.open(center_request)
#bytes -->str  
    data = response.read().decode()
    return data

if __name__ == "__main__":
    result_file = open("result.txt", "w")
    pageid = 1
    rownum = 1000
    login_url = "http://192.168.5.1:5050/CMS/login"
    query_url = "http://192.168.5.1:5050/CMS/channel/scheduleAssortQuery"
    username = "UDwangluo"
    password = "888888"

    login(username, password, login_url)
    data = query(query_url, pageid, rownum)
 #   print (data)
    dict_data = json.loads(data)
    channel_list = []
    print ("total pages :",dict_data["total"])
    print ("total records :",dict_data["records"])
#    print (len(dict_data["rows"]))
#    page_count = int(dict_data["records"]/rownum)+1
    page_count = int(dict_data["total"])
    for i in range(page_count):
        pageid = i+1
        print ("pageid: " + str(pageid))
        data = query(query_url, pageid, rownum)
        dict_data = json.loads(data)
        for j in range(len(dict_data["rows"])):
            channel_name = dict_data["rows"][j]["cell"][0]
            if channel_name not in channel_list:
                channel_list.append(channel_name)
    now = datetime.datetime.now()
    tomorrow = now+ datetime.timedelta(days=1)
    print ("%s: 有%s节目单的频道:" % (now,tomorrow.strftime("%Y-%m-%d")),file=result_file)
    print (sorted(channel_list),file=result_file)
    print ("有节目单的频道总数: ",len(channel_list),file=result_file)
    
with open("../files/channel_list.txt", encoding="utf8") as f:
    channel = f.read().split("\n")
print ("----------------------------------------------------------------",file=result_file)
channel_miss=[]
for channel_name in channel:
    if channel_name not in channel_list:
        channel_miss.append(channel_name)
if channel_miss:
    print ("共有%s个频道节目单缺失: " % len(channel_miss),file=result_file)
    print (",".join(channel_miss),file=result_file)
else:
    print ("节目单无异常",file=result_file)


result_file.close()

# 第三方 SMTP 服务
# 发送邮件相关参数
smtpserver = 'smtp.163.com'         # 发件服务器
port = 0                            # 端口
sender = '13666633777@163.com'         # 发件人邮箱
psw = 'XSBTZQCZBGWQVYYG'                            # 发件人密码
receiver = "hans.han@utstarcom.cn"       # 接收人
# 邮件标题
subjext = '每日节目单检查%s' %now.strftime('%Y-%m-%d')
# 获取附件信息
#with open('result.html', "rb") as f:
#body = "节目单检查结果"
message = MIMEMultipart()
# 发送地址
message['from'] = sender
message['to'] = receiver
message['subject'] = subjext
# 正文
body = MIMEText((open("result.txt", "r")).read(), 'plain', 'utf-8')
message.attach(body)
# 同一目录下的文件
#att = MIMEText(open("result.txt", 'rb').read(), 'base64', 'utf-8') 
#att["Content-Type"] = 'application/octet-stream'
# filename附件名称
#filename = 'attachment; filename='+str(result_file)
#att["Content-Disposition"] = filename
#message.attach(att)
smtp = smtplib.SMTP()
smtp.connect(smtpserver)    # 链接服务器
smtp.login(sender, psw)     # 登录
smtp.sendmail(sender, receiver, message.as_string())  # 发送
smtp.quit()             # 关闭
