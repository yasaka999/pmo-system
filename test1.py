# -*- coding: UTF-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
result_file = open("result.txt", "w")
with open("../files/hlj_channel.txt", encoding="utf8") as f:
    channel = f.read().split("\n")
print (channel)
print ("----------------------------------------------------------------")

channel_list = ['CCTV-俄语频道节目单', 'CCTV-法语频道节目单', 'CCTV-西班牙语频道节目单', 'CCTV-阿拉伯语频道节目单', 'CCTV10节目单', 'CCTV10高清节目单', 'CCTV11节目单', 'CCTV12节目单', 'CCTV12高清节目单', 'CCTV13节目单', 'CCTV14节目单', 'CCTV14高清节目单', 'CCTV15节目单', 'CCTV17节目单', 'CCTV17高清节目单', 'CCTV1节目单', 'CCTV1高清节目单', 'CCTV2节目单', 'CCTV2高清节目单', 'CCTV3节目单', 'CCTV3高清节目单', 'CCTV4节目单', 'CCTV5节目单', 'CCTV5高清节目单', 'CCTV6节目单', 'CCTV6高清节目单', 'CCTV7节目单', 'CCTV7高清节目单', 'CCTV8节目单', 'CCTV8高清节目单', 'CCTV9节目单', 'CCTV9高清节目单', 'CCTVnews-英语新闻频道节目单', 'CETV1节目单', 'CETV4空中课堂节目单', '七彩戏剧节目单', '上海东方卫视节目单', '世界地理节目单', '东南卫视高清节目单', '东方卫视高清节目单', '东方财经节目单', '中国气象节目单', '乐游节目单', '云南卫视节目单', '优漫卡通节目单', '兵团卫视节目单', '内蒙古卫视节目单', '农垦北大荒节目单', '动漫秀场节目单', '劲爆体育节目单', '北京卫视节目单', '北京卫视高清节目单', '卡酷动画节目单', '吉林卫视节目单', '吉林卫视高清节目单', '四川卫视节目单', '四川卫视高清节目单', '国学频道节目单', '大庆教育频道节目单', '大湾区卫视节目单', '天津卫视节目单', '天津卫视高清节目单', '宁夏卫视节目单', '安徽卫视节目单', '安徽卫视高清节目单', '家庭理财节目单', '家政节目单', '山东卫视节目单', '山东卫视高清节目单', '山西卫视节目单', '广东卫视节目单', '广东卫视高清节目单', '广东嘉佳卡通节目单', '广西卫视节目单', '延边卫视节目单', '快乐宠物节目单', '收藏天下节目单', '新疆卫视节目单', '极速汽车节目单', '江苏卫视节目单', '江苏卫视高清节目单', '江西卫视节目单', '江西卫视高清节目单', '河北卫视节目单', '河北卫视高清节目单', '河南卫视节目单', '河南卫视高清节目单', '法治天地节目单', '浙江卫视节目单', '浙江卫视高清节目单', '海南卫视节目单', '深圳卫视节目单', '深圳卫视高清节目单', '游戏风云节目单', '湖北卫视节目单', '湖北卫视高清节目单', '湖南卫视节目单', '湖南卫视高清节目单', '湖南金鹰卡通卫视节目单', '甘肃卫视节目单', '生活时尚节目单', '电子体育节目单', '百姓健康节目单', '福建东南卫视节目单', '老故事节目单', '西藏卫视节目单', '证券资讯节目单', '财富天下节目单', '贵州卫视节目单', '贵州卫视高清节目单', '辽宁卫视节目单', '辽宁卫视高清节目单', '都市剧场节目单', '重庆卫视节目单', '重庆卫视高清节目单', '金色频道节目单', '陕西卫视节目单', '青海卫视节目单', '靓妆节目单', '魅力音乐节目单', '黑龙江农业科教节目单', '黑龙江卫视节目单', '黑龙江卫视高清节目单', '黑龙江少儿节目单', '黑龙江影视节目单', '黑龙江文体节目单', '黑龙江新闻法治节目单', '黑龙江新闻法治高清节目单', '黑龙江都市节目单']
channel_miss=[]
for channel_name  in channel:
    if channel_name + "节目单" not in channel_list:
        channel_miss.append(channel_name)
if channel_miss:
    print ("共有%s个频道节目单缺失: " % len(channel_miss),file=result_file)
    print (",".join(channel_miss),file=result_file)
else:
    print ("节目单无异常",file=result_file)
result_file.close()

# 第三方 SMTP 服务
# 发送邮件相关参数
smtpserver = 'smtp.163.com'         # 发件服务器
port = 0                            # 端口
sender = '13666633777@163.com'         # 发件人邮箱
psw = 'XSBTZQCZBGWQVYYG'                            # 发件人密码
receiver = "hans.han@utstarcom.cn"       # 接收人
# 邮件标题
subjext = '每日节目单检查'
# 获取附件信息
#with open('result.html', "rb") as f:
body = "节目单检查结果"
message = MIMEMultipart()
# 发送地址
message['from'] = sender
message['to'] = receiver
message['subject'] = subjext
# 正文
body = MIMEText((open("result.txt", "r")).read(), 'html', 'utf-8')
message.attach(body)
# 同一目录下的文件
#att = MIMEText(open("result.txt", 'rb').read(), 'base64', 'utf-8') 
#att["Content-Type"] = 'application/octet-stream'
# filename附件名称
#filename = 'attachment; filename='+str(result_file)
#att["Content-Disposition"] = filename
#message.attach(att)
smtp = smtplib.SMTP()
smtp.connect(smtpserver)    # 链接服务器
smtp.login(sender, psw)     # 登录
smtp.sendmail(sender, receiver, message.as_string())  # 发送
smtp.quit()             # 关闭