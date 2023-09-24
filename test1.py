records = [
    {'result_time': '2023-07-26_23:59:54', 'recived': 352, 'error': 0, 'discard': 0, 'fix': 200, 'queueDiscard': 0, 'handled': 352, 'sent': 352},
    {'result_time': '2023-07-26_23:59:55', 'recived': 408, 'error': 0, 'discard': 0, 'fix': 250, 'queueDiscard': 0, 'handled': 408, 'sent': 408},
    {'result_time': '2023-07-26_23:59:56', 'recived': 371, 'error': 0, 'discard': 0, 'fix': 226, 'queueDiscard': 0, 'handled': 371, 'sent': 371},
    {'result_time': '2023-07-26_23:59:57', 'recived': 378, 'error': 0, 'discard': 0, 'fix': 224, 'queueDiscard': 0, 'handled': 378, 'sent': 378},
    # Add more records here...
]

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
        'recived': sum(values['recived']) / len(values['recived']),
        'sent': sum(values['sent']) / len(values['sent']),
    })

# 输出每分钟的记录
print(result_list)
