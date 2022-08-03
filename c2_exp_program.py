# xml生成模块:需要三种类型的数据，分别是：program,movie,picture
# 参数：类型，字典
def object_deal(type, dic):
    object = ET.SubElement(objects, "Object")
    object.set("Action", "REGIST")
    object.set("Code", dic['CODE'])
    object.set("ElementType", "Program")
    object.set("ID", dic['CODE'])
    for key, value in dic.items():
        if key not in ('CODE', 'SERIESID') and value is not None:
            key = object_name_format(key, object_map)
            property = ET.SubElement(object, "Property")
            property.set("Name", key)
            property.text = str(value)


# object name格式化模块
def object_name_format(name, map_dict):
    for key in map_dict:
        if key.lower() == name.lower():
            name = key
            break
    return name

object_map = ['Name','Code','OriginalName','SortName','SearchName','LicensingWindowStart','LicensingWindowEnd',\
    'Kpeople','Director','Description','Price','ReleaseYear','SeriesType','CopyRight','ContentProvider','VSPCode',\
        'VolumCount','ScriptWriter','Compere','Guest','Reporter','OPIncharge','ORGAIRDATE','Status','Genre',\
            'SeriesType','CPActiveTime','OverdueTime']
# sql查询并转换成字典模块
def sql_deal(sql):  
    nCount=0
  print "Database Info:",database,databaseuser,databasepassword
#  db = cx_Oracle.connect('wacos','oss','10.50.13.101:1521/orcl')
  print "Connecting Database"
  db=cx_Oracle.connect(databaseuser,databasepassword,database)
  print "Connect Database Success"
  cr=db.cursor()

# sql='select programid,name,code,to_char(licensingwindowstart,\'yyyymmddhh24miss\'),to_char(licensingwindowend,\'yyyymmddhh24miss\'),kpeople,director from program where rownum<20'
  sql=sqlbase+' '+sqlwhere
  print "GetData SQL: ",sql

  cr.execute(sql)
  rs=cr.fetchone()
  print "Begin process exp programs"
  while rs:
    crmovie=db.cursor()
    print (rs[0])
#    sqlmovie= 'select contentname,a.code moviecode,fileurl,b.code programcode,c.MediaSpec MediaSpec,type,SCREEN_FORMAT from mediacontent a,program b ,contentdef c where a.ContentDefID=c.ContentDefID and a.status=''4''  and mediacontentid in (select  mediacontentid from programmediacontent where objtype=''1'' and objid='+str(rs[0])+') and b.programid='+str(rs[0])
    sqlmovie= "select contentname,a.code moviecode,fileurl,b.code programcode,c.MediaSpec MediaSpec,type,SCREEN_FORMAT from mediacontent a,program b ,contentdef c where a.ContentDefID=c.ContentDefID and a.status='4'  and mediacontentid in ( \
        select  mediacontentid from programmediacontent where objtype= '1' and objid=%d) and b.programid=%d" % (rs[0],rs[0])
    crmovie.execute(sqlmovie)
    rsmovie=crmovie.fetchall()
    crmovie.close()

    crpicture=db.cursor()
    sqlpicture='select a.code programcode,c.code picturecode,c.picture picture,decode(b.picturetypeid,400,0,401,1,402,2,403,3,404,4,405,5,406,6,407,7,0) picturetypeid,b.sequence sequence from program a,picturemap b,metapicture c \
              where b.objtype=''4'' and c.status=''1''  and a.programid=b.objid and b.metapictureid=c.metapictureid and a.programid='+str(rs[0])

    crpicture.execute(sqlpicture)
    rspicture=crpicture.fetchall()
    crpicture.close()
    nCount = nCount + 1
    now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
    if (nCount%10==0):
       print now+" : Processed "+str(nCount)+" programs"
    dealprogram(rs,rsmovie,rspicture)
    rs=cr.fetchone()
  now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
  print now+" : Processed "+str(nCount)+" programs"
  print "Finished process exp programs"
  cr.close()
  db.close()
