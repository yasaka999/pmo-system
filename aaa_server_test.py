#!/usr/bin/python
# coding=utf-8
import socket
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

HOST, PORT = '', 8410

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print('Serving HTTP on port %s ...' % PORT)
with open('/root/test.txt', 'r') as f:
    http_data = f.read()
http_head = 'HTTP/1.1 200\r\nContent-Type: text/xml;charset=UTF-8\r\n'
content_length = 'Content-Length:' + str(len(http_data)) + '\r\n'
http_head = http_head + content_length + '\r\n'
http_response = http_head + http_data
print(http_response)

while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024)
    print(request.decode("utf-8"))
    client_connection.sendall(http_response.encode("utf-8"))
    client_connection.close()
'''
功能：可模拟soap_server应答指定的soap消息
不同的端口修改PORT值，应答内容放到test.txt文件里
'''
