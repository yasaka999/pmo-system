import openpyxl
from xml.etree import ElementTree as ET
from xml.dom import minidom

# object中的字段对象生成
def object_deal(type, dic, del_columns):
    object = ET.SubElement(objects, "Object")
    object.set("Action", "REGIST")
    object.set("Code", dic['CODE'])
    object.set("ElementType", type)
    object.set("ID", dic['CODE'])
    for key, value in dic.items():
        if key not in del_columns and value is not None:
        #    key = object_name_format(key, object_map)
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



file="../files/hlj_demo_all.xlsx"
#Open the given filename and return the workbook
workbook=openpyxl.load_workbook(file)

#选中工作簿中的表单
sh=workbook.worksheets[0]

# 读取
# print(sh.rows,type(sh.rows))
# 按行读取，每一行的数据放到一个元组中
res=list(sh.rows)

# print(res,type(res))
title=[i.value for i in res[0]]
# print(title)
series_objects=[]
j=0
#遍历除第一行外的其他行
for item in res[1:]:
#    print(item)
    it=[i.value for i in item]
    # 打包成字典
    case=dict(zip(title,it))
    # 添加默认字段
    case['CODE'] = 'HLJDEMO000000'+str(80000+j)
    case['LicensingWindowStart'] = '20180714130410'
    case['LicensingWindowEnd'] = '20280714130410'
    case['SearchName'] = 'hljdemo'
    case['ActorDisplay']= '佚名'
    case['Language'] = '中文'
    case['OriginalCountry']='中国'
    series_objects.append(case)
    j=j+1
#print(cases)

file = open("../files/hlj_series_code.txt", 'w')
picture_object=[]

for i in range(len(series_objects)):
    root_xml = ET.Element("ADI")
    root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    objects = ET.SubElement(root_xml, "Objects")
    mappings = ET.SubElement(root_xml, "Mappings")
    s_delcolumn = ('SERIESID', 'CODE')
    print (series_objects[i])
    object_deal('Series', series_objects[i], s_delcolumn)

    pic1code = 'HLJDEMO000000'+str(60000+2*i)
    pic2code = 'HLJDEMO000000'+str(60000+2*i+1)
    pic_fileurl = 'ftp://wacos:wacos@10.20.30.60:21//opt/wacos/CTMSData/picture/6668/1672972776668.png'
    picture_object = [{'CODE':pic1code,'MAPPINGCODE':series_objects[i]['CODE'],'FileURL':pic_fileurl,'TYPE':'0','SEQUENCE':'1'},\
        {'CODE':pic2code,'MAPPINGCODE':series_objects[i]['CODE'],'FileURL':pic_fileurl,'TYPE':'1','SEQUENCE':'2'}]
    pic_delcolumn = ('CODE', 'SEQUENCE', 'TYPE', 'MAPPINGCODE')
    for k in picture_object:
        object_deal('Picture', k, pic_delcolumn)
        mapping_deal('Picture','Series', k)
   
    print (series_objects[i]['CODE'],series_objects[i]['Name'],sep ='|',file=file)
#    object_deal('Program', cases[i],code,mcode)
    tree = ET.ElementTree(root_xml)
    saveXML(root_xml, "../files/series/hlj_series_%s.xml" %series_objects[i]['CODE'])

file.close()