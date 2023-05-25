from collections import defaultdict
import time
import glob
import os
from multiprocessing import Pool

def process_file(file_path):
    user_counts_by_month = defaultdict(set)
    with open(file_path, 'r') as file:
        file_name = os.path.basename(file_path)
        print("Processing file: %s" % file_path)

        for line in file:
            line_parts = line.split('|')
            if len(line_parts) >= 2:
                userid, timestamp = line_parts[0], line_parts[1]
                if userid:
                    month = timestamp[:6]
                    user_counts_by_month[month].add(userid)
    return user_counts_by_month

def write_to_file(month, user_set):
    filename = "{0}_users.txt".format(month)
    with open(filename, 'w') as file:
        for user in user_set:
            file.write(user + '\n')

start_time = time.time()
file_pattern = './*iew*'

pool = Pool(processes=6)
results = pool.map(process_file, glob.glob(file_pattern))
pool.close()
pool.join()

user_counts_by_month = defaultdict(set)
for result in results:
    for month, user_set in result.iteritems():
        user_counts_by_month[month] |= user_set

for month, user_set in user_counts_by_month.iteritems():
    count = len(user_set)
    print("Month: %s, Unique User Count: %s" % (month, count))
    write_to_file(month, user_set)

end_time = time.time()
print("Total time: %s seconds" % (end_time - start_time))