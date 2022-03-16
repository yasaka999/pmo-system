import urllib.request 
from http import cookiejar    #保存cookie用的
from urllib import parse 
import json
import datetime


login_url = "http://10.178.50.164:8080/bi-portal/login/login.do"

login_form_data = {
    "name": "reportadmin",
    "password": "Utiptv@2021",
}
 #1.3 发送登录请求POST
cook_jar = cookiejar.CookieJar()
#定义有添加 cook 功能的 处理器
cook_hanlder = urllib.request.HTTPCookieProcessor(cook_jar)
#根据处理器 生成 opener
opener = urllib.request.build_opener(cook_hanlder)

#带着参数 发送post请求
#1 参数 将来 需要转译 转码； 2 post 请求的 data 要求是bytes
login_str = parse.urlencode(login_form_data).encode('utf-8')
login_request = urllib.request.Request(login_url,data=login_str)

#如果登录成功，cookjar自动保存cookie
opener.open(login_request)
token_url = "http://10.178.50.164:8080/bi-portal/configure/getToken.do"
#token_request = urllib.request.Request(token_url)
response = opener.open(token_url)
#bytes -->str
data = json.loads(response.read())
token = data['token']

# 开始请求
yesterday = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y%m%d')

query_url = "http://10.178.50.164:8080/statplatform5/query"

q_data1="?qdi=queryc3ordersinglepoint&starttime="+yesterday+"&endtime="+yesterday+"&datetype=D&token="+token+"&sysid=t&userid=test1"
url = query_url+q_data1

q_request = urllib.request.Request(url)

res = urllib.request.urlopen(q_request)
result = json.loads(res.read())
c3_order = {}
for i in range(len(result["subject"])):
    c3_order[result["subject"][i]["CODE"]] = result["subject"][i]["ORDERCOUNT"]
    print (result["subject"][i]["NAME"],result["subject"][i]["ORDERCOUNT"],result["subject"][i]["CODE"])

q_data2="?qdi=queryc3ordermonthpoint&starttime="+yesterday+"&endtime="+yesterday+"&datetype=D&type=0%27%2C%273%27%2C%274%27%2C%275%27%2C%27&token="+token+"&sysid=t&userid=test1"
url = query_url+q_data2

q_request = urllib.request.Request(url)

res = urllib.request.urlopen(q_request)
result = json.loads(res.read())

for i in range(len(result["subject"])):
    c3_order[result["subject"][i]["CODE"]] = result["subject"][i]["NEW_ORDERCOUNT"]
    print (result["subject"][i]["NAME"],result["subject"][i]["NEW_ORDERCOUNT"],result["subject"][i]["CODE"])
print (c3_order)


