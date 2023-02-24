# 中文冒号转换为英文冒号
# 提取实际节目单所在行的数据
# 去空格和0xa0及其他异常字符及格式修正
# 拼出结束时间，最后一条结束时间取第一条的开始时间
# 添加频道名称
# 按每日分隔，添加date
# 有些异常的判断处理：时间格式不是ab:cd；有ab::cd的要做替换
# 增加了对文件编码格式的判断和转换,统一转成utf8
# 增加对节目单时间顺序有效性的判断
# 增加对跨0点节目单的切割
# 对于有24点以后节目单的，先进行清洗，替换24:为00:
# 强制输出文件编码格式为utf8
# 修正对于00:00节目单的bug
# 使用格式：schedule_format2.py 源文件名 频道名称 开始日期20221001
import datetime
import sys
import re
import chardet
import codecs

def detect(contents):
    result = chardet.detect(contents)
    return result['encoding']

def detect_and_read_file(filename):
    with open(filename, 'rb') as f:
        contents = f.read()
    encoding = detect(contents)
#    print (encoding)
    if encoding != 'UTF-8':
        contents = contents.decode(encoding).encode('utf-8')
    return contents.decode('utf-8')

#in_file = "../files/nmtest.txt"
in_file = sys.argv[1]
channel_name = sys.argv[2]
start_date = sys.argv[3]
tmp_date = datetime.datetime.strptime(start_date, '%Y%m%d')
new_date = tmp_date.strftime('%Y%m%d')
out_file = open(in_file[:-4]+'-format.txt', 'w')
print("Channel:%s" % channel_name, file=out_file)
print("Date:%s" % new_date, file=out_file)

f= detect_and_read_file(in_file)
#with open(in_file, encoding='utf8') as f:
list1 = f.split("\n")
list2 = []
for i in range(len(list1)):
    # 中文冒号转换为英文冒号
    list1[i] = list1[i].replace("：", ":")
    # 山西的节目单有含冒号的非有效数据，这里用包含数字和冒号的正则表达式去除
    if re.search(r'\d.*:', list1[i]):
#        if ":" in list1[i]:
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
print ("%s节目单转换完成：生成文件%s" %(channel_name,in_file[:-4]+'-format.txt'))
