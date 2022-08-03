# 中文冒号转换为英文冒号
# 提取：所在行数据
# 去空格,处理0xa0转换
# 按每日分隔，添加date
# 取前4位生成列表
# 需要增加前面的时间格式判断aa:bb的形式：a:bb前面加0；
import datetime

start_date = '20221025'
tmp_date = datetime.datetime.strptime(start_date, '%Y%m%d')
new_date = tmp_date.strftime('%Y%m%d')
s_file = "../files/nmtest3.txt"
output_txt = open("../files/output_schedule.txt", "w")
print("Date:%s" % new_date, file=output_txt)
with open(s_file, encoding="utf8") as f:
    list1 = f.read().split("\n")
    list2 = []
    for i in range(len(list1)):
        # 中文冒号转换为英文冒号
        list1[i] = list1[i].replace("：", ":")
        if ":" in list1[i]:
            list1[i] = list1[i].replace(chr(0xa0), '').replace(' ', '')
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
                  file=output_txt)
            if list2[i][0][:1] == '2' and list2[i + 1][0][:1] == '0':
                tmp_date = tmp_date + datetime.timedelta(days=1)
                new_date = tmp_date.strftime('%Y%m%d')
                print("Date:%s" % new_date, file=output_txt)

        else:
            print(list2[i][0].replace(':', '') + '-' + '0000' + '|' +
                  list2[i][1],
                  file=output_txt)
output_txt.close()
