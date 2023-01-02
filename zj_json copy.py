import json
import time
import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir="/Users/hanxiong/Downloads/instantclient_19_8")


conn = cx_Oracle.connect("credb/oss@www.homegw.ml:1522/orcl")
cursor = conn.cursor()
print("连接数据库成功")
sql = ("select name,genres,columntype from credb.ws_mergedmedia where c2code=:1")
# 打开 JSON 文件
with open('../files/isrs_youlike.txt', 'r') as f:
    # 逐行读取文件
    for line in f:
        # 将每行转换为 Python 字典
        data = json.loads(line)
        userid = data['userId']
        code_list = data['videoSimilarityDTOList']
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

