# 增加了对文件编码格式的判断和转换,统一转成utf8
# 增加对节目单时间顺序有效性的判断,开始时间如果正确可以自动纠正
# 增加对跨0点节目单的切割
# 使用格式：schedule_format_nm.py 源文件名
import datetime
import sys
import re
import codecs
import chardet

def detect(contents):
    result = chardet.detect(contents)
    return result['encoding']

def detect_and_read_file(filename):
    with open(filename, 'rb') as f:
        contents = f.read()
    encoding = detect(contents)
    if encoding != 'UTF-8':
        contents = contents.decode(encoding).encode('utf-8')
    return contents.decode('utf-8')

#in_file = "../files/test1.9—1.15.txt"
in_file = sys.argv[1]

f= detect_and_read_file(in_file)
list1 = f.split("\n")
list2 = []
channel_name = list1[0].split(':')[1].rstrip()
start_date = list1[1].split(':')[1].rstrip()
tmp_date = datetime.datetime.strptime(start_date, '%Y%m%d')
new_date = tmp_date.strftime('%Y%m%d')
out_file = codecs.open(in_file[:-4]+'-format.txt', 'w','utf-8')

print("Channel:%s" % channel_name, file=out_file)
print("Date:%s" % new_date, file=out_file)
for i in range(len(list1)):
    if re.search(r'\d.*-', list1[i]):
        # 有些数据缺|，统一先去掉
        list1[i] = list1[i].replace('|','').rstrip()
        list2.append(list1[i])

for i in range(len(list2)):
    if i < len(list2) - 1:
        time_start = list2[i][:4]
        time_end = list2[i + 1][:4]
        schedule_name = list2[i][9:]
        
        if time_start[:1] == '2' and time_end[:1] == '0' :
            tmp_date = tmp_date + datetime.timedelta(days=1)
            new_date = tmp_date.strftime('%Y%m%d')
            print(time_start + '-0000' + '|' +schedule_name,file=out_file)
            print("Date:%s" % new_date, file=out_file)
            if time_end != '0000':
                print('0000' + '-' + time_end + '|' + schedule_name,file=out_file)
        elif time_start>=time_end :
            print ("Error:节目单时间有误：%s 前一条%s,后一条%s" %(new_date,list2[i],list2[i+1]))
        else:
            print(time_start + '-' + time_end + '|' +schedule_name,file=out_file)
            
    else:
        time_start = list2[i][:4]
        time_end = list2[i][5:9]
        schedule_name = list2[i][9:]
        
        if time_start[:1] == '2' and time_end[:1] == '0':
            tmp_date = tmp_date + datetime.timedelta(days=1)
            new_date = tmp_date.strftime('%Y%m%d')
            print(time_start + '-0000' + '|' +schedule_name,file=out_file)
            print("Date:%s" % new_date, file=out_file)
            print('0000' + '-' + time_end + '|' + schedule_name,file=out_file)
        else:
            print(time_start + '-' + time_end + '|' +schedule_name,file=out_file)
out_file.close()
print ("%s节目单转换完成：生成文件%s" %(channel_name,in_file[:-4]+'-format.txt'))

