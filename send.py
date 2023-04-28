import requests
import time

url = 'http://10.48.115.100:8510'

# 使用Session对象来保持连接
session = requests.Session()
session.headers.update({'Connection': 'keep-alive'})

# 每隔0.1秒发送一个POST请求
while True:
    headers = {'Content-Type': 'application/xml'}
    data = '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:impl="iptv"><SOAP-ENV:Header/><SOAP-ENV:Body><impl:ExecCmd><CSPID>71ABTV</CSPID><LSPID>150ABTV</LSPID><CorrelateID>588</CorrelateID><CmdFileURL>ftp://scms:scms@172.19.64.71:21//opt/scms/CTMSData/output/2023/04/07/10/71ABTV_150ABTV__5881680834679183.xml</CmdFileURL></impl:ExecCmd></SOAP-ENV:Body></SOAP-ENV:Envelope>'
    response = session.post(url, data=data,headers=headers)
    print(response.text)

    time.sleep(0.1)
