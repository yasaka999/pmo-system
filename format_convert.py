"""
通过源文件，按一定规则，转换生成目标文件
"""

#!/usr/bin/python
# -*- coding:utf8 -*-
import datetime

today = datetime.date.today()
yesterday = datetime.date.today() + datetime.timedelta(-1)
# 源文件名
s_file = "a.txt"
print(s_file)
# 目标文件名
d_file = "7day_" + datetime.datetime.strftime(yesterday, "%Y%m%d") + ".txt"
print(d_file)


txt = open(d_file, "w")
# 逐行读文件成列表，按规则转换
with open(s_file, "r") as sfile:
    for l in sfile.readlines():
        l = l.strip("\n")
        s = l.split("|")

        # python2
        print >> txt, s[0] + "," + s[3] + "," + s[5]
# python3
#        print('8|$|1|$|'+userid+'|$||$||$||$||$|833|$|'+areacode+'|$|'\
#                +date2+'|$||$|4|$||$|'+contentid+'|$|'+contentname+'|$||$|'+behaviorpath\
#                +'|$|1|$|'+productlist+'|$|'+method,file=txt)
txt.close
