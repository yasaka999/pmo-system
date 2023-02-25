import xlrd
import re
import codecs
from xml.etree import ElementTree as ET
from xml.dom import minidom


# object中的字段对象生成，通用方法
def object_deal(type, dic, del_columns):
    object = ET.SubElement(objects, "Object")
    object.set("Action", "REGIST")
    object.set("Code", dic["CODE"])
    object.set("ElementType", type)
    object.set("ID", dic["CODE"])
    for key, value in dic.items():
        if key not in del_columns and value is not None:
            #    key = object_name_format(key, object_map)
            property = ET.SubElement(object, "Property")
            property.set("Name", key)
            property.text = str(value)


# mapping生成模块，通用方法
def mapping_deal(parenttype, elementtype, dic):
    if parenttype != "Picture":
        mapping = ET.SubElement(mappings, "Mapping")
        mapping.set("Action", "REGIST")
        mapping.set("ElementCode", dic["CODE"])
        mapping.set("ElementID", dic["CODE"])
        mapping.set("ElementType", elementtype)
        mapping.set("ParentCode", dic["MAPPINGCODE"])
        mapping.set("ParentID", dic["MAPPINGCODE"])
        mapping.set("ParentType", parenttype)
        if parenttype == "Series":
            property = ET.SubElement(mapping, "Property")
            property.set("Name", "Sequence")
            property.text = str(dic["SEQUENCE"])
    else:
        mapping = ET.SubElement(mappings, "Mapping")
        mapping.set("Action", "REGIST")
        mapping.set("ElementCode", dic["MAPPINGCODE"])
        mapping.set("ElementID", dic["MAPPINGCODE"])
        mapping.set("ElementType", elementtype)
        mapping.set("ParentCode", dic["CODE"])
        mapping.set("ParentID", dic["CODE"])
        mapping.set("ParentType", parenttype)
        property = ET.SubElement(mapping, "Property")
        property.set("Name", "Sequence")
        property.text = str(dic["SEQUENCE"])
        property = ET.SubElement(mapping, "Property")
        property.set("Name", "Type")
        property.text = str(dic["TYPE"])


# 写xml文件模块
def saveXML(root, filename, indent="\t", newl="\n", encoding="utf-8"):
    rawText = ET.tostring(root)
    dom = minidom.parseString(rawText)
    with codecs.open(filename, "w", encoding="utf-8") as f:
        dom.writexml(f, "", indent, newl, encoding)


# 打开 Excel 文件
workbook = xlrd.open_workbook("../files/岩华电视剧1.xls")

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
            cell_value = (
                int(cell_value) if cell_value.is_integer() else round(cell_value)
            )
        row_data[field_names[col_idx]] = cell_value
    data.append(row_data)

# 选出剧头，按sequence是否为空做判断，并增加code
series_objects = [d for d in data if d["Sequence"] == ""]
for i, d in enumerate(series_objects):
    d["CODE"] = "SXYANHUA000000" + str(80000 + i)
# 选出电影,以volumecount=1做判断，增加code,seriesflag=0
program_objects = [d for d in data if d["VolumnCount"] == 1]
for i, d in enumerate(program_objects):
    d["CODE"] = "SXYANHUA000000" + str(20000 + i)
    d["SeriesFlag"] = "0"
# 选出子集,增加code,seriesflag=1
single_program_objects = [
    d for d in data if (d["Sequence"] != "" and d["VolumnCount"] != 1)
]
for i, d in enumerate(single_program_objects):
    d["CODE"] = "SXYANHUA000000" + str(10000 + i)
    d["SeriesFlag"] = "1"
# 生成剧头和子集的映射,以名称做匹配规则（截取第+数字前面的内容）prgramcode,seriescode,sequence
pattern = r"^(.*)第\d+.*$"
seriesdtl_objects = []
for d1 in series_objects:
    for d2 in single_program_objects:
        #        print (d2)
        match = re.match(pattern, d2["Name"])
        if d1["Name"] == match.group(1):
            seriesdtl = {}
            seriesdtl["MAPPINGCODE"] = d1["CODE"]
            seriesdtl["CODE"] = d2["CODE"]
            seriesdtl["SEQUENCE"] = d2["Sequence"]
            seriesdtl_objects.append(seriesdtl)

# 记录下这批生成的数据
file = open("../files/sx_yanhua.txt", "w")
for i in series_objects:
    print(i["CODE"], i["Name"], sep="|", file=file)
for i in program_objects:
    print(i["CODE"], i["Name"], sep="|", file=file)
for i in single_program_objects:
    print(i["CODE"], i["Name"], sep="|", file=file)
file.close()

# 生成series的xml
for i in range(len(series_objects)):
    root_xml = ET.Element("ADI")
    root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    objects = ET.SubElement(root_xml, "Objects")
    mappings = ET.SubElement(root_xml, "Mappings")
    s_delcolumn = ("Sequence", "CODE", "Time")
    #    print (series_objects[i])
    object_deal("Series", series_objects[i], s_delcolumn)

    seriesdtl_object = [
        d for d in seriesdtl_objects if d["MAPPINGCODE"] == series_objects[i]["CODE"]
    ]
    for l in seriesdtl_object:
        mapping_deal("Series", "Program", l)
    #    object_deal('Program', cases[i],code,mcode)
    tree = ET.ElementTree(root_xml)
    saveXML(root_xml, "../files/sx_series_%s.xml" % series_objects[i]["CODE"])


# 生成single_program的xml

for i in range(len(single_program_objects)):
    root_xml = ET.Element("ADI")
    root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    objects = ET.SubElement(root_xml, "Objects")
    mappings = ET.SubElement(root_xml, "Mappings")
    p_delcolumn = ("VolumnCount", "CODE", "Sequence", "Time")
    #    print (program_objects[i])
    object_deal("Program", single_program_objects[i], p_delcolumn)

    #    object_deal('Program', cases[i],code,mcode)
    tree = ET.ElementTree(root_xml)
    saveXML(
        root_xml,
        "../files/sx_single_program_%s.xml" % single_program_objects[i]["CODE"],
    )

# 生成program的xml

for i in range(len(program_objects)):
    root_xml = ET.Element("ADI")
    root_xml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    objects = ET.SubElement(root_xml, "Objects")
    mappings = ET.SubElement(root_xml, "Mappings")
    p_delcolumn = ("VolumnCount", "CODE", "Sequence", "Time")
    #    print (program_objects[i])
    object_deal("Program", program_objects[i], p_delcolumn)

    #    object_deal('Program', cases[i],code,mcode)
    tree = ET.ElementTree(root_xml)
    saveXML(root_xml, "../files/sx_program_%s.xml" % program_objects[i]["CODE"])
