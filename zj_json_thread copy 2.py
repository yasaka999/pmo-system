# _*_coding:utf-8_*_
import json
import time
import cx_Oracle
import threading
import sys
import queue

cx_Oracle.init_oracle_client(lib_dir="/Users/hanxiong/Downloads/instantclient_19_8")

class Reader(threading.Thread):
    def __init__(self, thread_id):
        super(Reader, self).__init__()
        self.thread_id = thread_id
 
    def run(self):
        global q
 
        temp_list = q.get()
        conn = cx_Oracle.connect("credb/oss@www.homegw.ml:1522/orcl")
        cursor = conn.cursor()
        print("连接数据库成功")
        sql = ("select name,genres,columntype from credb.ws_mergedmedia where c2code=:1")
        for line in temp_list:
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
 
 
class Partition(object):
    def __init__(self, file_name, thread_num):
        self.file_name = file_name
        self.block_num = thread_num
 
    #按照线程数对文件进行分块并存进queue中
    def part_and_queue(self):
        pos_list = []
        #文件总行数
        with open(self.file_name, 'rb') as f:
          count = 0
          buf_size = 1024 * 1024
          buf = f.read(buf_size)
          while buf:
            count += buf.count(b'\n')
            buf = f.read(buf_size)
        file_size = count
        #按照线程数分成对应块的大小
        block_size = file_size / self.block_num
        start_pos = 0
        global q
 
        for i in range(self.block_num):
            if i == self.block_num - 1:
                end_pos = file_size - 1
                pos_list.append((start_pos, end_pos))
                break
            end_pos = start_pos + block_size - 1
            if end_pos >= file_size:
                end_pos = file_size - 1
            if start_pos >= file_size:
                break
            pos_list.append((start_pos, end_pos))
            start_pos = end_pos + 1
 
        #读取每块内容存进queue中
        fd = open(self.file_name, 'r')
        for pos_tu in pos_list:
            temp_text = []
            start = pos_tu[0]
            end = pos_tu[1]
 
            while start <= end:
                text = fd.readline().strip('\n')
                temp_text.append(text)
                start = start + 1
 
            q.put(temp_text)
        fd.close()
 
 
if __name__ == '__main__':
    file_name = '../files/isrs_youlike.txt'
 
    #线程数量可配
    thread_num = 30
    #起始时间
    start_time = time.time()
    q = queue.Queue()
    p = Partition(file_name, thread_num)
    t = []
    p.part_and_queue()
 
    for i in range(thread_num):
        t.append(Reader(i))
    for i in range(thread_num):
        t[i].start()
    for i in range(thread_num):
        t[i].join()
    
    end_time = time.time()
    print ("Cost time is %f" % (end_time - start_time))