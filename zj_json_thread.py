import json
import time
import cx_Oracle
from threading import Thread

cx_Oracle.init_oracle_client(lib_dir="/Users/hanxiong/Downloads/instantclient_19_8")


def isrs_youlike(filename):
    conn = cx_Oracle.connect("credb/oss@www.homegw.ml:1522/orcl")
    cursor = conn.cursor()
    print("连接数据库成功")
    sql = ("select name,genres,columntype from credb.ws_mergedmedia where c2code=:1")
# 打开 JSON 文件
    with open(filename, 'r') as f:
    # 逐行读取文件
        for line in f:
        # 将每行转换为 Python 字典
            data = json.loads(line)
            userid = data['userId']
            code_list = data['videoSimilarityDTOList']
        #cursor.execute(sql, (code_list[0]['code'],))
        #row = cursor.fetchone()
        #type = row[0]
        #now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #print (now,userid,code_list[0]['code'],type,row[1])
            type = ['001','002','004','005','type113']
            for i in range (len(code_list)):
                if  type:
                    cursor.execute(sql, (code_list[i]['code'],))
                    row = cursor.fetchone()
                    if row[2] in type:
                        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        print (now,userid,code_list[i]['code'],row[0],row[1],row[2])
                        type.remove(row[2])
    cursor.close()
    conn.close()


with open('file.txt', 'r') as f:
    # 每次读10行，并使用Thread模块创建10个新线程，并使用这些线程处理这10行
    while True:
        lines = f.readlines(10)
        if not lines:
            break
        threads = [Thread(target=isrs_youlike, args=(lines,)) for _ in range(10)]
        for thread in threads:
            thread.start()
