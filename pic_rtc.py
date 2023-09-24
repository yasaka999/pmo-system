from matplotlib.legend_handler import HandlerLine2D
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

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
#for record in records:
#     print(record)


# 创建一个字典来存储每分钟的记录
minute_records = {}

# 遍历每秒的记录，将它们汇总到每分钟的记录中
for record in records:
    result_time = record['result_time']
    # 提取时间戳中的时分部分，忽略秒部分
    minute = result_time.split('_')[1][:5]

    # 将当前记录合并到每分钟的记录中
    if minute in minute_records:
        minute_records[minute]['recived'].append(record['recived'])
        minute_records[minute]['sent'].append(record['sent'])
    else:
        minute_records[minute] = {
            'recived': [record['recived']],
            'sent': [record['sent']],
        }

# 计算每分钟的平均值，并构造结果列表
result_list = []
for minute, values in minute_records.items():
    result_list.append({
        'result_time': minute,
        'recived': sum(values['recived']),
        'sent': sum(values['sent']) / len(values['sent']),
    })

# 提取时间和各项值的列表
result_times = [record['result_time'] for record in result_list]
received_values = [record['recived'] for record in result_list]
#error_values = [record['error'] for record in records]
#discard_values = [record['discard'] for record in records]
#fix_values = [record['fix'] for record in records]
#queueDiscard_values = [record['queueDiscard'] for record in records]
#handled_values = [record['handled'] for record in records]
#sent_values = [record['sent'] for record in records]

# 转换时间字符串为日期时间类型
#result_times = [datetime.strptime(time_str, "%Y-%m-%d_%H:%M:%S") for time_str in result_times]

# 创建一个DataFrame对象
#data = pd.DataFrame({'Time': result_times, 'Received': received_values, 'Error': error_values, 'Discard': discard_values,'Fix': fix_values, 'queueDiscard':queueDiscard_values, 'handled': handled_values, 'sent': sent_values })
data = pd.DataFrame({'Time': result_times, 'Received': received_values})

# 设置时间列为索引
data.set_index('Time', inplace=True)

# 绘制曲线图
data.plot()

# 添加标题和标签
plt.title('rtc request')
plt.xlabel('Time')
plt.ylabel('Value')


# 显示图形
plt.show()

