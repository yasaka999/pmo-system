import re

pattern = re.compile(r'([^:]+)?(?:\:(\d+))?')
str = 'abcd:12223'
print(pattern.search(str))
print(pattern.search(str).group(1))
print(pattern.search(str).group(2))