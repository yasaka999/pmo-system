#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import shutil
import time
import datetime
import codecs, sys
import cx_Oracle
import ConfigParser
#reload(sys)
#sys.setdefaultencoding('utf8')
def DupSchedule (sChannel,dChannel):
    airdate=(datetime.datetime.today()+datetime.timedelta(days=1)).strftime("%Y%m%d")
    airdate=(datetime.datetime.today()).strftime("%Y%m%d")
    f.write("Channel:"+dChannel+"\n")
    f.write("Date:"+str(airdate)+"\n")
    db=cx_Oracle.connect(databaseuser,databasepassword,database)
#    print "Connect Database Success"
    cr=db.cursor() 
    sql1 = "select to_char(airstarttime,'hh24mi'),to_char(airendtime,'hh24mi'),name,airdate from schedule where source='"
    sql2 = "' and airdate >='"
    sql3 = "' order by scheduleid"
    sql = sql1+sChannel+sql2+airdate+sql3

    print 'GetData SQL: ',sql
   
    nCount=0 
    cr.execute(sql)
    rs=cr.fetchone()
    print "Begin process exp %s to %s " %(sChannel,dChannel)
    while rs:
        nCount = nCount + 1
        now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
        if (nCount%10==0): 
            print now+" : Processed "+str(nCount)+" schedule"
        item=rs[0]+"-"+rs[1]+"|"+rs[2]+"\n"
        if airdate !=rs[3]:
            airdate = rs[3]
            f.write("Date:"+str(airdate)+"\n")
        
        f.write(item)
        rs=cr.fetchone()
    now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
    print now+" : Processed "+str(nCount)+" schedule"  
    print "Finished process exp to LIVEBATCHSCHEDULE.TXT" 
    cr.close()
    db.close()
    
config = ConfigParser.ConfigParser()
config.readfp(open('/opt/xhan/dup_channel.conf', "rb"))
database = config.get("global", "database")
databaseuser = config.get("global", "databaseuser")
databasepassword = config.get("global", "databasepassword")
s_channelname = config.get("global", "schannelname")
d_channelname=config.get("global", "dchannelname")
schannelname = s_channelname.split(',')
dchannelname = d_channelname.split(',')
    
f = open ("/opt/xhan/LIVEBATCHSCHEDULE.TXT","w+")
for i in range(len(schannelname)):
    DupSchedule(schannelname[i],dchannelname[i])
f.close()

okfile = open("/opt/xhan/LIVEBATCHSCHEDULE.TXT.OK","w")
okfile.close()