import os
import openpyxl
import re
from collections import defaultdict


# 指定目录路径
directory = '../files/28'

# 正则表达式模式匹配时间范围
pattern = r"\d{4}-\d{4}"
# 遍历目录中的所有文件
for filename in os.listdir(directory):
    # 创建一个空列表用于存储最终的打印值
    result_list = []

    # 创建一个字典用于记录每个remark的计数
    remark_sums = defaultdict(int)
    if filename.endswith(".xlsx"):
        file_path = os.path.join(directory, filename)
        
        # 使用正则表达式提取时间范围
        match = re.search(pattern, filename)

        if match:
            time_range = match.group()
        else:
            time_range = "未知"

        # 打开Excel文件
        workbook = openpyxl.load_workbook(file_path)

        # 选择第一个工作表
        sheet = workbook.worksheets[0]

        # 遍历每一行，将第一列、第三列和备注的值添加到列表，并将相同remark的value3值相加
        for row in sheet.iter_rows(min_row=2):
            value1 = row[1].value
            value3 = int(row[2].value)  # 转换为整数类型
            remark = ''

            if '少儿' in value1 or '动画' in value1 or '动漫' in value1 or '儿童' in value1:
                remark = '少儿动漫'
            elif '幻' in value1 or '悬疑' in value1 or '灾难' in value1 or '动作' in value1:
                remark = '科幻悬疑灾难'
            elif '军' in value1 or '战争' in value1:
                remark = '战争警匪'
            elif '爱情' in value1 or '古装' in value1 or '综艺' in value1:
                remark = '爱情古装'
            elif '家庭' in value1 or '伦理' in value1 or '都市' in value1 or 'TVB' in value1:
                remark = '家庭伦理'
            elif '游戏' in value1 or '电竞' in value1:
                remark = '游戏电竞'
            else:
                remark = '其他'

            result_list.append([value1, value3, remark])

            # 将相同remark的value3值相加
            remark_sums[remark] += value3

        # 关闭Excel文件
        workbook.close()

        # 按照item[1]值从小到大排序结果列表
        sorted_list = sorted(result_list, key=lambda x: x[1])

        # 打印最终的排序结果列表和每个remark类别的总数
    #    for item in sorted_list:
    #        print(item[0], item[1], item[2])

        print('---',time_range,'---')

        # 打印每个remark类别的总数
        for remark, total_sum in remark_sums.items() :
            print(total_sum, remark)

