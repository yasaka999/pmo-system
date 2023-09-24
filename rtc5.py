# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import glob

yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  # 获取昨天的日期字符串，格式为"YYYY-MM-DD"
file_pattern = "/opt/spark/rtc/logs/rtc.log.%s-*" % yesterday 
files = glob.glob(file_pattern)

records = []

for file in files:
    with open(file, 'r') as f:
        for line in f:
            if 'recived:' in line:
                parts = line.split()

                # 提取各项值
                result_time = parts[5]
                recived = int(parts[7])
                error = int(parts[9])
                discard = int(parts[11])
                fix = int(parts[13])
                queueDiscard = int(parts[15])
                handled = int(parts[17])
                sent = int(parts[19])

                record = {
                    'filename': file,
                    'result_time': result_time,
                    'recived': recived,
                    'error': error,
                    'discard': discard,
                    'fix': fix,
                    'queueDiscard': queueDiscard,
                    'handled': handled,
                    'sent': sent
                }

                records.append(record)

# 打印列表
# for record in records:
#     print(record)

index = {}
for item in records:
    index[item['result_time']] = item['recived']

target_result_times = []
target_records = []

with open("/opt/spark/rtc/logs/rtc.log", 'r') as f2:
    lines = f2.readlines()
    reversed_lines = reversed(lines)
    count = 0

    for line in reversed_lines:
        if 'recived:' in line:
            parts = line.split()
            result_time = parts[5]
            recived = int(parts[7])

            target_result_times.append(result_time)
            target_records.append({'result_time': result_time, 'recived': recived})

            count += 1

        if count == 10:
            break

#print(target_result_times)


# 计算百分比差并打印告警信息
percent_diff_list = []  # 用于存储所有的百分比差

for record in target_records:
    result_time = record['result_time']
    result_time = (datetime.strptime(result_time, "%Y-%m-%d_%H:%M:%S")- timedelta(days=1)).strftime('%Y-%m-%d_%H:%M:%S')
    recived_value = index.get(result_time)
    if recived_value is not None:
        percent_diff = (record['recived'] - float(recived_value)) / recived_value * 100
        print("recived value from rtc log %s: %s; %s: %s; diff: %d; percent: %.2f" % (result_time, recived_value, record['result_time'], record['recived'], in
t(record['recived'] - recived_value), percent_diff))
        percent_diff_list.append(percent_diff)

        # 不再判断单个百分比差是否大于20，而是将所有的百分比差都记录下来后再进行判断

    else:
        print("No matching record found for result_time %s" % (result_time))

# 打印告警信息
#if all(diff > 20 for diff in percent_diff_list):
if len([diff for diff in percent_diff_list if abs(diff) > 20]) >= 10:
    print("Warning: All 'recived' values in the last 10 records have a percentage difference greater than 20.")