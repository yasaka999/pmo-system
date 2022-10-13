


with open("../files/hlj_series_code.txt", "r") as f:
    map1 = {}
    for line in f.readlines():
        line = line.strip("\n")
        b = line.split(" ")
        map1[b[1].replace('《','').replace('》','').replace('（','').replace('）','').replace('.','').replace('，','').replace('？','')] = b[0]
#print (map1.get('多样星球第一季'))
file = open("../files/hlj_series_program.txt","w")
with open("../files/hlj.txt", encoding='utf8') as f:
    list1 = f.read().split("\n")
    list2 = []
    list3 = []
    for i in range(len(list1)):
        list1[i] = list1[i].replace('│', '').strip()
        if '.mp4' in list1[i] or '.ts' in list1[i] or '.mov' in list1[i] :
            list2.append(list1[i].replace('.mp4', '').replace('.ts', '').replace('.mov','').strip())
for i in list2:
    series = map1.get(i.split('-')[0].replace('《','').replace('》','').replace('（','').replace('）','').replace('.',''))
#    if series is not None:
    print(series,i,sep='|',file=file)
file.close()
