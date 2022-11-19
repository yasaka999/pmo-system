from xml.etree import ElementTree as ET
import sys

def xml_parser(filename):
    list = []
    file = open(filename)
    ori_xml = file.read()
    file.close()
    xml = ori_xml.replace("utf-8","GBK")
    print (xml)
    tree = ET.parse(ET.fromstring(xml))
    root = tree.getroot()
    for child in root:
        a = child.tag
        for node in child:
            b = node.tag+'|'+node.attrib['ElementType']
            for object in node:
                list.append(a+'|'+b+'|'+object.attrib['Name']+'|'+str(object.text))
    return list

if __name__ == '__main__':
    list1 = xml_parser(sys.argv[1])
    list2 = xml_parser(sys.argv[2])
    diff = set(list1).symmetric_difference(set(list2))
    diff = sorted(list(diff))
    if not diff:
        print (" no difference ! ")
    else:
        for i in diff:
            print (i)
