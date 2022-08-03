# deal with xml file
from xml.etree import ElementTree as ET
from xml.dom import minidom

from jinja2 import DictLoader

from class_xml import main
'''
tree= ET.ElementTree(file='../files/REGIST.xml')
# print(tree)
root = tree.getroot()
print(root.tag)
print(root.attrib)
for sub in root:
    print(sub.tag, sub.attrib)
for ele in tree.iter(tag="Property"):
    print(ele.tag, ele.attrib, ele.text)
print(root[0][0][1].text)
'''
class XmlDeal:
    def __init__(self, file_name, type, dictData, del_columns):
        self.object_map = ['FileURL', 'Name', 'OriginalName', 'SortName', 'SearchName', 'Director', 'Kpeople', 'Description', 'Price',\
     'ReleaseYear', 'SeriesType', 'CopyRight', 'ContentProvider', 'VSPCode', 'VolumCount', 'ScriptWriter', 'Compere',\
          'Guest', 'Reporter', 'LicensingWindowStart', 'LicensingWindowEnd', 'SeriesFlag','Language','Duration',\
               'Status', 'SPCode', 'Genre', 'ScreenFormat', 'MediaSpec', 'Type', 'PriceTaxIn', 'SourceType']
        self.file_name = file_name
        self.type = type
        self.dictData = dictData
        self.del_columns = del_columns
        self.root_xml = ET.Element('ADI')
        self.root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.objects = ET.SubElement(self.root_xml, "Objects")
        self.mappings = ET.SubElement(self.root_xml, "Mappings")


    def object_name_format(self,name):
        for new_name in self.object_map:
            if new_name.lower() == name.lower():
                name = new_name
                break
        return name

    def object_deal(self,type):
        object = ET.SubElement(self.objects, "Object")
        object.set("Action", "REGIST")
        object.set("Code", self.dictData['CODE'])
        object.set("ElementType", type)
        object.set("ID", self.dictData['CODE'])
        for key, value in self.dictData.items():
            if key not in self.del_columns and value is not None:
                key = self.object_name_format(key)
                property = ET.SubElement(object, "Property")
                property.set("Name", key)
                property.text = str(value)

    def mapping_deal(self,type):
        if type != 'Picture':
            mapping = ET.SubElement(self.mappings, "Mapping")
            mapping.set("Action", "REGIST")
            mapping.set("ElementCode", self.dictData['CODE'])
            mapping.set("ElementID", self.dictData['CODE'])
            mapping.set("ElementType", type)
            mapping.set("ParentCode", self.dictData['PROGRAMCODE'])
            mapping.set("ParentID", self.dictData['PROGRAMCODE'])
            mapping.set("ParentType", 'Program')
        else:
            mapping = ET.SubElement(self.mappings, "Mapping")
            mapping.set("Action", "REGIST")
            mapping.set("ElementCode", self.dictData['PROGRAMCODE'])
            mapping.set("ElementID", self.dictData['PROGRAMCODE'])
            mapping.set("ElementType", 'Program')
            mapping.set("ParentCode", self.dictData['CODE'])
            mapping.set("ParentID", self.dictData['CODE'])
            mapping.set("ParentType", type)
            property = ET.SubElement(mapping, "Property")
            property.set("Name", 'Sequence')
            property.text = str(self.dictData['SEQUENCE'])
            property = ET.SubElement(mapping, "Property")
            property.set("Name", 'Type')
            property.text = str(self.dictData['TYPE'])
    

    def saveXML(self,root, indent="\t", newl="\n", encoding="utf-8"):
        rawText = ET.tostring(root)
        dom = minidom.parseString(rawText)
        with open(self.file_name, 'w') as f:
            dom.writexml(f, "", indent, newl, encoding)
            

def main():
    testData = {'CODE': '12345', 'Name': 'test', 'OriginalName': 'test', 'SortName': 'test', 'SearchName': 'test', 'Director': 'test', 'Kpeople': 'abcd', 'Description': 'test', 'Price': 'test', 'ReleaseYear': 'test', 'SeriesType': 'test', 'CopyRight': 'test', 'ContentProvider': 'test', 'VSPCode': 'test', 'VolumCount': 'test', 'ScriptWriter': 'test', 'Compere': 'test', 'Guest': 'test', 'Reporter': 'test', 'LicensingWindowStart': 'test', 'LicensingWindowEnd': 'test', 'SeriesFlag': 'test', 'Language': 'test', 'Duration': 'test', 'Status': 'test', 'SPCode': 'test', 'Genre': 'test', 'ScreenFormat': 'test', 'MediaSpec': 'test', 'Type': 'test', 'PriceTaxIn': 'test', 'SourceType': 'test'}
    delcolumn = ('PROGRAMID', 'CODE')
    xml_deal = XmlDeal('../files/test2.xml', 'Movie', testData, delcolumn)
    xml_deal.object_deal('Program')
    xml_deal.object_deal('Movie')
    xml_deal.mapping_deal('Movie')
    xml_deal.saveXML(xml_deal.root_xml)

if __name__ == '__main__':
    main()

