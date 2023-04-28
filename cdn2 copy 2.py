#!/usr/bin/python
# coding=utf-8
import time
import socket
import sys
import re
import urllib2
import subprocess
from xml.etree import ElementTree as ET

def substr(keyword,str1):
    result = re.findall('%s.*>(.+?)</%s' %(keyword,keyword) ,str1)[0]
    return result

def xml_parser(filename):
    list = []
    tree = ET.parse(filename)
    root = tree.getroot()
    for child in root:
        a = child.tag
        for node in child:
            if "ParentType"  in node.attrib.keys():
                b = node.tag+'|'+node.attrib['ElementType']+'|'+node.attrib["ParentType"]
            else:
                b = node.tag+'|'+node.attrib['ElementType']
            c = []
            for k,v in node.attrib.items():
                c.append(k+':'+v)
            c.sort()
            d='|'.join(c)
            list.append(node.tag+'|'+d)
            for object in node:
                list.append(a+'|'+b+'|'+object.attrib['Name']+':'+str(object.text))
    return list

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
            print ("%s: ResultNotify Success" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            return 0
    except Exception :
        print (" send soap request Fail,check DestUrl")
        return -1

defaultencoding = "utf-8"
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

soap_response = '<?xml version="1.0" encoding="utf-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" \
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\
        <soapenv:Body><ns1:ExecCmdResponse soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:ns1="iptv">\
            <ExecCmdReturn xsi:type="ns1:CSPResult"><Result xsi:type="xsd:int">0</Result><ErrorDescription xsi:type="soapenc:string" \
                xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">Receive the request:and ready to process.</ErrorDescription></ExecCmdReturn>\
                    </ns1ExecCmdResponse></soapenv:Body></soapenv:Envelope>'

soap_resultnotify= '<?xml version="1.0" encoding="utf-8"?><SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" \
    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:impl="iptv" xmlns:xsd="http://www.w3.org/2001/XMLSchema" \
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header/><SOAP-ENV:Body><impl:ResultNotify><CSPID >cspid</CSPID>\
            <LSPID>lspid</LSPID><CorrelateID>correlateid</CorrelateID><CmdResult>0</CmdResult><ResultFileURL>ftp</ResultFileURL>\
                </impl:ResultNotify></SOAP-ENV:Body></SOAP-ENV:Envelope>'

HOST, PORT = "", 8510

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(5)
print("Serving HTTP on port %s ..." % PORT)

while True:
    client_connection, client_address = listen_socket.accept()
    print("%s: Receive new soap request: " % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    request = b""
    while True:
        data = client_connection.recv(1024)
        if not data:
            break
        request += data
        if b"\r\n\r\n" in request:
            # we received the complete HTTP header
            # extract Content-Length value from header
            headers, body = request.split(b"\r\n\r\n", 1)
            header_lines = headers.decode("utf-8").split("\r\n")
            content_length = 0
            for line in header_lines:
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":")[1].strip())
                    break
            if len(body) >= content_length:
                # we received the complete message
                request = headers + b"\r\n\r\n" + body[:content_length]
                break

    if "CSPID" in request.decode("utf-8"):
        cspid = substr('CSPID',request.decode("utf-8"))
        lspid = substr('LSPID',request.decode("utf-8")) 
        correlateid = substr('CorrelateID',request.decode("utf-8"))
        fileurl = substr('CmdFileURL',request.decode("utf-8"))
        xmlfile = fileurl.split("/")[-1] 
    else:
        print ("something wrong !aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    print("CSPID: %s, LSPID: %s" %(cspid,lspid))
    print("CorrelateID: %s" %correlateid)
    print("FileUrl: %s" %fileurl)

    try:
        client_connection.sendall(response(soap_response).encode("utf-8"))
    except:
        print ("send response err")

    if "Connection: close" in request.decode("utf-8"):
        client_connection.close()
    else:
        # keep the connection alive
        pass

# 下载xml文件并解析
    try:
        subprocess.call('wget -O %s %s' %(xmlfile,fileurl),shell=True)
        # 解析xml文件
        list1 = xml_parser(xmlfile)
        for i in list1:
            print (i)
    except:
        print ("download xml error")

# 发送resultNotify
    url = "http://172.18.106.5:8002/scms-output-dispatcher/services/ctms_smg"
    ftp = "ftp://scms:Sxiptv_2022@172.18.106.14:21/result.xml"
    data = soap_resultnotify.replace("cspid",cspid).replace("lspid",lspid).replace("correlateid",correlateid).replace("ftp",ftp)
#    print(data)
    time.sleep(1)
    doPost(url, data)
"""
功能：可模拟下游接收节点，应答soap消息，下载xml文件，解析打印内容，并回复处理结果的resultNotify.
需要修改的配置：不同的端口修改PORT值（默认8510），回调地址修改url, ftp地址也需要按实际修改，确认可被下载。
后台执行：nohup python -u ./cdn2.py &
result.xml的内容如下：
<?xml version="1.0" encoding="UTF-8"?><xsi:ADI xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Reply><Property Name="Result">0</Property><Property Name
="Description">Success</Property></Reply></xsi:ADI>
"""