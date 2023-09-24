# 从csv中读取生成删除的对象
from xml.etree import ElementTree as ET
from xml.dom import minidom
import csv
import chardet

# object中的字段对象生成
def object_deal(type, code):
    root_xml = ET.Element("ADI")
    root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    objects = ET.SubElement(root_xml, "Objects")
    object = ET.SubElement(objects, "Object")
    object.set("Action", "DELETE")
    object.set("Code", code[0])
    object.set("ElementType", type)
    object.set("ID", code[0])
    property = ET.SubElement(object, "Property")
    property.set("Name", "Name")
    property.text = code[1]
#    tree = ET.ElementTree(root_xml)
    return root_xml

# 写xml文件模块
def saveXML(root, filename, indent="\t", newl="\n", encoding="utf-8"):
    rawText = ET.tostring(root)
    dom = minidom.parseString(rawText)
    with open(filename, 'w',encoding="utf-8") as f:
        dom.writexml(f, "", indent, newl, encoding)

if __name__ == '__main__':
    with open('../files/hlj_program.csv', mode='rb') as f:
        # 检测文件编码
        result = chardet.detect(f.read())
        encoding = result['encoding']
    
    with open('../files/hlj_program.csv', mode='r', encoding=encoding) as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)
            root = object_deal('Program', row)
            saveXML(root, '../files/temp/hlj_del_program_%s.xml '%row[0])
#    code_list = ('123456', '测试节目2')
#    root_xml= object_deal('Program', code_list)
#    saveXML(root_xml, '../files/delProgram_%s.xml' %code_list[0])