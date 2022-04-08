import os

from xpinyin import Pinyin
file1 = open("../files/map.txt", "w")
p = Pinyin()
file_dir = "../files/programlist20220317/bak2"
for root, dirs, files in os.walk(file_dir):
    for name in files:
        if name.endswith(".txt"):
            print (name.split(".")[0],end=',',file=file1)
            print (p.get_pinyin(name.split(".")[0],""),file=file1)
        else:
            print (name)
