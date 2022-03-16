"""
序列化：把对象变成字符串或字节串
反序列化：把字符串或字节串还原成对象
json: object ---> str / str ---> object ---> 跨语言
pickle: object ---> bytes / bytes ---> object ---> Python
"""
import json
import pickle
import redis
import javaobj.v2 as javaobj


# 数据库的连接
redis_cli = redis.Redis(host='172.25.130.70',
                        port=6379,
                        password='',
                        db=12,)
# 判断数据库是否连接成功
print(redis_cli.ping())
print(redis_cli.ttl('username'))
print(redis_cli.get('username'))
#redis_cli.expire('username', 1800)


# 反序列化，将字节串转化为对象显示：pickle.loads


for k in redis_cli.scan_iter("aaa_profile*",30): 
    print(k.decode())
    data2 = redis_cli.get(k)
    res = javaobj.loads(data2)
    print(res.usergroupnmb)

#print(type(res))

#print(res.dump())

