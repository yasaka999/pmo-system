#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import shutil
import time
import datetime
import urllib2
import xml.dom.minidom as Dom    
import codecs, sys
import pymysql
import ConfigParser
import logging
reload(sys)
sys.setdefaultencoding('utf8')

config = ConfigParser.ConfigParser()
config.readfp(open('/opt/tools/delschedule/del_schedule.conf', "rb"))
host = config.get("host","hosts")
database = config.get("global", "database")
user = config.get("global", "user")
password = config.get("global", "password")
sourcedir = config.get("global", "sourcedir")
desturl = config.get("global", "desturl")
ftpurl = config.get("global", "ftpurl")
lspid = config.get("global", "lspid")
cspid = config.get("global", "cspid")

#去空行和BOM格式转换
file1 = open('/opt/tools/delschedule/channelname.txt', 'r')
file2 = open('/opt/tools/delschedule/channelname_new.txt', 'w')
try:
    for line in file1.readlines():
        if line == '\n':
            line = line.strip("\n")
        elif line[:3] == codecs.BOM_UTF8:
                line = line[3:]
        file2.write(line)
finally:
    file1.close()
    file2.close()
shutil.move('/opt/tools/delschedule/channelname.txt','/opt/tools/delschedule/channelname.txt.bak')
shutil.move('/opt/tools/delschedule/channelname_new.txt','/opt/tools/delschedule/channelname.txt')

            
#从文件中提取时间和频道名
with open('/opt/tools/delschedule/channelname.txt', 'r') as f1:
    channelname = f1.readlines()
starttime= channelname[0].rstrip('\n')
endtime = channelname[1].rstrip('\n')
for i in range(0, len(channelname)):
    channelname[i] = channelname[i].rstrip('\n')
channelname=channelname[2:]

def Indent(dom, node, indent = 0):
    children = node.childNodes[:]
    if indent:
        text = dom.createTextNode('\n' + '\t' * indent)
        node.parentNode.insertBefore(text, node)
    if children:
        if children[-1].nodeType == node.ELEMENT_NODE:
            text = dom.createTextNode('\n' + '\t' * indent)
            node.appendChild(text)
        for n in children:
            if n.nodeType == node.ELEMENT_NODE:
                Indent(dom, n, indent + 1)


def dealschedule(schedulerecord_list):
    doc = Dom.Document()  
    root_node = doc.createElement("ADI")  
    root_node.setAttribute("StaffID", "999999999")   
    root_node.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")  
    doc.appendChild(root_node) 
    for schedulerecord in schedulerecord_list:
      (code,channelid,channelcode,scheduleid)=(schedulerecord[0],schedulerecord[1],schedulerecord[2],schedulerecord[3])
    
      Objects_node = doc.createElement("Objects")
      Object_node = doc.createElement("Object")
      Object_node.setAttribute("ElementType","Schedule")
      Object_node.setAttribute("Action","DELETE")
      Object_node.setAttribute("Code",str(code))
      Object_node.setAttribute("ID",str(code))
                
      Property_node=doc.createElement("Property")
      Property_node.setAttribute("Name","ChannelID")
      Property_value = doc.createTextNode(str(channelid)) 
      Property_node.appendChild(Property_value)
      Object_node.appendChild(Property_node)

      Property_node=doc.createElement("Property")
      Property_node.setAttribute("Name","ChannelCode")
      Property_value = doc.createTextNode(str(channelcode)) 
      Property_node.appendChild(Property_value)
      Object_node.appendChild(Property_node)
                  
      Objects_node.appendChild(Object_node)
      root_node.appendChild(Objects_node) 
    
    domcopy = doc.cloneNode(True)                      
    Indent(domcopy, domcopy.documentElement)    
    f = file('/opt/tools/delschedule/data/schedule_'+str(1000000000+scheduleid)+'.xml', 'wb')                     
    writer = codecs.lookup('utf-8')[3](f)       
    domcopy.writexml(writer, encoding = 'utf-8')
    domcopy.unlink() 
    f.close()
    
