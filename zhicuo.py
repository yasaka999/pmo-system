#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
  获取 个人中心的页面
  1.代码登录  登录成功 cookie(有效)
  2. 自动带着cookie 去请求个人中心

  cookiejar  自动保存这个cookie
"""
import urllib.request          #请求库
from http import cookiejar    #保存cookie用的
from urllib import parse   #转译
import re #解析
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import subprocess
#登录之前的， 登录页的网址https://www.yaozh.com/login
#找登录参数

#后台 根据你发送的请求方式来判断的 如果你是get(登录页面),如果POST(登录结果)
#1.代码登录
    # 1.1 登录的网址
login_url = "http://zhicuo.cn/login"


    #1.2 登录的参数
login_form_data = {
    "name": "13666633777",
    "password": "han2015",
}
 #1.3 发送登录请求POST
cook_jar = cookiejar.CookieJar()
#定义有添加 cook 功能的 处理器
cook_hanlder = urllib.request.HTTPCookieProcessor(cook_jar)
#根据处理器 生成 opener
opener = urllib.request.build_opener(cook_hanlder)

#带着参数 发送post请求
#添加请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3650.400 QQBrowser/10.4.3341.400"}
#1 参数 将来 需要转译 转码； 2 post 请求的 data 要求是bytes
login_str = parse.urlencode(login_form_data).encode('utf-8')
login_request = urllib.request.Request(login_url,headers=headers,data=login_str)
#如果登录成功，cookjar自动保存cookie
opener.open(login_request)

# 2 代码带着cookie去访问 试卷中心
center_url = "http://zhicuo.cn/topicpaper?ch=0"
center_request = urllib.request.Request(center_url,headers=headers)
response = opener.open(center_url)
#bytes -->str
data = response.read().decode()
# 获取paperid
paperid = re.findall('onclick="getpaper\(''(.*)\)" style',data)
# 去引号
paper=eval(paperid[0])

# 3 请求下载生成试卷
url = "http://zhicuo.cn/interface/getpaperd"
data = {"paperid":paper}
datas=urllib.parse.urlencode(data).encode('utf-8') 
a=urllib.request.Request(url,data=datas)
doc=urllib.request.urlopen(a).read()
#定义文件名，每天一个
date=datetime.datetime.now().strftime('%Y-%m-%d')
papername='zhicuo-'+str(date)+'.doc'
with open(papername,"wb") as f:
     f.write(doc)
print ("paper download success:"+papername)

# convert to pdf
conv=subprocess.Popen("/opt/libreoffice7.0/program/soffice  --invisible --convert-to pdf " + papername,shell=True)
conv.wait()
papername='zhicuo-'+str(date)+'.pdf'
print ("conver sucess to: "+papername)
# 4 发送邮件给打印机
# 第三方 SMTP 服务
# 发送邮件相关参数
smtpserver = 'smtp.163.com'         # 发件服务器
port = 0                            # 端口
sender = '13666633777@163.com'         # 发件人邮箱
psw = 'XSBTZQCZBGWQVYYG'                            # 发件人密码
receiver = "hans.han@utstarcom.cn"       # 接收人
# 邮件标题
subjext = '每日错题'+date
# 获取附件信息
#with open('result.html', "rb") as f:
body = "知错试卷"
message = MIMEMultipart()
# 发送地址
message['from'] = sender
message['to'] = receiver
message['subject'] = subjext
# 正文
#body = MIMEText(body, 'html', 'utf-8')
#message.attach(body)
# 同一目录下的文件
att = MIMEText(open(papername, 'rb').read(), 'base64', 'utf-8') 
att["Content-Type"] = 'application/octet-stream'
# filename附件名称
filename = 'attachment; filename='+papername
att["Content-Disposition"] = filename
message.attach(att)
smtp = smtplib.SMTP()
smtp.connect(smtpserver)    # 链接服务器
smtp.login(sender, psw)     # 登录
smtp.sendmail(sender, receiver, message.as_string())  # 发送
smtp.quit()             # 关闭