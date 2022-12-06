import subprocess
ftpurl = "ftp://wacos:wacos@172.25.135.98:21//home/PMSData/response1/masvc/fjbi_15530830_12358908_Schedule_REGIST_20221203194412663-4_new_res_20221203195010.xml"
#cmd = ftp://wacos:wacos@172.25.135.98:21//home/PMSData/response1/masvc/fjbi_15530830_12358908_Schedule_REGIST_20221203194412663-4_new_res_20221203195010.xml
#subprocess.call('wget %s' %ftpurl,shell=True)
a = ftpurl.split("/")[-1]
print (a)