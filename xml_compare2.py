from xml.etree import ElementTree as ET
import sys
# python2下编码格式如有问题，去掉下面两行注释
# reload(sys)
# sys.setdefaultencoding('utf-8')
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
            list.append((node.tag+'|'+d).strip())
            for object in node:
                list.append(((a+'|'+b+'|'+object.attrib['Name']+':'+str(object.text).strip().replace('None', ''))).strip())
    return list

if __name__ == '__main__':
    list1 = xml_parser(sys.argv[1])
#    print (list1)
    list2 = xml_parser(sys.argv[2])
#    print (list2)
    diff = set(list1).symmetric_difference(set(list2))
    diff = sorted(list(diff))
    if not diff:
        print (" no difference ! ")
    else:
        for i in diff:
            print (i)
