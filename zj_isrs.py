# encoding:utf-8 
from __future__ import print_function
import json
import time
import cx_Oracle
import os
import sys
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.utf8'
reload(sys)
sys.setdefaultencoding('utf-8') 
out_file = open('result2.txt', 'w')

conn = cx_Oracle.connect("credb/oss@172.28.102.4:1521/orcl")
cursor = conn.cursor()
print("connect success")
sql = ("select type ,name,genres,columntype from credb.ws_mergedmedia where c2code=:1")
with open('/opt/hadoop/hadoop-data/datanode/data4/yhshoushi/20221212/isrs_youlike_20221211.txt', 'r') as f:
    for line in f:
        data = json.loads(line)
        userid = data['userId']
        code_list = data['videoSimilarityDTOList']
        for i in range(0, 11):
#       print (code_list[0]['code'])
            cursor.execute(sql, (str(code_list[i]['code']),))
            row = cursor.fetchone()
#       print (row)
        #type = row[0]
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(now,userid.encode('utf-8'),code_list[i]['code'].encode('utf-8'),row[0],row[1],row[2],row[3],sep='|')

cursor.close()
conn.close()
out_file.close()
