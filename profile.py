import redis2 as redis
import javaobj.v2 as javaobj

redis_cli = redis.Redis(host='172.25.121.211',
                        port=6377,
                        password='',
                        db=8,)

print ("start to export......")

txt= open('epggroupnum.txt', 'w')

for k in redis_cli.scan_iter("aaa_profile*"): 
    print(k.decode(),end=',',file=txt)
    data2 = redis_cli.get(k)
    res = javaobj.loads(data2)
    print(res.usergroupnmb,file=txt)
txt.close()
