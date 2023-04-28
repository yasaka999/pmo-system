import socket
import threading

HOST, PORT = "", 8510
soap_response = '<?xml version="1.0" encoding="utf-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" \
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\
        <soapenv:Body><ns1:ExecCmdResponse soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:ns1="iptv">\
            <ExecCmdReturn xsi:type="ns1:CSPResult"><Result xsi:type="xsd:int">0</Result><ErrorDescription xsi:type="soapenc:string" \
                xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">Receive the request:and ready to process.</ErrorDescription></ExecCmdReturn>\
                    </ns1ExecCmdResponse></soapenv:Body></soapenv:Envelope>'
def httpresponse(http_data):
    http_head = "HTTP/1.1 200\r\nContent-Type: text/xml;charset=UTF-8\r\n"
    content_length = "Content-Length:" + str(len(http_data)) + "\r\n"
    http_head = http_head + content_length + "\r\n"
    http_response = http_head + http_data
    return http_response

def handle_request(client_socket):
    request = b""
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        request += data
        if b"\r\n\r\n" in request:
            # we received the complete HTTP header
            # extract Content-Length value from header
            headers, body = request.split(b"\r\n\r\n", 1)
            header_lines = headers.decode("utf-8").split("\r\n")
            content_length = 0
            for line in header_lines:
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":")[1].strip())
                    break
            if content_length == 0:
                # there is no message body, we can process the request
                print(f"Received message: {request.decode('utf-8')}")
                response = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\nConnection: keep-alive\r\n\r\n"
                client_socket.sendall(response)
            else:
                # we received a request with message body, wait for more data
                while len(body) < content_length:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    body += data
                if len(body) >= content_length:
                    # we received the complete message
                    request = headers + b"\r\n\r\n" + body[:content_length]
                    print(f"Received message: {request.decode('utf-8')}")
                    response = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\nConnection: keep-alive\r\n\r\n"
                    client_socket.sendall(httpresponse(soap_response).encode("utf-8"))
    # close the socket when the loop ends
    client_socket.close()

def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(5)
    print(f"Serving HTTP on port {PORT} ...")

    while True:
        client_socket, client_address = listen_socket.accept()
        t = threading.Thread(target=handle_request, args=(client_socket,))
        t.start()

if __name__ == '__main__':
    serve_forever()
