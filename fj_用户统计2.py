from collections import defaultdict
import time
start_time = time.time()
file_path = '/Users/hanxiong/temp/Contentviewlog_20230228.log'

user_counts_by_month = defaultdict(set)

with open(file_path, 'r') as file:
    for line in file:
        line_parts = line.split('|')
        if len(line_parts) >= 2:
            userid, timestamp = line_parts[0], line_parts[1]
            month = timestamp[:6] 
            user_counts_by_month[month].add(userid)


for month, user_set in user_counts_by_month.items():
    count = len(user_set)
    print(f"Month: {month}, Unique User Count: {count}")
end_time = time.time()
print(f"Total time: {end_time - start_time} seconds")

