import urllib.parse
import execjs

js_file = './encry.js'  # <-- rsa.js文件地址
with open(js_file, 'r', encoding='utf-8') as f:
    js_code = f.read()

js = execjs.compile(js_code)
password = urllib.parse.quote(js.call('getRsaResult', 'admin'))
print('password:', password)