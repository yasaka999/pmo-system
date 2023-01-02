# _*_coding:utf-8_*_
import json
import time
import cx_Oracle
#import threading
from multiprocessing import Process

cx_Oracle.init_oracle_client(lib_dir="/Users/hanxiong/Downloads/instantclient_19_8")

def trunk_process(file_name,start_pos,end_pos):
    fd = open(file_name, 'r')
    '''
    该if块主要判断分块后的文件块的首位置是不是行首，
    是行首的话，不做处理
    否则，将文件块的首位置定位到下一行的行首
    '''
    if start_pos != 0:
      fd.seek(start_pos-1)
      if fd.read(1) != '\n':
        line = fd.readline()
        start_pos = fd.tell()
    fd.seek(start_pos)
    
    conn = cx_Oracle.connect("credb/oss@www.homegw.ml:1522/orcl")
    cursor = conn.cursor()
    print("连接数据库成功")
    sql = ("select name,genres,columntype from credb.ws_mergedmedia where c2code=:1")
    while (start_pos <= end_pos):
          line = fd.readline()
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

'''
对文件进行分块，文件块的数量和线程数量一致
'''
class Partition(object):
  def __init__(self, file_name, thread_num):
    self.file_name = file_name
    self.block_num = thread_num
 
  def part(self):
    fd = open(self.file_name, 'r')
    fd.seek(0, 2)
    pos_list = []
    file_size = fd.tell()
    block_size = file_size/self.block_num
    start_pos = 0
    for i in range(self.block_num):
      if i == self.block_num-1:
        end_pos = file_size-1
        pos_list.append((file_name,start_pos, end_pos))
        break
      end_pos = start_pos+block_size-1
      if end_pos >= file_size:
        end_pos = file_size-1
      if start_pos >= file_size:
        break
      pos_list.append((file_name,start_pos, end_pos))
      start_pos = end_pos+1
    fd.close()
    return pos_list
 
if __name__ == '__main__':
  file_name = '../files/isrs_youlike.txt'
  #线程数量
  process_num = 30
  #起始时间
  start_time = time.time()
  m = Partition(file_name, process_num)
  t = m.part()


  ps=[]
  # 创建子进程实例
  for i in range(len(t)):
    p=Process(target=trunk_process,name="worker"+str(i),args=t[i])
    ps.append(p)
  # 开启进程
  for i in range(process_num):
    ps[i].start()
  # 阻塞进程
  for i in range(process_num):
    ps[i].join()
  print("主进程终止")

  #结束时间
  end_time = time.time()
  print ("Cost time is %f" % (end_time - start_time))

