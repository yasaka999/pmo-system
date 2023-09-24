
# -*- coding:utf-8 -*-
from datetime import datetime,timedelta

records = []
# 打开文件
with open('../files/test.log', 'r') as file:
    # 逐行读取
    for line in file:
        # 如果行中包含"recived:"，则打印该行
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


                # 创建一个字典来存储这些值
                record = {
                    'result_time':result_time,
                    'recived':recived,
                    'error':error,
                    'discard':discard,
                    'fix':fix,
                    'queueDiscard':queueDiscard,
                    'handled':handled,
                    'sent':sent
                }

                # 将字典添加到列表中
                records.append(record)

# 打印列表
for record in records:
     print(record)

index = {item['result_time']: item['recived'] for item in records}

target_result_times = ['2023-07-26_00:59:54', '2023-07-26_19:59:55']

for result_time in target_result_times:
    recived_value = index.get(result_time)
    if recived_value is not None:
        print(f"recived value for result_time {result_time}: {recived_value}")
    else:
        print(f"No matching record found for result_time {result_time}")

time_str='2023-08-01_19:59:54'
y_time = (datetime.strptime(time_str, "%Y-%m-%d_%H:%M:%S")- timedelta(days=1)).strftime('%Y-%m-%d_%H:%M:%S')
print (y_time)
