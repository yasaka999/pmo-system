# 使用格式：schedule_format.py 源文件名 频道名称 开始日期20221001
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

def adapter_format(list1,channel_name,start_date):
    list2 = []
#    channel_name = list1[0].split(':')[1].rstrip()
#    start_date = list1[1].split(':')[1].rstrip()
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

def other_format(list1,channel_name,start_date):
    list2 = []
    tmp_date = datetime.datetime.strptime(start_date, '%Y%m%d')
    new_date = tmp_date.strftime('%Y%m%d')
    out_file = codecs.open(in_file[:-4]+'-format.txt', 'w','utf-8')
    print("Channel:%s" % channel_name, file=out_file)
    print("Date:%s" % new_date, file=out_file)

    for i in range(len(list1)):
        # 中文冒号转换为英文冒号
        list1[i] = list1[i].replace("：", ":")
        # 山西的节目单有含冒号的非有效数据，这里用包含数字和冒号的正则表达式去除
        if re.search(r'\d.*:', list1[i]):
            # 需要一些特殊处理的数据在这里修正
            list1[i] = list1[i].replace(chr(0xa0), '').replace(' ', '').replace("::", ":").replace('　','').replace('	','')\
                .replace('24:','00:').rstrip(":")
            if len(list1[i].split(':', 1)[0]) == 1:
                print("warn: 时间格式异常：%s" % list1[i])
                list1[i] = "0" + list1[i]
            if len(list1[i].split(':', 1)[0]) >2:
                print ("Error: 时间格式错误：%s" % list1[i])
                list1[i] = list1[i][1:]
            list_temp = []
            list_temp.append(list1[i][:5])
            list_temp.append(list1[i][5:])
            list2.append(list_temp)

    for i in range(len(list2)):
        if i < len(list2) - 1:
            time_temp = list2[i + 1][0][:5].replace(':', '')
            
            if list2[i][0][:1] == '2' and list2[i + 1][0][:1] == '0':
                tmp_date = tmp_date + datetime.timedelta(days=1)
                new_date = tmp_date.strftime('%Y%m%d')
                print(list2[i][0].replace(':', '') + '-0000' + '|' +
                    list2[i][1],file=out_file)
                print("Date:%s" % new_date, file=out_file)
                if time_temp != '0000':
                    print('0000' + '-' + time_temp + '|' +list2[i][1],file=out_file)
            elif list2[i][0]>=list2[i+1][0]:
                print ("Error:节目单时间有误：%s 前一条%s,后一条%s" %(new_date,list2[i],list2[i+1]))
            else:
                print(list2[i][0].replace(':', '') + '-' + time_temp + '|' +
                    list2[i][1],file=out_file)

        else:
            end_time = list2[0][0][:5].replace(':', '')
            
            if list2[i][0][:1] == '2' and list2[0][0][:1] == '0':
                tmp_date = tmp_date + datetime.timedelta(days=1)
                new_date = tmp_date.strftime('%Y%m%d')
                print(list2[i][0].replace(':', '') + '-0000' + '|' +
                    list2[i][1],file=out_file)
                print("Date:%s" % new_date, file=out_file)
                print('0000' + '-' + end_time + '|' +list2[i][1],file=out_file)
            elif list2[i][0]>=list2[0][0]:
                print ("Error:节目单时间有误：%s 前一条%s,后一条%s" %(new_date,list2[i],list2[0]))
            else:
                print(list2[i][0].replace(':', '') + '-' + end_time + '|' +
                    list2[i][1],file=out_file)
    out_file.close()
    

if __name__ == '__main__':
    in_file = sys.argv[1]
    channel_name = sys.argv[2]
    start_date = sys.argv[3]
    f= detect_and_read_file(in_file)
    list1 = f.split("\n")
    if list1[0][:7] == 'Channel':
        adapter_format(list1,channel_name,start_date)
    else:
        other_format(list1,channel_name,start_date)
    print ("%s节目单转换完成：生成文件%s" %(channel_name,in_file[:-4]+'-format.txt'))

