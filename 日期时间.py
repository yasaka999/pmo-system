import datetime
start_date='20221031'
tmp_date=datetime.datetime.strptime(start_date,'%Y%m%d')
# add 1 day
tmp_date=tmp_date+datetime.timedelta(days=1)
print(tmp_date.strftime('%Y%m%d'))