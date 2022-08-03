# 定义一个类，生成xml文件
from xml.etree import ElementTree as ET
from xml.dom import minidom
class XmlCreate:
    def __init__(self, file_name, mediaObjects, dictData):
        self.file_name = file_name
        self.mediaObjects = mediaObjects
        self.dictData = dictData
        self.objects = ET.Element('Objects')
        self.mappings = ET.Element('Mappings')
        self.root = ET.Element('Root')
        self.root.append(self.objects)
        self.root.append(self.mappings)
        self.tree = ET.ElementTree(self.root)
        self.tree.write(self.file_name, encoding='utf-8', xml_declaration=True)
        self.root = self.tree.getroot()
        self.objects = self.root[0]
        self.mappings = self.root[1]
        self.object_map = {'CODE': 'Code', 'PROGRAMCODE': 'ProgramCode', 'SEQUENCE': 'Sequence', 'TYPE': 'Type'}
        self.del_columns = ['CODE', 'PROGRAMCODE', 'SEQUENCE', 'TYPE']

    def create_xml(self):
        for row in self.rows:
            for i in row:
                dic = dict(zip(self.columns, i))
                print(dic)
                if dic['TYPE'] == 'Movie':
                    self.object_deal(dic['TYPE'], dic, self.del_columns)
                    self.mapping_deal(dic['TYPE'], dic)
                else:
                    self.object_deal(dic['TYPE'], dic, self.del_columns)
                    self.mapping_deal(dic['TYPE'], dic)
        self.tree.write(self.file_name, encoding='utf-8', xml_declaration=True)

    def object_deal(self, type, dic, del_columns):
        object = ET.SubElement(self.objects, "Object")
        object.set("Action", "REGIST")
        object.set("Code", dic['CODE'])
        object.set("ElementType", type)

def main():
    columns = ['TYPE', 'PROGRAMCODE', 'SEQUENCE', 'TYPE']
    rows = [('1', '2', '3', 'Movie'), ('4', '5', '6', 'Picture')]
    xml = XmlCreate('test.xml', columns, rows)
    xml.create_xml()

if __name__ == '__main__':
    main()