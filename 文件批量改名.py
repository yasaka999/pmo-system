import os
import sys

def file_rename(path,file_names, file_type,map):
    for file in file_names:
        if file.endswith(file_type):
            if file.split(file_type)[0] in map:
                new_filename = map[file.split(file_type)[0]]+file_type
            else:
                new_filename = file
            print (file, new_filename)
        # os.rename(old,new)
            os.rename(os.path.join(path, file), os.path.join(path, new_filename))

with open(sys.argv[2],'r',encoding='utf8') as f:
    map1 = {}
    for line in f.readlines():
        line = line.strip("\n")
        b = line.split("|")
        map1[b[1]] = b[0]

# 文件路径
file_path=sys.argv[1]
# 列出该文件夹下所有文件名
file_names = os.listdir(file_path)
file_rename(file_path,file_names,".mp4",map1)
file_rename(file_path,file_names,".ts",map1)
file_rename(file_path,file_names,".mov",map1)
