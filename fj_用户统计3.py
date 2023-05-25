import csv
import time
from collections import defaultdict
start_time = time.time()
file_path = '/Users/hanxiong/temp/Contentviewlog_20230228.log'

# 创建一个字典用于存储每个月的用户记录数
user_counts_by_month = defaultdict(set)

with open(file_path, 'r',encoding='latin-1') as file:
    reader = csv.reader(file, delimiter='|')
    for row in reader:
        userid = row[0]
        timestamp = row[1]
        month = timestamp[:6]  # 提取时间戳的前6位表示月份
        user_counts_by_month[month].add(userid)

# 统计每个月的用户去重记录数
for month, user_set in user_counts_by_month.items():
    count = len(user_set)
    print(f"Month: {month}, Unique User Count: {count}")

end_time = time.time()
print(f"Total time: {end_time - start_time}")
