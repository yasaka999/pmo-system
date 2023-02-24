import xlrd
from xml.etree import ElementTree as ET
from xml.dom import minidom
import re

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

# 打开 Excel 文件
workbook = xlrd.open_workbook('../files/岩华电视剧.xls')

# 获取第一个工作表
worksheet = workbook.sheet_by_index(0)

# 获取字段名称
field_names = [cell.value for cell in worksheet.row(0)]

# 遍历每一行，将每行数据存储在一个字典中，然后添加到列表中
data = []
for row_idx in range(1, worksheet.nrows):
    row_data = {}
    for col_idx in range(worksheet.ncols):
        cell_value = worksheet.cell_value(row_idx, col_idx)
        if isinstance(cell_value, float):
            # 如果确定单元格中的值为浮点数，且小数部分为0，使用 int() 进行转换
            cell_value = int(cell_value) if cell_value.is_integer() else round(cell_value)
        row_data[field_names[col_idx]] = cell_value
    data.append(row_data)


# 选出剧头，增加code
series_objects = [d for d in data if d['Sequence']=='']
for i, d in enumerate(series_objects):
    d['CODE'] = 'SXYANHUA000000'+str(80000+i)

# 选出子集,增加code,seriesflag
program_objects = [d for d in data if d['Sequence']!='']
for i, d in enumerate(program_objects):
    d['CODE'] = 'SXYANHUA000000'+str(10000+i)
    d['SeriesFlag'] = '1'

# 生成剧头和子集的映射:code,mappingcode,sequence
#[{pcode:,scode,sequence},{pcode:,scode,sequence}]
pattern = r'^(.*)第\d+.*$'  # 定义正则表达式模式
seriesdtl_objects = []
for d1 in series_objects:
    print (d1)
    for d2 in program_objects:
        print(d2)
        match = re.match(pattern, d2['Name'])  # 匹配字符串
        if d1['Name'] == match.group(1):
            seriesdtl = {}  # 创建一个新的字典对象
            seriesdtl['seriescode'] = d1['CODE']
            seriesdtl['programcode'] = d2['CODE']
            seriesdtl['sequence'] = d2['Sequence']
            seriesdtl_objects.append(seriesdtl)  # 将新的字典对象添加到列表中

for data in seriesdtl_objects:
    print (data)


    
'''
# 打印数据
for row_data in series_objects :
    print(row_data)

for row_data in program_objects :
    print(row_data)
'''