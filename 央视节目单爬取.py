import requests
import json
import time
import datetime
channel = ('cctv1', 'cctv2','cctv4','cctv7','cctv12','cctv13','cctv17')
def get_schedule(channelname,day):
    url = "https://api.cntv.cn/epg/getEpgInfoByChannelNew?c=%s&serviceId=tvcctv&d=%s&t=jsonp&cb=shanxi" %(channelname,day)
    content = requests.get(url).text[7:-2]
    dictinfo = json.loads(content)
#print (content)
    schedule = dictinfo['data'][channelname]['list']
#    print (dictinfo['data'][channelname]['list'])
    print ("---------------------------------")
    print (channelname+"   "+day+"节目单")
    print ("---------------------------------")
    for i in schedule:
        print (i['title'],time.strftime('%H:%M:%S', time.localtime(i['startTime'])),time.strftime('%H:%M:%S', time.localtime(i['endTime'])),sep='|')

if __name__ == '__main__':
    day = datetime.datetime.now().strftime('%Y%m%d')
    for i in channel:
        get_schedule(i,day)