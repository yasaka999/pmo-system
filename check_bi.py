import re
import sys
from datetime import datetime

def total_seconds(td):
    return td.days * 24 * 3600 + td.seconds

prev_ts = 0
logfile = sys.argv[1]
with open(logfile, 'r') as file:
#with open('test.log', 'r') as file:
    for line in file:
        dt_field = ""
        line = line.strip()

        # Match the timestamp in the format yyyyMMdd-HHmmss
        match1 = re.match(r'^\d{8}-\d{6}', line)
        # Match the timestamp in the format yy/MM/dd HH:mm:ss
        match2 = re.match(r'^\d{2}/\d{2}/\d{2}\ \d{2}:\d{2}:\d{2}', line)
        match3 = re.match(r'^\d{4}-\d{2}-\d{2}\ \d{2}:\d{2}:\d{2}', line)

        if match1:
            dt_field = datetime.strptime(match1.group(), '%Y%m%d-%H%M%S')
        elif match2:
            dt_field = datetime.strptime(match2.group(), '%y/%m/%d %H:%M:%S')
        elif match3:
            dt_field = datetime.strptime(match3.group(), '%Y-%m-%d %H:%M:%S')
        if not dt_field:
            continue

        epoch = datetime(1970, 1, 1)
        curr_ts = int(total_seconds(dt_field - epoch))
#        print(dt_field)
#        print("prev=", prev_ts)
#        print("curr=", curr_ts)

        if prev_ts != 0 and curr_ts - prev_ts > 200:
            print(line)

        prev_ts = curr_ts