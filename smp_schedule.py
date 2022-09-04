#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import urllib.request          #请求库
from http import cookiejar    #保存cookie用的
from urllib import parse   #转译
import re #解析
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def login(username, password, url):
    login_form_data = {
    "userName": username,
    "password": password,
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
    headers = {"User-Agent": "Chrome/70.0.3538.25"}
#1 参数 将来 需要转译 转码； 2 post 请求的 data 要求是bytes
    login_str = parse.urlencode(login_form_data).encode('utf-8')
    login_request = urllib.request.Request(url,headers=headers,data=login_str)
#如果登录成功，cookjar自动保存cookie
    opener.open(login_request)
    print ("%s: login OK" %now)

def query(url, data=None,pageid=1,rownum=100):
    post_data = parse.urlencode(data).encode('utf-8')
    # print (post_data)
    url = url %(pageid,rownum)
#    print (url)
#    print (post_data)
    center_request = urllib.request.Request(url,data=post_data)
    response = opener.open(center_request)
#bytes -->str  
    data = response.read().decode()
    return data
if __name__ == "__main__":
    result_file = open("result.txt", "w")
    pageid = 1
    rownum = 500
    login_url = "http://172.25.116.7/iptvsmp/login.do"
    query_url = "http://172.25.116.7/iptvsmp/content/ListBackSeeScheduleAction.do?page=%d&rowNum=%d&windowStaffId=999999999&windowDomainId=0"
    username = "00"
    password = "1qaz@WSX"
    now = datetime.datetime.now()
    tomorrow=datetime.datetime.now()+ datetime.timedelta(days=1)
    start_time = tomorrow.strftime('%Y-%m-%d')
    end_time = tomorrow.strftime('%Y-%m-%d')
    post_data = {
        "sortOrder":"", 
        "sortName": "",
        "storeTimeBegin": start_time,
        "storeTimeEnd": end_time,
        "name":"", 
        "channelName":"" 
        }
    login(username, password, login_url)
    data = query(query_url, post_data, pageid, rownum)
#    print (data)
    dict_data = json.loads(data)
    channel_list = []
    print ("总分页数: ",dict_data["total"])
    print ("总节目单数: ",dict_data["records"],file=result_file)
#    print (len(dict_data["adaptedRows"]))
#    page_count = int(dict_data["records"]/rownum)+1
    page_count = dict_data["total"]
    for i in range(page_count):
        pageid = i+1
        print ("pageid: " + str(pageid))
        data = query(query_url, post_data, pageid, rownum)
        dict_data = json.loads(data)
        for j in range(len(dict_data["adaptedRows"])):
            channel_name = dict_data["adaptedRows"][j]["channel"]["name"]
            if channel_name not in channel_list:
                channel_list.append(channel_name)
    now = datetime.datetime.now()
    print ("%s: 有%s节目单的频道:" % (now,start_time),file=result_file)
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

