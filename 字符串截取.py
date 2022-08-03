import json

a = 'GET /?opt=put&user_id=itv047281464587&data={"refer_page_name":"电信八屏","seqid":"122","refer_type":"1","refer_pos_id":"","area_code":"0472","stb_type":"E900-S","currentplaytime":"1658651353","action_type":"tv_playing","stb_id":"001004990104900018232C18757A0B03","refer_parent_id":"","path":"电信八屏\/播放页","stb_ip":"10.200.236.243","user_id":"itv047281464587","user_group_id":"002A019999","refer_pos_name":"遥控器切台键进入播放页","mediacode":"04710001000000050000000000000652","epg_group_id":"01","definition":"2","sys_id":"t","terminal_type":"329","stb_mac":"2C:18:75:7A:0B:03","refer_page_id":"page08.java","refer_mediacode":"","county":"2A","tryview":"0","start_time":"1658641752","bitrate":"0","log_time":"1658651353"} HTTP/1.1'
ind1 = a.index("{")
ind2 = a.index("}")
print(ind1)
print(ind2)
print(a[ind1 : ind2 + 1])
print(
    json.dumps(
        json.loads(a[ind1 : ind2 + 1]), indent=2, sort_keys=False, ensure_ascii=False
    )
)
