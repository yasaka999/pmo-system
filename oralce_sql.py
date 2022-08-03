import cx_Oracle,time,datetime
cx_Oracle.init_oracle_client(lib_dir="/Users/hanxiong/Downloads/instantclient_19_8")

def sql_object(sql,db_connect):
    cursor = db_connect.cursor()
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    row = cursor.fetchall()
    data = []
    for i in row:
        data.append(dict(zip(columns, i)))
    cursor.close()
    return data
    
conn = cx_Oracle.connect("wacos/nmBKsmp2015@172.25.116.5:1521/orcl")
cr = conn.cursor()
nCount=0
sql = "SELECT A.ProgramID programid, A.CODE Code,A.NAME Name,A.ALIAS OriginalName,\
    A.TITLE_SORT_NAME SortName,A.TITLE_SEARCH_NAME SearchName,substr(A.Director,0,47) Director,\
        substr(A.Kpeople,0,147) Kpeople,to_char(A.LICENSINGWINDOWSTART,'YYYYMMDDHH24MiSS') LicensingWindowStart, \
            to_char(A.LICENSINGWINDOWEND,'YYYYMMDDHH24MiSS') LicensingWindowEnd,A.SeriesFlag SeriesFlag,\
                A.LANGUAGE Language,A.DESCRIPTION Description,A.PRICE PriceTaxIn,A.SourceType SourceType,\
                    A.ReleaseYear ReleaseYear,C.Code VSPCode,A.CopyRight CopyRight, A.ContentProvider ContentProvider,\
                        ceil(to_number(nvl(A.Duration,'0'))/1500) Duration,substr(A.ScriptWriter,0,47) ScriptWriter,\
                            substr(A.Compere,0,47) Compere,substr(A.Guest,0,47) Guest,substr(A.Reporter,0,47) Reporter,\
                                A.OPIncharge OPIncharge,B.Status Status, A.Genre Genre,A.LinkURL LinkURL,A.overduetime OverdueTime,\
                                    A.NewPrice NewPrice,A.Rating Rating,A.ORGAIRDATE ORGAIRDATE from program A, domainobjects B,\
                                         vsp C , program_bak d where A.ProgramID=B.ObjID and A.VSPID=C.VSPID and B.ObjType='1' \
                                              and A.seriesflag='0' and B.DomainID=8 and A.status='4' and  d.programcode = a.code2\
                                                  and rownum<25"

#sql=sqlbase+' '+sqlwhere
#print "GetData SQL: ",sql
cr.execute(sql)
rs = cr.fetchone()
print(rs)
program_columns = [column[0] for column in cr.description]
#program_data = []
print("Begin process exp programs")
while rs:
    print(rs[0])
    program_object = [dict(zip(program_columns, rs))]
#    print(program_object)
    
    sqlmovie= "select contentname,a.code moviecode,fileurl,b.code programcode,c.MediaSpec MediaSpec,type,SCREEN_FORMAT from mediacontent a,program b ,contentdef c where a.ContentDefID=c.ContentDefID and a.status='4'  and mediacontentid in ( \
        select  mediacontentid from programmediacontent where objtype= '1' and objid=%d) and b.programid=%d" % (rs[0],rs[0])
    movie_object = sql_object(sqlmovie,conn)
#    print(movie_object)

    sqlpicture="select a.code programcode,c.code picturecode,c.picture picture,decode(b.picturetypeid,400,0,401,1,402,2,403,3,404,4,405,5,406,6,407,7,0) picturetypeid,b.sequence sequence from program a,picturemap b,metapicture c \
              where b.objtype='4' and c.status='1'  and a.programid=b.objid and b.metapictureid=c.metapictureid and a.programid=%d" % (rs[0])
    picture_object = sql_object(sqlpicture,conn)
#    print(picture_object)

    nCount = nCount + 1
    now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
    if (nCount%10==0):
       print(now+" : Processed "+str(nCount)+" programs")
 #   dealprogram(rs,rsmovie,rspicture)
    rs=cr.fetchone()
now = time.strftime('%H%M%S') + str(datetime.datetime.now().microsecond)
print(now+" : Processed "+str(nCount)+" programs")
print("Finished process exp programs")
cr.close()
conn.close()