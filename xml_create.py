# create xml file
from xml.etree import ElementTree as ET
from xml.dom import minidom
import cx_Oracle, time, datetime

cx_Oracle.init_oracle_client(
    lib_dir="/Users/hanxiong/Downloads/instantclient_19_8")


# sql生成字典，匹配xml文件中的具体字段与对应值
def sql_object(sql, db_connect):
    cursor = db_connect.cursor()
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    row = cursor.fetchall()
    data = []
    for i in row:
        data.append(dict(zip(columns, i)))
    cursor.close()
    return data


# object name格式化模块：因为xml文件中的字段名称与数据库中的字段名称大小写不一致，需要进行转换
def object_name_format(name, map_dict):
    for new_name in map_dict:
        if new_name.lower() == name.lower():
            name = new_name
            break
    return name


# object中的字段对象生成
def object_deal(type, dic, del_columns):
    object = ET.SubElement(objects, "Object")
    object.set("Action", "REGIST")
    object.set("Code", dic['CODE'])
    object.set("ElementType", type)
    object.set("ID", dic['CODE'])
    for key, value in dic.items():
        if key not in del_columns and value is not None:
            key = object_name_format(key, object_map)
            property = ET.SubElement(object, "Property")
            property.set("Name", key)
            property.text = str(value)


# mapping生成模块，针对movie和picture
def mapping_deal(type, dic):
    if type == 'Movie':
        mapping = ET.SubElement(mappings, "Mapping")
        mapping.set("Action", "REGIST")
        mapping.set("ElementCode", dic['CODE'])
        mapping.set("ElementID", dic['CODE'])
        mapping.set("ElementType", type)
        mapping.set("ParentCode", dic['PROGRAMCODE'])
        mapping.set("ParentID", dic['PROGRAMCODE'])
        mapping.set("ParentType", 'Program')
    else:
        mapping = ET.SubElement(mappings, "Mapping")
        mapping.set("Action", "REGIST")
        mapping.set("ElementCode", dic['PROGRAMCODE'])
        mapping.set("ElementID", dic['PROGRAMCODE'])
        mapping.set("ElementType", 'Program')
        mapping.set("ParentCode", dic['CODE'])
        mapping.set("ParentID", dic['CODE'])
        mapping.set("ParentType", type)
        property = ET.SubElement(mapping, "Property")
        property.set("Name", 'Sequence')
        property.text = str(dic['SEQUENCE'])
        property = ET.SubElement(mapping, "Property")
        property.set("Name", 'Type')
        property.text = str(dic['TYPE'])


# 写xml文件模块
def saveXML(root, filename, indent="\t", newl="\n", encoding="utf-8"):
    rawText = ET.tostring(root)
    dom = minidom.parseString(rawText)
    with open(filename, 'w') as f:
        dom.writexml(f, "", indent, newl, encoding)


# picture文件的ftp目录
ftp_dir = 'ftp://wacos:wacos@172.25.130.5//opt/wenke/expxml_program/data/picture/'
# xml文件中的所有字段要在这里完全一致
object_map = ['FileURL', 'Name', 'OriginalName', 'SortName', 'SearchName', 'Director', 'Kpeople', 'Description', 'Price',\
     'ReleaseYear', 'SeriesType', 'CopyRight', 'ContentProvider', 'VSPCode', 'VolumCount', 'ScriptWriter', 'Compere',\
          'Guest', 'Reporter', 'LicensingWindowStart', 'LicensingWindowEnd', 'SeriesFlag','Language','Duration',\
               'Status', 'SPCode', 'Genre', 'ScreenFormat', 'MediaSpec', 'Type', 'PriceTaxIn', 'SourceType']
conn = cx_Oracle.connect("wacos/nmBKsmp2015@172.25.116.5:1521/orcl")
cr = conn.cursor()
nCount = 0
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
                                                  and rownum<15"

#sql=sqlbase+' '+sqlwhere
#print "GetData SQL: ",sql
cr.execute(sql)
rs = cr.fetchone()
program_columns = [column[0] for column in cr.description]
#program_data = []
print("Begin process exp programs")
while rs:
    print(rs[0])
    program_object = [dict(zip(program_columns, rs))]
    #    print(program_object)

    sqlmovie = "select contentname name ,a.code code,a.fileurl,b.code programcode,c.MediaSpec MediaSpec,type,SCREEN_FORMAT SCREENFORMAT from mediacontent a,program b ,contentdef c where a.ContentDefID=c.ContentDefID and a.status='4'  and mediacontentid in ( \
        select  mediacontentid from programmediacontent where objtype= '1' and objid=%d) and b.programid=%d" % (
        rs[0], rs[0])
    movie_object = sql_object(sqlmovie, conn)
    #    print(movie_object)

    sqlpicture = "select a.code programcode,c.code code, 'ftp://wacos:wacos@172.25.130.5//opt/wenke/expxml_program/data/picture/'||c.picture FileURL,decode(b.picturetypeid,400,0,401,1,402,2,403,3,404,4,405,5,406,6,407,7,0) type,b.sequence sequence from program a,picturemap b,metapicture c \
              where b.objtype='4' and c.status='1'  and a.programid=b.objid and b.metapictureid=c.metapictureid and a.programid=%d" % (
        rs[0])
    picture_object = sql_object(sqlpicture, conn)
    #    print(picture_object)

    nCount = nCount + 1
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if (nCount % 10 == 0):
        print(now + " : Processed " + str(nCount) + " programs")
#   dealprogram(rs,rsmovie,rspicture)
    root_xml = ET.Element("ADI")
    root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    objects = ET.SubElement(root_xml, "Objects")
    mappings = ET.SubElement(root_xml, "Mappings")
    # crteate program
    p_delcolumn = ('PROGRAMID', 'CODE')
    for i in program_object:
        object_deal('Program', i, p_delcolumn)

    # create movie
    m_delcolumn = ('PROGRAMCODE', 'CODE')
    for j in movie_object:
        object_deal('Movie', j, m_delcolumn)
        mapping_deal('Movie', j)

    # create picture
    p_delcolumn = ('PROGRAMCODE', 'CODE', 'SEQUENCE', 'TYPE')
    for k in picture_object:
        object_deal('Picture', k, p_delcolumn)
        mapping_deal('Picture', k)

    tree = ET.ElementTree(root_xml)
    saveXML(root_xml, "../files/c2_%s.xml" % i['PROGRAMID'])
    rs = cr.fetchone()

now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print(now + " : Processed " + str(nCount) + " programs")
print("Finished process exp programs")
cr.close()
conn.close()
