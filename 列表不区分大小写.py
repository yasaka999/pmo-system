# 查询列表不区分大小写
field_map = ['Name', 'Code', 'OriginalName', 'SortName']
field = 'NAME'
for key in field_map:
    if key.lower() == field.lower():
        field = key
        break
print(field)
