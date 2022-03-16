#!/usr/bin/python
import socket

HOST, PORT = "", 3410

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print("Serving HTTP on port %s ..." % PORT)
with open("/root/1.txt", "r") as f:
    http_response = f.read()
#    print (http_response)
while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024)
    print(request.decode("utf-8"))
    client_connection.sendall(http_response.encode("utf-8"))
    client_connection.close()
    print(http_response)

"""
1.txt like this: modifly as you like
HTTP/1.1 200 
Content-Type: text/xml;charset=UTF-8
Content-Length: 530
Date: Fri, 17 Apr 2020 08:20:20 GMT

<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><loginResponse xmlns="http://user.webservice.surftv.shtel.com"><loginReturn><Description>success</Description><EpgGroupNMB>1</EpgGroupNMB><Products></Products><Result>0</Result><TokenExpireTime>20200427231734</TokenExpireTime><UserGroupNMB>4008</UserGroupNMB><UserToken>015955027879i001X200427231734521</UserToken><CDNID xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/></loginReturn></loginResponse></soap:Body></soap:Envelope>
"""
