import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir="/Users/hanxiong/Downloads/instantclient_19_8")
rs= [3968715,2346]
conn = cx_Oracle.connect("wacos/nmBKsmp2015@172.25.116.5:1521/orcl")
cursor = conn.cursor()
sql = "SELECT A.SeriesID seriesid,A.CODE code,A.NAME name,A.ALIAS OriginalName,A.TITLE_SORT_NAME SortName,A.TITLE_SEARCH_NAME SearchName,to_char(A.ValidThrough,'YYYYMMDDHH24MiSS') licensingwindowstart,\
    to_char(A.ValidUntil,'YYYYMMDDHH24MiSS') licensingwindowend,substr(A.Kpeople,0,150) kpeople,substr(A.Director,0,47) director ,A.DESCRIPTION Description,A.PRICE Price,A.ReleaseYear ReleaseYear,A.SeriesType SeriesType,\
        A.CopyRight CopyRight, A.ContentProvider ContentProvider,C.Code VSPCode,A.VolumCount volumncount, substr(A.ScriptWriter,0,47) db_ScriptWriter,substr(A.Compere,0,47) db_Compere,substr(A.Guest,0,47) db_Guest,\
            substr(A.Reporter,0,47) db_Reporter,A.OPIncharge db_OPIncharge,A.ORGAIRDATE db_ORGAIRDATE,B.Status db_Status,A.Genre db_Genre,A.SeriesType db_SeriesType,A.CPActiveTime db_cpactivetime,A.overduetime db_overduetime from \
                series A, domainobjects B, vsp C where B.DomainID=7 and A.VSPID=C.VSPID and B.ObjID=A.SeriesID and B.ObjType='35' and A.status='4' and a.seriesid=238764"
cursor.execute(sql)
row = cursor.fetchall()
print(row)
cursor.close()
conn.close()

