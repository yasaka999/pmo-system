#coding=utf-8
import json

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


with open('/Users/hanxiong/downloads/YANHUA00000000011SEAST0001555862.json') as f: 
  data = json.load(f)
#data = byteify(data)  
#print data
episodes=data['episodes']
series = data['series']
code = data['series']['code']
title = data[u'series'][u'title']
nums = len(data[u'episodes'])
index = data[u'episodes'][1][u'index']
#a=str(title.decode('unicode_escape'))
new_data = json.dumps(episodes, sort_keys=True, indent=4, ensure_ascii=False)
data2 = json.loads(new_data)
#print   (type(episodes))
#print (episodes)
print (type(code))
print code
print nums
#print (type(a))
#print (new_data)
print index
#print (title+"("+code+")")
new_index=[]
for i in range(len(episodes)):
	new_index.append(int(data[u'episodes'][i][u'index']))
print new_index



#print json.dump(new_data,f)
