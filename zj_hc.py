'''
通过源文件，按一定规则，转换生成目标文件
'''

#!/usr/bin/python
# -*- coding:utf8 -*-
import datetime
today = datetime.date.today()
yesterday = datetime.date.today() + datetime.timedelta(-1)
#源文件名
s_file='huodong_'+datetime.datetime.strftime(yesterday, '%Y%m%d')+'.txt'
print (s_file)
#目标文件名
d_file='833_Behaviorlog_'+datetime.datetime.strftime(yesterday, '%Y%m%d')+'.txt'
print (d_file)
#读映射表生成字典
with open('JZYX_CONTENT_INFO_DATA.txt','r') as f:
	map1={}
	for line in f.readlines():
		line=line.strip('\n')
		b=line.split('	')
		for i in range(len(b)): 
			map1[b[i]]=b[1:]

txt= open(d_file, 'w')
#逐行读文件成列表，按规则转换
with open(s_file,'r') as sfile:
    for l in sfile.readlines():
        l=l.strip('\n')
        s=l.split(' ')
#根据帐号转换区域码
        s3=s[0][0:3]
        s4=s[0][0:4]
        if s4 in ['1570','0570','1702'] or s3=='570' :
        	areacode='83308'
        elif s4 in ['1571','0571','1712'] or s3=='571' :
        	areacode='83301'
        elif s4 in ['1572','0572','1722'] or s3=='572' :
        	areacode='83305'
        elif s4 in ['1573','0573','1732'] or s3=='573' :
        	areacode='83304'
        elif s4 in ['1574','0574','1742'] or s3=='574' :
        	areacode='83302'
        elif s4 in ['1575','0575','1752'] or s3=='575' :
        	areacode='83306'
        elif s4 in ['1576','0576','1762'] or s3=='576' :
        	areacode='83310'
        elif s4 in ['1577','0577','1772'] or s3=='577' :
        	areacode='83303'
        elif s4 in ['1578','0578','1782'] or s3=='578' :
        	areacode='83311'
        elif s4 in ['1579','0579','1792'] or s3=='579' :
        	areacode='83307'
        elif s4 in ['1580','0580','1802'] or s3=='580' :
        	areacode='83309'
        else:
        	areacode='99999'
#        print(s[0],areacode)
#处理时间格式转换
        date=s[2]+' '+s[3]
        date1 = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
#        print(date1)
        date2 = datetime.datetime.strftime(date1, '%Y%m%d%H%M%S')
#        print(date2)
#从映射表中取其他字段数据
        userid=s[0]
        epgcode=s[1]
        contentid=map1.get(epgcode)[2]
        contentname=map1.get(epgcode)[3]
        behaviorpath=map1.get(epgcode)[4]
        productlist=map1.get(epgcode)[7]
        method=map1.get(epgcode)[5]
#python2
        print >>txt,'8|$|1|$|'+userid+'|$||$||$||$||$|833|$|'+areacode+'|$|'\
        	+date2+'|$||$|4|$||$|'+contentid+'|$|'+contentname+'|$||$|'+behaviorpath\
        	+'|$|1|$|'+productlist+'|$|'+method
#python3
#        print('8|$|1|$|'+userid+'|$||$||$||$||$|833|$|'+areacode+'|$|'\
#                +date2+'|$||$|4|$||$|'+contentid+'|$|'+contentname+'|$||$|'+behaviorpath\
#                +'|$|1|$|'+productlist+'|$|'+method,file=txt)
txt.close