HTTP_POST_HEADERS = {'SOAPAction': 'test','content-type':'application/xml'}
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(threadName)-8s %(levelname)-5s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='/opt/tools/delschedule/del_schedule.log',
                    filemode='w')

print 'Source Dir: '+sourcedir
print 'DestUrl :' + desturl
print 'FtpUrl :'+ ftpurl
print 'LspID :'+lspid
print 'CspID :'+cspid
logging.debug('Source Dir: '+sourcedir)
logging.debug('DestUrl :' + desturl)
logging.debug('FtpUrl :' + ftpurl)
logging.debug('LspID :' + lspid)
logging.debug('CspID :' + cspid)
SoapEnvdata = '<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:impl="iptv">'
SoapEnvdata = SoapEnvdata+'<SOAP-ENV:Body SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><impl:ExecCmd><CSPID xsi:type="xsd:string">'+cspid+'</CSPID><LSPID xsi:type="xsd:string">'+lspid+'</LSPID>'
SoapEnvEnddata ='</impl:ExecCmd></SOAP-ENV:Body></SOAP-ENV:Envelope>'

def doPost(url, data=None,filename=None):
    postReq = urllib2.Request(url=url, headers=HTTP_POST_HEADERS, data=data)
    try:
        response = urllib2.urlopen(postReq, timeout=8)
        if (response.getcode() != 200):
            print response.getcode()
            print filename+' Fail'
            logging.debug(filename+' Fail'+response.getcode())
            return -1
        else:
            print filename+' Sucess'
            logging.debug(filename+' sucess')
            return 0
    except Exception, e:
        print filename+' send soap request Fail,check DestUrl'
        logging.debug(filename+" response exception: %s" % (e))
        return -1

def main():     
#  db=cx_Oracle.connect(databaseuser,databasepassword,database)
  db = pymysql.connect(host="127.0.0.1",user="scms",password="",database=database)
  print "Connect Database Success"
  print 'starttime: ',starttime
  print 'endtime: ',endtime
  cr=db.cursor() 
  for name in channelname:
    sql1 = "select s.play_start_date ,s.out_source_id,c.channel_id,c.out_source_id,s.schedule_id from cms_pre_channel c,cms_pre_schedule_base s where s.channel_out_source_id =c.out_source_id\
      and c.is_cp_delete =0 and c.channel_name in ("
    sql2 = ") and  s.play_start_date between '"
    sql3 = "' and '"
    sql4 = "'"
  #  sql = sql1+channelname+sql2+starttime+sql3+endtime+sql4
    sql = sql1+ name+sql2+starttime+sql3+endtime+sql4
    print 'GetData SQL: ',sql
    
    nCount=0 
    cr.execute(sql)
    rs=cr.fetall()
    print "Begin process exp schedule"
    while rs:
      nCount = nCount + 1
      now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
      if (nCount%10==0): 
        print now+" : Processed "+str(nCount)+" schedule"

      dealschedule(rs)
      rs=cr.fetchone()
    now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
    print now+" : Processed "+str(nCount)+" schedule"  
    print "Finished process exp schedule"
  cr.close()
  db.close()

  if not os.path.exists(sourcedir+'/'):
    print 'Sourcedir not exists,Create it '+sourcedir
    os.makedirs(sourcedir+'/')
    
  if not os.path.exists(sourcedir+'/bak/'):
    print 'Back dir not exists,Create it '+sourcedir+'/bak/'
    os.makedirs(sourcedir+'/bak/')
   
  listfile=os.listdir(sourcedir)
  
  listfile.sort()
  for line in listfile:  
    if (line[-4:] == '.xml') :
      now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
      CorrelateIDdata='<CorrelateID xsi:type="xsd:string">'+now+'</CorrelateID>'
      shutil.move(sourcedir+'/'+line,sourcedir+'/bak/'+line)
      CmdFileUrldata='<CmdFileURL xsi:type="xsd:string">'+ftpurl+sourcedir+'/bak/'+line+'</CmdFileURL>'
      servicedata=SoapEnvdata+CorrelateIDdata+CmdFileUrldata+SoapEnvEnddata
#      doPost(desturl, servicedata,line)
      time.sleep(0.2)
if __name__ == "__main__":
  main()
