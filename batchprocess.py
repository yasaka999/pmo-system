#!/usr/bin/python
import datetime
import logging
import os
import shutil
import time

import ConfigParser
import urllib2

HTTP_POST_HEADERS = {"SOAPAction": "test", "content-type": "application/xml"}
# 添加日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(threadName)-8s %(levelname)-5s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    filename="/opt/wenke/batchprocessxml/batchprocessxml.log",
    filemode="w",
)
# 对配置文件的定义与使用
config = ConfigParser.ConfigParser()
config.readfp(open("/opt/wenke/batchprocessxml/batchprocessxml.conf", "rb"))
sourcedir = config.get("global", "sourcedir")
desturl = config.get("global", "desturl")
ftpurl = config.get("global", "ftpurl")
lspid = config.get("global", "lspid")
cspid = config.get("global", "cspid")
# 打印配置文件中的获取的参数
print "Source Dir: " + sourcedir
print "DestUrl :" + desturl
print "FtpUrl :" + ftpurl
print "LspID :" + lspid
print "CspID :" + cspid
# 写日志
logging.debug("Source Dir: " + sourcedir)
logging.debug("DestUrl :" + desturl)
logging.debug("FtpUrl :" + ftpurl)
logging.debug("LspID :" + lspid)
logging.debug("CspID :" + cspid)
# 定义soap消息体内容
SoapEnvdata = '<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:impl="iptv">'
SoapEnvdata = (
    SoapEnvdata
    + '<SOAP-ENV:Body SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><impl:ExecCmd><CSPID xsi:type="xsd:string">'
    + cspid
    + '</CSPID><LSPID xsi:type="xsd:string">'
    + lspid
    + "</LSPID>"
)
SoapEnvEnddata = "</impl:ExecCmd></SOAP-ENV:Body></SOAP-ENV:Envelope>"
# 定义post请求的函数
def doPost(url, data=None, filename=None):
    postReq = urllib2.Request(url=url, headers=HTTP_POST_HEADERS, data=data)
    try:
        response = urllib2.urlopen(postReq, timeout=3)
        if response.getcode() != 200:
            print response.getcode()
            print filename + " Fail"
            logging.debug(filename + " Fail" + response.getcode())
            return -1
        else:
            print filename + " Sucess"
            logging.debug(filename + " sucess")
            return 0
    except Exception, e:
        print filename + " send soap request Fail,check DestUrl"
        logging.debug(filename + " response exception: %s" % (e))
        return -1


def main():

    if not os.path.exists(sourcedir + "/"):
        print "Sourcedir not exists,Create it " + sourcedir
        os.makedirs(sourcedir + "/")

    if not os.path.exists(sourcedir + "/bak/"):
        print "Back dir not exists,Create it " + sourcedir + "/bak/"
        os.makedirs(sourcedir + "/bak/")

    listfile = os.listdir(sourcedir)

    listfile.sort()
    for line in listfile:
        if line[-4:] == ".xml":
            now = time.strftime("%H%M%S") + str(datetime.datetime.now().microsecond)
            CorrelateIDdata = (
                '<CorrelateID xsi:type="xsd:string">' + now + "</CorrelateID>"
            )
            shutil.move(sourcedir + "/" + line, sourcedir + "/bak/" + line)
            CmdFileUrldata = (
                '<CmdFileURL xsi:type="xsd:string">'
                + ftpurl
                + sourcedir
                + "/bak/"
                + line
                + "</CmdFileURL>"
            )
            servicedata = (
                SoapEnvdata + CorrelateIDdata + CmdFileUrldata + SoapEnvEnddata
            )
            doPost(desturl, servicedata, line)
            time.sleep(0.2)


if __name__ == "__main__":
    main()
