import os
import shutil
map_file = "../files/map.txt"
src_dir = "../files/programlist20220317"
dst_dir = "../files/programlist20220317_pinyin"
bak_dir = "../files/programlist20220317_bak"

def mapping(map_file):
    map1 = {}
    with open(map_file, "r") as f:
        for line in f.readlines():
            line = line.strip("\n")
            b = line.split(",")
            map1[b[0]] = b[1]
    return map1

map1 = mapping(map_file)

src_files = os.listdir(src_dir)
for src_name in src_files:
    if src_name.endswith(".txt"):
        dst_name = map1[src_name.split(".")[0]]
        print(src_name)
        print(dst_name + ".txt")
        shutil.copy(src_dir + "/" + src_name, dst_dir + "/" + dst_name + ".txt")
        shutil.copy(src_dir + "/" + src_name, dst_dir + "/" + dst_name + ".txt.ok")
        shutil.move(src_dir + "/" + src_name, bak_dir + "/" + src_name)
