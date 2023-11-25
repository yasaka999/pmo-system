import tkinter as tk
from tkinter import filedialog
from xml.etree import ElementTree as ET
import sys

def parse_xml(filename, result_text):
    result_list = []

    try:
        tree = ET.parse(filename)
    except ET.ParseError as e:
        error_message = f"Error: Invalid XML format in file '{filename}'.\nDetails: {e}"
        print(error_message)
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, error_message)
        result_text.config(state=tk.DISABLED)
        return []

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

def choose_file(entry_var, result_text):
    file_path = filedialog.askopenfilename(
        title="Choose a file",
        filetypes=[
            ("XML files", "*.xml"),
            ("All files", "*.*"),
        ]
    )
    if file_path:
        entry_var.set(file_path)

def process_files(entry1_var, entry2_var, result_text):
    filename1 = entry1_var.get()
    filename2 = entry2_var.get()

    if not filename1 or not filename2:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Please choose both XML files.")
        result_text.config(state=tk.DISABLED)
        return

    list1 = parse_xml(filename1, result_text)
    list2 = parse_xml(filename2, result_text)

    if not list1 or not list2:
        # Parsing error occurred, do not proceed with comparison
        return

    diff = set(list1).symmetric_difference(set(list2))
    diff = sorted(list(diff))

    if not diff:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No difference!")
        result_text.config(state=tk.DISABLED)
    else:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "\n".join(diff))
        result_text.config(state=tk.DISABLED)

def copy_to_clipboard(result_text):
    result = result_text.get(1.0, tk.END)
    result_text.clipboard_clear()
    result_text.clipboard_append(result)
    result_text.update()

# 创建主窗口
root = tk.Tk()
root.title("XML Comparison Tool")

# 文件选择部分
file_label1 = tk.Label(root, text="Choose the first XML file:")
file_label1.grid(row=0, column=0, padx=10, pady=10)

entry1_var = tk.StringVar()
file_entry1 = tk.Entry(root, textvariable=entry1_var, width=40)
file_entry1.grid(row=0, column=1, padx=10, pady=10)

# 默认显示.xml文件，同时增加一个可以选择所有文件类型的选项
browse_button1 = tk.Button(root, text="Browse", command=lambda: choose_file(entry1_var, result_text))
browse_button1.grid(row=0, column=2, padx=10, pady=10)

file_label2 = tk.Label(root, text="Choose the second XML file:")
file_label2.grid(row=1, column=0, padx=10, pady=10)

entry2_var = tk.StringVar()
file_entry2 = tk.Entry(root, textvariable=entry2_var, width=40)
file_entry2.grid(row=1, column=1, padx=10, pady=10)

# 默认显示.xml文件，同时增加一个可以选择所有文件类型的选项
browse_button2 = tk.Button(root, text="Browse", command=lambda: choose_file(entry2_var, result_text))
browse_button2.grid(row=1, column=2, padx=10, pady=10)

# 处理文件部分
process_button = tk.Button(root, text="Process Files", command=lambda: process_files(entry1_var, entry2_var, result_text))
process_button.grid(row=2, column=1, pady=20)

# 结果显示
result_text = tk.Text(root, wrap=tk.NONE, width=60, height=15)
result_text.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky='nsew')
result_text.config(state=tk.DISABLED, wrap='none')

# 创建垂直滚动条
vsb = tk.Scrollbar(root, orient="vertical", command=result_text.yview)
vsb.grid(row=3, column=3, sticky='ns')

# 创建水平滚动条
hsb = tk.Scrollbar(root, orient="horizontal", command=result_text.xview)
hsb.grid(row=4, column=0, columnspan=3, sticky='ew')

result_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

# 复制按钮
copy_button = tk.Button(root, text="Copy to Clipboard", command=lambda: copy_to_clipboard(result_text))
copy_button.grid(row=4, column=1, pady=10)

# 设置窗口的行和列可以调整大小
root.rowconfigure(3, weight=1)
root.columnconfigure(0, weight=1)

# 启动主循环
root.mainloop()
