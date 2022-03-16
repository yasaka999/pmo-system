# test.py
# coding=utf-8
a = [1, 2, 4, 5, 10, 15,100]
if a[0] != 1:
	for i in range(1, a[0]):
		lost.append(i)
	lost2 = sorted(list(set(range(a[0], a[-1]+1))-set(a)))
	print (lost+lost2)
#    print (sorted(list(set(range(a[0],a[-1]+1))-set(a))))
else:
	print (sorted(list(set(range(a[0],a[-1]+1))-set(a))))


