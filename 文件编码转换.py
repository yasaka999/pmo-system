
import chardet
import codecs

#filename = '../files/LIVEBATCHSCHEDULE.txt'
filename = '../files/nmtest-format.txt'
with open(filename, 'rb') as f:
    data = f.read()
    encoding_type = chardet.detect(data)
    print(encoding_type)

filename_in = '../files/nmtest-format.txt'
filename_out = '../files/nmtest-format-gb2312.txt'

# 输入文件的编码类型
encode_in = 'utf8'

# 输出文件的编码类型
encode_out = 'gb2312'

with codecs.open(filename=filename_in, mode='r', encoding=encode_in) as fi:
    data = fi.read()
    with open(filename_out, mode='w', encoding=encode_out) as fo:
        fo.write(data)
        fo.close()

with open(filename_out, 'rb') as f:
    data = f.read()
    print(chardet.detect(data))


