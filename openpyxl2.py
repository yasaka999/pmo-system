from openpyxl import load_workbook

def get_charts_from_worksheet(file_path, sheet_name):
    # 加载工作簿
    workbook = load_workbook(file_path)
    
    # 选择工作表
    sheet = workbook[sheet_name]
    
    # 获取图表对象
    charts = sheet._charts
    
    return charts

# 示例用法
file_path = '../files/test2.xlsx'  # Excel 文件路径
sheet_name = 'sheet1'       # 工作表名称

charts = get_charts_from_worksheet(file_path, sheet_name)

# 打印图表数量和名称
print("图表数量:", len(charts))
for chart in charts:
    print("图表名称:", chart.title)
