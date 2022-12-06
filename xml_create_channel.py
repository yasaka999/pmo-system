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
object_map = ['Name', 'ChannelNumber', 'Description', 'CallSign', 'TimeShift',\
     'Type','ChannelCode','BitrateType','MultiCastIP','MultiCastPort']
#conn = cx_Oracle.connect("wacos/nmBKsmp2015@172.25.116.5:1521/orcl")
conn = cx_Oracle.connect("sx0351yd/sx0351yd@172.19.97.211:1521/orcl")

cr = conn.cursor()
nCount = 0
sql = "select channelid,code,name,channelnumber,type,callsign,timeshift,Description from channel where status='4'"

#sql=sqlbase+' '+sqlwhere
#print "GetData SQL: ",sql
cr.execute(sql)
rs = cr.fetchone()
channel_columns = [column[0] for column in cr.description]

print("Begin process exp channels")
while rs:
    # print(rs[0])
    channel_object = [dict(zip(channel_columns, rs))]

    sqlphysicalchannel = "select a.code channelcode ,b.code code ,b.bitratetype,b.sourceip MultiCastIP,b.sourceport MultiCastPort \
        from channel a,physicalchannel b where a.status='4' and a.channelid=b.channelid \
               and  a.channelid=%d" % (rs[0])
    physicalchannel_object = sql_object(sqlphysicalchannel, conn)

    sqlpicture = "select a.code mappingcode,c.code code, 'ftp://wacos:wacos@172.25.130.5//opt/wenke/expxml_program/data/picture/'||c.picture FileURL,\
        decode(b.picturetypeid,400,0,401,1,402,2,403,3,404,4,405,5,406,6,407,7,0) type,b.sequence sequence from channel a,picturemap b,metapicture c \
              where b.objtype='2'   and a.channelid=b.objid and b.metapictureid=c.metapictureid and a.channelid=%d" % (rs[0])
    picture_object = sql_object(sqlpicture, conn)

    nCount = nCount + 1
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if (nCount % 10 == 0):
        print(now + " : Processed " + str(nCount) + " channels")

    root_xml = ET.Element("ADI")
    root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    objects = ET.SubElement(root_xml, "Objects")
    mappings = ET.SubElement(root_xml, "Mappings")
    # crteate channel
    ch_delcolumn = ('CHANNELID', 'CODE')
    for i in channel_object:
        object_deal('Channel', i, ch_delcolumn)

    # create physicalChannel
    pch_delcolumn = ('CODE')
    for j in physicalchannel_object:
        object_deal('PhysicalChannel', j, pch_delcolumn)

    # create picture
    pic_delcolumn = ('CODE', 'SEQUENCE', 'TYPE', 'MAPPINGCODE')
    for k in picture_object:
        object_deal('Picture', k, pic_delcolumn)
        mapping_deal('Picture','Channel', k)

    tree = ET.ElementTree(root_xml)
    saveXML(root_xml, "../files/c2_channel_%s.xml" % i['CHANNELID'])
    rs = cr.fetchone()

now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print(now + " : Processed " + str(nCount) + " channels")
print("Finished process exp channels")
cr.close()
conn.close()
