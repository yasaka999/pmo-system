#!/usr/bin/python
# -*- coding:gb2312 -*-

import codecs
import datetime
import logging
import os
import shutil
import sys
import time
import xml.dom.minidom as Dom

import ConfigParser
import cx_Oracle

reload(sys)
sys.setdefaultencoding("utf8")

picturedir = ""


def copyfile(filepath):

    filedir = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    newdir = "/opt/wenke/expxml_program/data/picture/" + filedir

    if not os.path.exists(newdir):
        os.makedirs(newdir)

    os.system(
        "cp %s %s"
        % ("/opt/wacos/CTMSData/picture/" + filepath, newdir + "/" + filename)
    )


#  if os.path.isfile (newdir+'/'+filename):
#    print filepath+" Copy Success"
#  else:
#    print filepath+" Copy Failed"


def Indent(dom, node, indent=0):
    children = node.childNodes[:]
    if indent:
        text = dom.createTextNode("\n" + "\t" * indent)
        node.parentNode.insertBefore(text, node)
    if children:
        if children[-1].nodeType == node.ELEMENT_NODE:
            text = dom.createTextNode("\n" + "\t" * indent)
            node.appendChild(text)
        for n in children:
            if n.nodeType == node.ELEMENT_NODE:
                Indent(dom, n, indent + 1)


def dealprogram(programrecord):
    (name, code) = (programrecord[0], programrecord[1])
    print (name, code)

    doc = Dom.Document()
    root_node = doc.createElement("ADI")
    root_node.setAttribute("StaffID", "999999999")
    root_node.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    doc.appendChild(root_node)
    objects_node = doc.createElement("Objects")
    object_node = doc.createElement("Object")

    object_node.setAttribute("Action", "DELETE")
    object_node.setAttribute("Code", str(code))
    object_node.setAttribute("ElementType", "Program")
    object_node.setAttribute("ID", str(code))

    Property_node = doc.createElement("Property")
    Property_node.setAttribute("Name", "Name")
    Property_value = doc.createTextNode(str(name))
    Property_node.appendChild(Property_value)
    object_node.appendChild(Property_node)

    objects_node.appendChild(object_node)
    root_node.appendChild(objects_node)
    domcopy = doc.cloneNode(True)
    Indent(domcopy, domcopy.documentElement)
    f = file(
        "/opt/wenke/expxml_program/data/delProgram_" + str(1000000000 + code) + ".xml",
        "wb",
    )
    writer = codecs.lookup("utf-8")[3](f)
    domcopy.writexml(writer, encoding="utf-8")
    domcopy.unlink()
    f.close()


if __name__ == "__main__":

    config = ConfigParser.ConfigParser()
    config.readfp(open("/opt/wenke/expxml_program/expxml_program.conf", "rb"))
    database = config.get("global", "database")
    databaseuser = config.get("global", "databaseuser")
    databasepassword = config.get("global", "databasepassword")
    sqlbase = config.get("global", "sqlbase")
    sqlwhere = config.get("global", "sqlwhere")
    picturedir = config.get("global", "picturedir")
    nCount = 0
    print "Database Info:", database, databaseuser, databasepassword
    #  db = cx_Oracle.connect('wacos','oss','10.50.13.101:1521/orcl')
    print "Connecting Database"
    db = cx_Oracle.connect(databaseuser, databasepassword, database)
    print "Connect Database Success"
    cr = db.cursor()

    #  sql='select programid,name,code,to_char(licensingwindowstart,\'yyyymmddhh24miss\'),to_char(licensingwindowend,\'yyyymmddhh24miss\'),kpeople,director from program where rownum<20'
    sql = sqlbase + " " + sqlwhere
    print "GetData SQL: ", sql

    cr.execute(sql)
    rs = cr.fetchone()
    print "Begin process exp programs"
    while rs:
        nCount = nCount + 1
        now = time.strftime("%H%M%S") + str(datetime.datetime.now().microsecond)
        if nCount % 10 == 0:
            print now + " : Processed " + str(nCount) + " programs"
        dealprogram(rs)
        rs = cr.fetchone()
    now = time.strftime("%H%M%S") + str(datetime.datetime.now().microsecond)
    print now + " : Processed " + str(nCount) + " programs"
    print "Finished process exp programs"
    cr.close()
    db.close()

    rs = ("abcd", 123456)
    dealprogram(rs)
