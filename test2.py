import pymysql
import yaml
import datetime


def DupSchedule(schannel,dchannel,airdate):
        db = pymysql.connect(host=config['MYSQL']['host'],
                     user=config['MYSQL']['user'],
                     password=config['MYSQL']['password'],
                     database=config['MYSQL']['database'])
        cursor = db.cursor()
        sql = "SELECT s.play_date,cast(s.play_start_date as char) ,cast(s.play_end_date as char),s.schedule_name \
                from cms_pre_schedule_base s, cms_pre_channel c where c.out_source_id=s.channel_out_source_id \
                        and c.is_cp_delete=0 and c.channel_name= %s and s.play_date>=%s order by s.play_start_date"
        cursor.execute(sql,(schannel,airdate))
        data = cursor.fetchall()
        cursor.close()
        db.close()
        print ('Channels:%s' % dchannel)
        print ('Date:'+str(airdate))
        for i in data:
                if i[0]!=airdate:
                        print ('Date:'+str(i[0]))
                        airdate = i[0]
                        print (i[1][11:16].replace(':','')+'-'+i[2][11:16].replace(':','')+'|'+i[3])
                else:
                        print (i[1][11:16].replace(':','')+'-'+i[2][11:16].replace(':','')+'|'+i[3])
with open("../files/channel_config.yml", "r") as f:
    config = yaml.safe_load(f)
#print (config)
#channelname =config['CHANNELS'][0].keys()

#airdate=(datetime.datetime.today()+datetime.timedelta(days=1)).strftime("%Y%m%d")
airdate = '20221209'
for i in range(len(config['CHANNELS'])):
        for schannel,dchannel in config['CHANNELS'][i].items():
                DupSchedule(schannel,dchannel,airdate)