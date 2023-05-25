
import sys
import pandas as pd
import re

# 获取命令行参数
input_file = sys.argv[1]

# 读取xlsx文件
df = pd.read_excel(input_file)

# 定义函数，根据通用规则处理频道名称
def process_channel_name(channel_name):
    processed_name = channel_name.strip()  # 去除空格
    processed_name = processed_name = re.sub(r'\(高清\)|高清|标清|\(标清\)|\（高清\）', '', channel_name)  # 去掉标高清
    return processed_name

# 处理频道名称
df['频道名称'] = df['频道名称'].apply(process_channel_name)

# 按频道名称合并相同频道的列，并对其他列的值进行求和
df_merged = df.groupby('频道名称').sum().reset_index()

# 按收视时长倒序排列
df_merged = df_merged.sort_values(by='收视时长（H）', ascending=False)

# 构造输出文件名
output_file = input_file.replace('.xlsx', '_new.xlsx')

# 保存处理后的结果为新的xlsx文件
df_merged.to_excel(output_file, index=False)
print(f"处理结果已保存至 {output_file}")
