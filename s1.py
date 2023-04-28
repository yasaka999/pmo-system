import http.server
import socketserver

class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
        # 获取POST请求的长度
        content_length = int(self.headers['Content-Length'])
        # 读取POST请求内容
        post_data = self.rfile.read(content_length)
        # 打印POST请求内容
        print(post_data.decode('utf-8'))

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'OK')

PORT = 8080

Handler = MyHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()
