import re
a=[{"createtime":"20210806120548","mark":"13","mc":"00000001000000050000000000000602","mode":"1","name":"CCTV-13高清","pic":"无","st":"1","type":"tv","userid":"01-01016790359-01"},{"createtime":"20210806120611","mark":"5","mc":"01010001000000050000000000000371","mode":"1","name":"CCTV-5高清","pic":"无","st":"2","type":"tv","userid":"01-01016790359-01"},{"createtime":"20210806120648","mark":"18","mc":"00000001000000050000000000000153","mode":"1","name":"CCTV-5+","pic":"无","st":"2","type":"tv","userid":"01-01016790359-01"}]
p1 = re.compile(r'[{](.*?)[}]', re.S) 
#print (a)
#arr = re.findall(p1,a[0])
#print (arr)
for i in a:
        print (i)