#!/usr/bin/python
# -*- coding:gb2312 -*-

import xml.dom.minidom as Dom    
import  codecs, sys
import cx_Oracle
import os
import shutil
import time
import datetime
import ConfigParser
import logging

reload(sys)
sys.setdefaultencoding('utf8')

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


def dealprogram(programrecord):
    (code,picturecode)=(programrecord[0],programrecord[1])
   
    doc = Dom.Document()  
    root_node = doc.createElement("ADI")  
    root_node.setAttribute("StaffID", "999999999")   
    root_node.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")  
    doc.appendChild(root_node)  


    objects_node = doc.createElement("Objects")
    object_node = doc.createElement("Object")
    
    object_node.setAttribute("Action", "REGISTER")
    object_node.setAttribute("Code", str(code))
    object_node.setAttribute("ElementType","Program")
    object_node.setAttribute("ID",str(code))


    objects_node.appendChild(object_node)
     
    root_node.appendChild(objects_node) 

    
    mappings_node = doc.createElement("Mappings")
 
    mapping_node = doc.createElement("Mapping")
    mapping_node.setAttribute("Action","DELETE")

    mapping_node.setAttribute("ElementCode",str(code))
    mapping_node.setAttribute("ElementID",str(code))
    mapping_node.setAttribute("ElementType","Program")
    mapping_node.setAttribute("ParentCode",str(picturecode))
    mapping_node.setAttribute("ParentID",str(picturecode))
    mapping_node.setAttribute("ParentType","Picture")

                
    mappings_node.appendChild(mapping_node)
                        
    root_node.appendChild(mappings_node) 
          
    domcopy = doc.cloneNode(True)                      
    Indent(domcopy, domcopy.documentElement)    
    f = file('/opt/wenke/expxml_program/data/delPic_'+str(code)+'_'+str(picturecode)+'.xml', 'wb')                     
    writer = codecs.lookup('utf-8')[3](f)       
    domcopy.writexml(writer, encoding = 'utf-8')
    domcopy.unlink() 
    f.close()
  
if __name__ == "__main__":  

  config = ConfigParser.ConfigParser()
  config.readfp(open('/opt/wenke/expxml_program/expxml_program.conf', "rb"))
  database = config.get("global", "database")
  databaseuser = config.get("global", "databaseuser")
  databasepassword = config.get("global", "databasepassword")
  sqlbase=config.get("global", "sqlbase")
  sqlwhere=config.get("global", "sqlwhere")
  picturedir=config.get("global", "picturedir")

  print "Database Info:",database,databaseuser,databasepassword
#  db = cx_Oracle.connect('wacos','oss','10.50.13.101:1521/orcl')
  print "Connecting Database"
  db=cx_Oracle.connect(databaseuser,databasepassword,database)
  print "Connect Database Success"
  
  cr=db.cursor()
  sql='select a.code programcode,c.code picturecode from program a,picturemap b,metapicture c \
          where b.objtype=''4'' and a.programid=b.objid and b.metapictureid=c.metapictureid and c.status =''0'' order by a.code'
          

  nCount=0 
  cr.execute(sql)
  rs=cr.fetchone()
  print "Begin process exp program"
  while rs:
    nCount = nCount + 1
    now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
    if (nCount%10==0): 
       print now+" : Processed "+str(nCount)+" program"

    dealprogram(rs)
    rs=cr.fetchone()
  now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
  print now+" : Processed "+str(nCount)+" program"  
  print "Finished process exp program"
  cr.close()
  db.close()