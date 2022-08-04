# 中文冒号转换为英文冒号
# 提取实际节目单所在行的数据
# 去空格和0xa0及其他异常字符及格式修正
# 拼出结束时间，最后一条结束时间取第一条的开始时间
# 添加频道名称
# 按每日分隔，添加date
# 有些异常的判断处理：时间格式不是ab:cd；有ab::cd的要做替换
# 使用格式：schedule_format.py 源文件名 频道名称 开始日期
import datetime
import sys
import re

#in_file = "../files/nmtest.txt"
in_file = sys.argv[1]
#start_date = '20220801'
channel_name = sys.argv[2]
start_date = sys.argv[3]
tmp_date = datetime.datetime.strptime(start_date, '%Y%m%d')
new_date = tmp_date.strftime('%Y%m%d')
out_file = open(in_file[:-4]+"-format.txt", "w")
print("Channel:%s" % channel_name, file=out_file)
print("Date:%s" % new_date, file=out_file)
with open(in_file, encoding="utf8") as f:
    list1 = f.read().split("\n")
    list2 = []
    for i in range(len(list1)):
        # 中文冒号转换为英文冒号
        list1[i] = list1[i].replace("：", ":")
        # 山西的节目单有含冒号的非有效数据，这里用包含数字和冒号的正则表达式去除
        if re.search(r'\d.*:', list1[i]):
#        if ":" in list1[i]:
            # 需要一些特殊处理的数据在这里修正
            list1[i] = list1[i].replace(chr(0xa0), '').replace(' ', '').replace("::", ":").replace('　','').replace('	','').rstrip(":")
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
            print(list2[i][0].replace(':', '') + '-' + time_temp + '|' +
                  list2[i][1],
                  file=out_file)
            if list2[i][0][:1] == '2' and list2[i + 1][0][:1] == '0':
                tmp_date = tmp_date + datetime.timedelta(days=1)
                new_date = tmp_date.strftime('%Y%m%d')
                print("Date:%s" % new_date, file=out_file)

        else:
            end_time = list2[0][0][:5].replace(':', '')
            print(list2[i][0].replace(':', '') + '-' + end_time + '|' +
                  list2[i][1],
                  file=out_file)
out_file.close()
