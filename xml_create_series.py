# create xml file
# 分两大类方法，register和mapping
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
#    print (columns)
    row = cursor.fetchall()
    data = []
    for i in row:
        data.append(dict(zip(columns, i)))
    cursor.close()
#    print (data)
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


# mapping生成模块，通用方法
def mapping_deal(parenttype,elementtype,dic):
    if parenttype != "Picture":
        mapping = ET.SubElement(mappings, "Mapping")
        mapping.set("Action", "REGIST")
        mapping.set("ElementCode", dic['CODE'])
        mapping.set("ElementID", dic['CODE'])
        mapping.set("ElementType", elementtype)
        mapping.set("ParentCode", dic['MAPPINGCODE'])
        mapping.set("ParentID", dic['MAPPINGCODE'])
        mapping.set("ParentType", parenttype)
        if parenttype == "Series":
            property = ET.SubElement(mapping, "Property")
            property.set("Name", 'Sequence')
            property.text = str(dic['SEQUENCE'])
    else :
        mapping = ET.SubElement(mappings, "Mapping")
        mapping.set("Action", "REGIST")
        mapping.set("ElementCode", dic['MAPPINGCODE'])
        mapping.set("ElementID", dic['MAPPINGCODE'])
        mapping.set("ElementType", elementtype)
        mapping.set("ParentCode", dic['CODE'])
        mapping.set("ParentID", dic['CODE'])
        mapping.set("ParentType", parenttype)        
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
               'Status', 'SPCode', 'Genre', 'ScreenFormat', 'MediaSpec', 'Type', 'PriceTaxIn', 'SourceType','OrgAirDate','OPIncharge']
conn = cx_Oracle.connect("wacos/nmBKsmp2015@172.25.116.5:1521/orcl")
cr = conn.cursor()
nCount = 0
sql = "SELECT A.SeriesID, A.CODE,A.NAME,A.ALIAS OriginalName,\
    A.TITLE_SORT_NAME SortName,A.TITLE_SEARCH_NAME SearchName,substr(A.Director,0,47) Director,\
        substr(A.Kpeople,0,147) Kpeople,to_char(A.VALIDTHROUGH,'YYYYMMDDHH24MiSS') LicensingWindowStart, \
            to_char(A.VALIDUNTIL,'YYYYMMDDHH24MiSS') LicensingWindowEnd,\
                A.DESCRIPTION,A.PRICE PriceTaxIn, A.VolumCount,\
                    A.ReleaseYear,C.Code VSPCode,A.CopyRight, A.ContentProvider,\
                        substr(A.ScriptWriter,0,47) ScriptWriter,\
                            substr(A.Compere,0,47) Compere,substr(A.Guest,0,47) Guest,substr(A.Reporter,0,47) Reporter,\
                                A.OPIncharge,B.Status, A.Genre,A.overduetime,\
                                    A.NewPrice,A.Rating,A.ORGAIRDATE from series A, domainobjects B,\
                                         vsp C  where A.SeriesID=B.ObjID and A.VSPID=C.VSPID and B.ObjType='35' \
                                              and B.DomainID=1 and A.status='4' and rownum<15"

cr.execute(sql)
rs = cr.fetchone()
series_columns = [column[0] for column in cr.description]

print("Begin process exp series")
while rs:
    print(rs[0])
    series_object = [dict(zip(series_columns, rs))]
    #    print(series_object)

    sqlpicture = "select a.code mappingcode,c.code code, 'ftp://wacos:wacos@172.25.130.5//opt/wenke/expxml_series/data/picture/'||c.picture FileURL,\
        decode(b.picturetypeid,400,0,401,1,402,2,403,3,404,4,405,5,406,6,407,7,0) type,\
            b.sequence sequence from series a,picturemap b,metapicture c \
              where b.objtype='5'   and a.seriesid=b.objid and b.metapictureid=c.metapictureid and a.seriesid=%d" % (rs[0])
    picture_object = sql_object(sqlpicture, conn)
    # print(picture_object)

    sqlseriesdtl = "select c.code,a.code mappingcode,b.seq sequence \
              from series a ,seriesdtl b,program c where a.seriesid=b.seriesid \
                and b.programid=c.programid and a.seriesid=%d order by b.seq" % (rs[0])
    seriesdtl_object = sql_object(sqlseriesdtl, conn)

    nCount = nCount + 1
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if (nCount % 10 == 0):
        print(now + " : Processed " + str(nCount) + " series")

    root_xml = ET.Element("ADI")
    root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    objects = ET.SubElement(root_xml, "Objects")
    mappings = ET.SubElement(root_xml, "Mappings")
    # crteate series
    s_delcolumn = ('SERIESID', 'CODE')
    for i in series_object:
        object_deal('Series', i, s_delcolumn)

    # create picture
    pic_delcolumn = ('CODE', 'SEQUENCE', 'TYPE', 'MAPPINGCODE')
    for k in picture_object:
        object_deal('Picture', k, pic_delcolumn)
        mapping_deal('Picture','Series', k)
    
    # create seriesdtl
    for l in seriesdtl_object:
        mapping_deal('Series','Program', l)


    tree = ET.ElementTree(root_xml)
    saveXML(root_xml, "../files/c2_series_%s.xml" % i['SERIESID'])
    rs = cr.fetchone()

now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print(now + " : Processed " + str(nCount) + " series")
print("Finished process exp series")
cr.close()
conn.close()
