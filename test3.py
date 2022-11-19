import re

s= 'aaa_user_products_ppv_B93039428_00000000000010010000000000000119_00000555248000116569930565919141'
p_user = s.split('_')[4]
p_code = s.split('_')[5]+'_'+s.split('_')[6]

print(p_user)
print(p_code)

a =['1','abc',' ']
b = 'ab'
if  b not in a:
    print('yes')
for i in a:
    
    print(i)

print (a[1:3])