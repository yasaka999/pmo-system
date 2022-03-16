#coding:utf
with open('fav_test.log') as file_object:
#        line1=[]
        for line in file_object:
                if line == '\n':
                        continue
                else:
                        line=eval(line)
                        for i in line:
                                print(i) 