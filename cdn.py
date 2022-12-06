#!/usr/bin/python
# coding=utf-8
# 接收上游工单请求，应答接收成功消息。回复resultNotify： 拼CorrelateID ，cspid,lspid
# 系统需要另提供 ftpserver功能
import time
import socket
import sys
import re
import urllib2

defaultencoding = "utf-8"
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

def response(http_data):
    http_head = "HTTP/1.1 200\r\nContent-Type: text/xml;charset=UTF-8\r\n"
    content_length = "Content-Length:" + str(len(http_data)) + "\r\n"
    http_head = http_head + content_length + "\r\n"
    http_response = http_head + http_data
    return http_response

def doPost(url, data=None):
    HTTP_POST_HEADERS = {"SOAPAction": "test","content-type": "text/xml"}
    postReq = urllib2.Request(url=url, headers=HTTP_POST_HEADERS, data=data)
    try:
        response = urllib2.urlopen(postReq, timeout=3)
        if response.getcode() != 200:
            print (response.getcode())
            print (" Fail")
            return -1
        else:
            print (" Success")
            return 0
    except Exception :
        print (" send soap request Fail,check DestUrl")
        return -1



soap_response = '<?xml version="1.0" encoding="utf-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" \
xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\
<soapenv:Body><ns1:ExecCmdResponse soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:ns1="iptv">\
<ExecCmdReturn xsi:type="ns1:CSPResult"><Result xsi:type="xsd:int">0</Result><ErrorDescription xsi:type="soapenc:string" \
xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">Receive the request:and ready to process.</ErrorDescription></ExecCmdReturn>\
</ns1:ExecCmdResponse></soapenv:Body></soapenv:Envelope>'

soap_resultnotify= '<?xml version="1.0" encoding="utf-8"?><SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:impl="iptv" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header/><SOAP-ENV:Body><impl:ResultNotify><CSPID >cspid</CSPID><LSPID>lspid</LSPID><CorrelateID>correlateid</CorrelateID><CmdResult>0</CmdResult><ResultFileURL>ftp</ResultFileURL></impl:ResultNotify></SOAP-ENV:Body></SOAP-ENV:Envelope>'


HOST, PORT = "", 8510

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(5)
print("Serving HTTP on port %s ..." % PORT)

while True:
    client_connection, client_address = listen_socket.accept()
# 有时读取到的数据不完整，这地方等一下看着没问题了
    time.sleep(0.1)
    request = client_connection.recv(1024)
    if "CSPID" in request.decode("utf-8"):
#       print (request)
        cspid = re.findall('CSPID.*>(.+?)</CSPID',request.decode("utf-8"))[0]
        lspid = re.findall('LSPID.*>(.+?)</LSPID',request.decode("utf-8"))[0]
        correlateid = re.findall('CorrelateID.*>(.+?)</CorrelateID',request.decode("utf-8"))[0]
    else:
        print ("something wrong !aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print("CSPID:%s; LSPID:%s" %(cspid,lspid))
    print("CorrelateID: ",correlateid)
#    time.sleep(1.5)
    client_connection.sendall(response(soap_response).encode("utf-8"))

#    print(soap_response.encode("utf-8"))
#    client_connection.close()

# 发送resultNotify
    url = "http://172.25.130.201:8002/scms-output-dispatcher/services/ctms_smg"
    ftp = "ftp://nmftp:Wjftp123!@172.25.130.202/result.xml"
    data = soap_resultnotify.replace("cspid",cspid).replace("lspid",lspid).replace("correlateid",correlateid).replace("ftp",ftp)
#    print(data)
    doPost(url, data)
"""
功能：可模拟下游接收节点，应答工单下的soap消息，并回复处理结果的resultNotify.
不同的端口修改PORT值，回调地址修改url, ftp地址也需要按实际修改
result.xml的内容如下：
<?xml version="1.0" encoding="UTF-8"?><xsi:ADI xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Reply><Property Name="Result">0</Property><Property Name
="Description">Success</Property></Reply></xsi:ADI>
"""