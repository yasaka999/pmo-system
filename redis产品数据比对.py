# 从index文件中提取用户与对应的产品（dict)
# 从product文件中提取用户与产品，与上面做匹配，打印不在其中的记录。
import re
out_file = open('../files/error.txt', 'w')
with open('../files/index_all.txt') as f1:
# 生成dict {userid:product[]}
    order={}
    for index in f1:
        index=index.rstrip()
        user =re.findall(r'aaa_index_user_products_(.+?) ',index)[0]
        product=index.split(' ')[1].split(',')
        order[user] =product

with open('../files/product_all.txt') as f2:
    for line in f2:
        line = line.rstrip()
        p_user = '_'.join(line.split('_')[3:5])
        p_code = '_'.join(line.split('_')[5:])
#        print (p_user, p_code)
        if p_user in order.keys():      
            if p_code not in order[p_user]:        
                print (p_user,p_code,file=out_file)
        else:
            print (p_user,p_code,file=out_file)

out_file.close()