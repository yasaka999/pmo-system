from xml.etree import ElementTree as ET
import sys

def parse_xml(filename):
    result_list = []
# 增加对xml文件格式的检查
    try:
        tree = ET.parse(filename)
    except ET.ParseError as e:
        print(f"Error: Invalid XML format in file '{filename}'.")
        print(f"Details: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    root = tree.getroot()

    for child in root:
        parent_tag = child.tag
        for node in child:
            element_type = node.attrib.get('ElementType', '')
            parent_type = node.attrib.get('ParentType', '')

            if parent_type:
                node_info = f"{node.tag}|{element_type}|{parent_type}"
            else:
                node_info = f"{node.tag}|{element_type}"

            attributes = [f"{k}:{v}" for k, v in sorted(node.attrib.items())]
            attributes_str = '|'.join(attributes)

            result_list.append(f"{node.tag}|{attributes_str}".strip())

            for obj in node:
                result_list.append(f"{parent_tag}|{node_info}|{obj.attrib['Name']}:{str(obj.text).strip().replace('None', '')}".strip())

    return result_list

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py file1.xml file2.xml")
        sys.exit(1)

    list1 = parse_xml(sys.argv[1])
    list2 = parse_xml(sys.argv[2])

    diff = set(list1).symmetric_difference(set(list2))
    diff = sorted(list(diff))

    if not diff:
        print("No difference!")
    else:
        for item in diff:
            print(item)
