from xml.etree import ElementTree as ET
import sys

def xml_parser(filename):
    list = []
    tree = ET.parse(filename)
    root = tree.getroot()
    for child in root:
        a = child.tag
        for node in child:
            b = node.tag+'|'+node.attrib['ElementType']
            for object in node:
                list.append(a+'|'+b+'|'+object.attrib['Name']+'|'+object.text)
    return list

if __name__ == '__main__':
    xml1 = sys.argv[1]
    xml2 = sys.argv[2]
    list1 = xml_parser(xml1)
    list2 = xml_parser(xml2)
    set1 = set(list1)
    set2 = set(list2)
    diff = set1.symmetric_difference(set2)
    if not diff:
        print (" all the same ! ")
    else:
        print (diff)
