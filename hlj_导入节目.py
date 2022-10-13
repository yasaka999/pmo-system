import openpyxl
from xml.etree import ElementTree as ET
from xml.dom import minidom

# object中的字段对象生成
def object_deal(type, dic,code,mcode):
    object = ET.SubElement(objects, "Object")
    object.set("Action", "REGIST")
    object.set("Code", code)
    object.set("ElementType", type)
    object.set("ID", code)
    for key, value in dic.items():
        if  value is not None:
            property = ET.SubElement(object, "Property")
            property.set("Name", key)
            property.text = str(value)
    
    object = ET.SubElement(objects, "Object")
    object.set("Action", "REGIST")
    object.set("Code", mcode)
    object.set("ElementType", "Movie")
    object.set("ID", mcode)
    property = ET.SubElement(object, "Property")
    property.set("Name", "Name")
    property.text = dic["Name"]
    property = ET.SubElement(object, "Property")
    property.set("Name", "FileURL")
    property.text = "ftp://staimspftp:staimspftp@172.25.127.6/media/20180714/734.ts"
    mappings = ET.SubElement(root_xml, "Mappings")
    mapping = ET.SubElement(mappings, "Mapping")
    mapping.set("Action", "REGIST")
    mapping.set("ElementCode", mcode)
    mapping.set("ElementID", mcode)
    mapping.set("ElementType", "Movie")
    mapping.set("ParentCode", code)
    mapping.set("ParentID", code)
    mapping.set("ParentType", 'Program')

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



file="../files/hlj_demo_all.xlsx"
#Open the given filename and return the workbook
workbook=openpyxl.load_workbook(file)

#选中工作簿中的表单
sh=workbook.worksheets[1]

# 读取
# print(sh.rows,type(sh.rows))
# 按行读取，每一行的数据放到一个元组中
res=list(sh.rows)

# print(res,type(res))
title=[i.value for i in res[0]]
# print(title)
cases=[]
#遍历除第一行外的其他行
for item in res[1:]:
#    print(item)
    it=[i.value for i in item]
    # 打包成字典
    case=dict(zip(title,it))
    # 添加默认字段
    case['LicensingWindowStart'] = '20180714130410'
    case['LicensingWindowEnd'] = '20280714130410'
    case['SearchName'] = 'hljdemo'
    case['SeriesFlag'] = '0'
    cases.append(case)
print(cases)
file = open("../files/hlj_program_code.txt", 'w')
for i in range(len(cases)) :
    if True:
#        print (cases[i]['Name'])
        root_xml = ET.Element("ADI")
        root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        objects = ET.SubElement(root_xml, "Objects")
#        mappings = ET.SubElement(root_xml, "Mappings")
    # crteate program
        code = 'HLJDEMO000000'+str(30000+i)
        mcode = 'HLJDEMO000000'+str(22000+i)
        print (code,cases[i]['Name'],file=file)
        object_deal('Program', cases[i],code,mcode)
        tree = ET.ElementTree(root_xml)
        saveXML(root_xml, "../files/hlj_program_%s.xml" %code)

file.close()