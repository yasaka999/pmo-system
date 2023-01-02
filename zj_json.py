import json
import time
import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir="/Users/hanxiong/Downloads/instantclient_19_8")


conn = cx_Oracle.connect("credb/oss@www.homegw.ml:1522/orcl")
cursor = conn.cursor()
print("连接数据库成功")
sql = ("select type,columnname from credb.ws_mergedmedia where c2code=:1")
# 打开 JSON 文件
with open('../files/isrs_youlike.txt', 'r') as f:
    # 逐行读取文件
    for line in f:
        # 将每行转换为 Python 字典
        data = json.loads(line)
        userid = data['userId']
        code_list = data['videoSimilarityDTOList']
        cursor.execute(sql, (code_list[0]['code'],))
        row = cursor.fetchone()
        type = row[0]
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print (now,userid,code_list[0]['code'],type,row[1])
        for i in range (1,len(code_list)):
            cursor.execute(sql, (code_list[i]['code'],))
            row = cursor.fetchone()
            if row[0] != type:
                now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print (now,userid,code_list[i]['code'],row[0],row[1])
                break

cursor.close()
conn.close()

