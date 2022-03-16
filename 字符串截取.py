import json
a='GET /?opt=put&user_id=047104476604@tv&data={"refer_type":"6","mediacode":"00000001000000050000000000000472","epg_group_id":"047101","seqid":117,"definition":2,"area_code":"0471","refer_pos_id":"","sys_id":"u","stb_type":"EC6109U_nmglt","terminal_type":"231","currentplaytime":"1634139703","stb_mac":"C4B8B4C18533","refer_page_id":"TuiJian.java","action_type":"tv_playing","county":"1A","stb_id":"00000415000890100000C4B8B4C18533","tryview":"0","mediaduration":"","path":"\/直播播放","start_time":"1634131603","bitrate":"","stb_ip":"172.163.220.31","user_id":"047104476604@tv","user_group_id":"1A01","log_time":1634139703} HTTP/1.1'
ind1 = a.index('{')
ind2 = a.index('}')
print (ind1)
print (ind2)
print (a[ind1:ind2+1])
print (json.dumps(json.loads(a[ind1:ind2+1]),indent=2,sort_keys=False,ensure_ascii=False))
