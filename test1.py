with open("../files/hlj_program_series_new.txt", "r") as f:
    map1 = {}
    for line in f.readlines():
        line = line.strip("\n")
        b = line.split("|")
        map1[b[1]] = b[0]
print (map1["长安处处有故事-杜回村.ts"])

for key,value in map1.items():
    if  key.split(".")[1] not in  ['ts','mp4']:
        print (key,value)