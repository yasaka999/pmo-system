from collections import defaultdict
import time
import glob

start_time = time.time()
file_pattern = '/tmp/*iew*.txt'

user_counts_by_month = defaultdict(set)
for file_path in glob.glob(file_pattern):

    with open(file_path, 'r') as file:
        for line in file:
            line_parts = line.split('|')
            if len(line_parts) >= 2:
                userid, timestamp = line_parts[0], line_parts[1]
                if userid:
                    month = timestamp[:6]
                    user_counts_by_month[month].add(userid)

for month, user_set in user_counts_by_month.items():
    count = len(user_set)
    print("Month: %s, Unique User Count: %s" % (month, count))

end_time = time.time()
print("Total time: %s seconds" % (end_time - start_time))
