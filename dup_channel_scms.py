# -*- coding: utf-8 -*-
import pymysql
import yaml
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def DupSchedule(schannel, dchannel, airdate):
    db = pymysql.connect(host=config['MYSQL']['host'],
                         user=config['MYSQL']['user'],
                         passwd=config['MYSQL']['password'],
                         db=config['MYSQL']['database'],
                         charset="utf8")
    cursor = db.cursor()
    sql = "SELECT s.play_date, cast(s.play_start_date as char), cast(s.play_end_date as char), s.schedule_name \
            FROM cms_pre_schedule_base s, cms_pre_channel c WHERE c.out_source_id=s.channel_out_source_id \
                    AND c.is_cp_delete=0 AND c.channel_name=%s AND s.play_date>=%s ORDER BY s.play_start_date"
    cursor.execute(sql, (schannel, airdate))
    data = cursor.fetchall()
    cursor.close()
    db.close()

    with open(config['OUTPUT'], "w+") as f:
        f.write('Channel:%s\n' % dchannel)
        f.write('Date:%s\n' % str(airdate))

        for i in data:
            if i[0] != airdate:
                f.write('Date:%s\n' % str(i[0]))
                airdate = i[0]
                f.write('%s-%s|%s\n' % (i[1][11:16].replace(':', ''), i[2][11:16].replace(':', ''), i[3]))
            else:
                f.write('%s-%s|%s\n' % (i[1][11:16].replace(':', ''), i[2][11:16].replace(':', ''), i[3]))


with open("channel_config.yml", "r") as f:
    config = yaml.safe_load(f)
#print (config)
delay=config['HISTORY']
airdate = (datetime.datetime.now()- datetime.timedelta(days=delay)).strftime("%Y%m%d")

for i in range(len(config['CHANNELS'])):
    for schannel, dchannel in config['CHANNELS'][i].items():
        DupSchedule(schannel, dchannel, airdate)
okfile = open(config['OUTPUT']+".ok","w")
okfile.close()