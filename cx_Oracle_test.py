import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir="/Users/hanxiong/Downloads/instantclient_19_8")
file6 = open("命中电影.txt", "w")
file7 = open("命中连续剧.txt", "w")
with open("待比对.txt", encoding="utf8") as f:
    list1 = f.read().split("\n")
#     print(list1)
conn = cx_Oracle.connect("wacos/nmBKsmp2015@172.25.116.5:1521/orcl")
for program_name in list1:
    cursor = conn.cursor()
    sql = (
        "select name 名称 ,contentprovider 内容提供商,code,status 状态,stockoutflag 出库标识 from program where name="
        + "'"
        + program_name
        + "'"
    )
    # 	print (sql)
    cursor.execute(sql)
    row = cursor.fetchall()
    # 	if row:
    # 		print (row)
    for i in row:
        print(i, file=file6)
    cursor.close()

for program_name in list1:
    cursor = conn.cursor()
    sql = (
        "select name 名称 ,contentprovider 内容提供商,code,status 状态,stockoutflag 出库标识 from series where name="
        + "'"
        + program_name
        + "'"
    )
    # 	print (sql)
    cursor.execute(sql)
    row = cursor.fetchall()
    # 	if row:
    # 		print (row)
    for i in row:
        print(i, file=file7)
    cursor.close()
file6.close
file7.close
