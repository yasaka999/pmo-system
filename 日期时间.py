import datetime
start_date='2022-10-03'
tmp_date=datetime.datetime.now()
print (tmp_date)
# add 1 day
tmp_date=tmp_date+datetime.timedelta(days=1)
tomorrow=datetime.datetime.now()+ datetime.timedelta(days=1)
print(tmp_date.strftime('%Y%m%d'))
start_time = tomorrow.strftime('%Y-%m-%d') + " 00:00:00"
end_time = tomorrow.strftime('%Y-%m-%d')  + " 23:59:59"
print (start_time)
print (end_time)

print (datetime.datetime.now())
# print (datetime.datetime.now().strftime('%Y-%m-%d'))