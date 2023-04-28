# 打开文件并读取数据
with open('../files/program.csv', 'r') as f:
    # 获取第一行作为字段名
    fieldnames = f.readline().strip().split('^&')
    # 构造字典列表
    result = []
    for line in f:
        values = line.strip().split('^&')
        result.append(dict(zip(fieldnames, values)))

# 输出结果
print(result)