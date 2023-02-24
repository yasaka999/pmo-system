# 从csv中读取生成对象
from asyncore import read
from xml.etree import ElementTree as ET
from xml.dom import minidom
import csv


# object中的字段对象生成
def object_deal(name, code,mcode,scode):
    root_xml = ET.Element("ADI")
    root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    objects = ET.SubElement(root_xml, "Objects")
    object = ET.SubElement(objects, "Object")
    object.set("Action", "REGIST")
    object.set("Code", code)
    object.set("ElementType", "Program")
    object.set("ID", code)
    property = ET.SubElement(object, "Property")
    property.set("Name", "Name")
    property.text = name
    property = ET.SubElement(object, "Property")
    property.set("Name", "SeriesFlag")
    property.text = "1"
    property = ET.SubElement(object, "Property")
    property.set("Name", "Duration")
    property.text = "30"
    property = ET.SubElement(object, "Property")
    property.set("Name", "LicensingWindowStart")
    property.text = "20180714130410"
    property = ET.SubElement(object, "Property")
    property.set("Name", "LicensingWindowEnd")
    property.text = "20280714130410"
    property = ET.SubElement(object, "Property")
    property.set("Name", "SearchName")
    property.text = "hljdemo"

    object = ET.SubElement(objects, "Object")
    object.set("Action", "REGIST")
    object.set("Code", mcode)
    object.set("ElementType", "Movie")
    object.set("ID", mcode)
    property = ET.SubElement(object, "Property")
    property.set("Name", "Name")
    property.text = name
    property = ET.SubElement(object, "Property")
    property.set("Name", "FileURL")
    property.text = "ftp://wacos:wacos@10.20.30.60:21//opt/wacos/ftp/%s.ts" %mcode
    mappings = ET.SubElement(root_xml, "Mappings")
    mapping = ET.SubElement(mappings, "Mapping")
    mapping.set("Action", "REGIST")
    mapping.set("ElementCode", mcode)
    mapping.set("ElementID", mcode)
    mapping.set("ElementType", "Movie")
    mapping.set("ParentCode", code)
    mapping.set("ParentID", code)
    mapping.set("ParentType", 'Program')

    mapping = ET.SubElement(mappings, "Mapping")
    mapping.set("Action", "REGIST")
    mapping.set("ElementCode", code)
    mapping.set("ElementID", code)
    mapping.set("ElementType", "Program")
    mapping.set("ParentCode", scode)
    mapping.set("ParentID", scode)
    mapping.set("ParentType", 'Series')


#    tree = ET.ElementTree(root_xml)
    return root_xml

# 写xml文件模块
def saveXML(root, filename, indent="\t", newl="\n", encoding="utf-8"):
    rawText = ET.tostring(root)
    dom = minidom.parseString(rawText)
    with open(filename, 'w') as f:
        dom.writexml(f, "", indent, newl, encoding)

if __name__ == '__main__':
    with open("../files/hlj.txt", encoding='utf8') as f:
        list1 = f.read().split("\n")
        list2 = []
        for i in range(len(list1)):
            list1[i] = list1[i].replace('│', '').strip()
            if '.mp4' in list1[i] or '.ts' in list1[i] or '.mov' in list1[i] :
                list2.append(list1[i].replace('.mp4', '').replace('.ts', '').replace('.mov','').strip())
#    print (len(list2))
    for i in range(len(list2)):
        print (list2[i],'HLJDEMO000000'+str(10000+i),sep=',')
        code = 'HLJDEMO000000'+str(30000+i)
        mcode = 'HLJDEMO000000'+str(22000+i)
        root = object_deal(list2[i], code, mcode)
        saveXML(root, '../files/test_%s.xml '%code)
#    code_list = ('123456', '测试节目2')
#    root_xml= object_deal('Program', code_list)
#    saveXML(root_xml, '../files/delProgram_%s.xml' %code_list[0])