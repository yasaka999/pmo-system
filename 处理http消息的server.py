import socket

HOST, PORT = "", 8510

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
                response = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
                client_socket.sendall(response)
                client_socket.close()
                return
            if len(body) >= content_length:
                # we received the complete message
                request = headers + b"\r\n\r\n" + body[:content_length]
                print(f"Received message: {request.decode('utf-8')}")
                response = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
                client_socket.sendall(response)
                client_socket.close()
                return

def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(5)
    print(f"Serving HTTP on port {PORT} ...")
    while True:
        client_socket, client_address = listen_socket.accept()
        handle_request(client_socket)

if __name__ == '__main__':
    serve_forever()
