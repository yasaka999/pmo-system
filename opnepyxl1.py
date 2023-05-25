from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader

# 打开Excel文件
workbook = load_workbook('../files/test2.xlsx')

# 获取工作表对象
worksheet = workbook['sheet1']  # 替换为你的工作表名称

# 遍历工作表中的图表
# Iterate over all charts in the sheet
for chart in worksheet._charts:
    # Get the anchor object for the chart
    anchor = chart.anchor

    # Print the location of the chart
#    print(anchor._from)

# Get the chart object from the sheet
chart = worksheet._charts

for i in chart:
    #if i.title == '':
        print (i.title.tx.strRef.strCache.ptList)


