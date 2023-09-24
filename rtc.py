# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import glob

yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  # 获取昨天的日期字符串，格式为"YYYY-MM-DD"
file_pattern = "rtc.log.%s-*" % yesterday 
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
#for record in records:
#    print(record)
index = {}
for item in records:
    index[item['result_time']] = item['recived']

target_result_times = []
with open("rtc.log", 'r') as f2:
    lines = f2.readlines()
    reversed_lines = reversed(lines)
    count = 0

    for line in reversed_lines:
        if 'recived:' in line:
            target_result_times.append(line.split()[5])
            count += 1

        if count == 10:
            break

print (target_result_times)
#target_result_times = ['2023-07-26_00:59:54', '2023-07-27_19:59:55']

for result_time in target_result_times:
    result_time = (datetime.strptime(result_time, "%Y-%m-%d_%H:%M:%S")- timedelta(days=1)).strftime('%Y-%m-%d_%H:%M:%S')
    recived_value = index.get(result_time)
    if recived_value is not None:
        print("recived value for result_time %s: %s") %(result_time, recived_value)
    else:
        print("No matching record found for result_time %s" %(result_time))


