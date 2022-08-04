import re
a=": 00  abc.txt"
pattern = re.compile(r'\d+.*:')
b=re.search(r'\d.*:',a)
print(b)