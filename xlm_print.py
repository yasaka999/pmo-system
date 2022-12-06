from xml.etree import ElementTree as ET
import sys

def xml_parser(filename):
    list = []
    tree = ET.parse(filename)
    root = tree.getroot()
    for child in root:
        a = child.tag
        for node in child:
            if "ParentType"  in node.attrib.keys():
                b = node.tag+'|'+node.attrib['ElementType']+'|'+node.attrib["ParentType"]
            else:
                b = node.tag+'|'+node.attrib['ElementType']
            c = []
            for k,v in node.attrib.items():
                c.append(k+':'+v)
            c.sort()
            d='|'.join(c)
            list.append(node.tag+'|'+d)
            for object in node:
                list.append(a+'|'+b+'|'+object.attrib['Name']+':'+str(object.text))
    return list
if __name__ == '__main__':
    list1= xml_parser("../files/c2-1.xml")
    for i in list1:
        print (i)