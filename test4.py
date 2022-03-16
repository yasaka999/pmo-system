#coding:utf
with open('fav_test.log') as file_object:
        for line in file_object:
                line=line.strip('\n')
                if line !='':
                        line=eval(line)
                        print (line)
                else:
                        print ('hahaha')

for i in line:
        print (i)
#                print (line)
#                print (line[0])
#                for i in range(len(line)):
#                    print (i)
