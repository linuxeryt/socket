#!/usr/bin/env python
# coding: utf-8

import socket
import StringIO
import sys

class WSGIServer(object):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):
        # 创建监听socket
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )

        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        listen_socket.bind(server_address)
        listen_socket.listen(self.request_queue_size)
    
        # 获取服务器主机名和端口
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

        self.headers_set = []

    def set_app(self, application):
        '''设置 网络应用程序, 如Flask的
        '''
        self.application = application

    def server_forever(self):
        '''无限循环，接收客户端请求
        '''
        listen_socket = self.listen_socket
        while True:
            self.client_connection, client_address = listen_socket.accept()
            self.handle_one_request()

    def handle_one_request(self):
        '''处理请求
        '''
        # "GET /hello HTTP/1.1\r\nUser-Agent: curl/7.29.0\r\nHost: 118.89.28.185:8888\r\nAccept: */*\r\n\r\n"
        self.request_data = request_data = self.client_connection.recv(1024)
        print 'Reuest:'
        print(''.join(
            '< {line}\n'.format(line=line)
            for line in request_data.splitlines()
        ))

        self.parse_request(request_data)

        # 使用请求数据构造环境变量
        env = self.get_environ()

        # 调用应用程序(如Flask的)，并获取HTTP响应体。
        # 根据WSGI，application 对象是一个可调用对象并且只接收两个参数
        # env 是环境变量，数据由来自客户端的请求提供
        # start_response是一个回调函数，由Server提供, HTTP status 和 HTTP headers是start_response()的参数
        body = self.application(env, self.start_response) 
        self.finish_response(body)

    def parse_request(self, text):
        '''解析HTTP 请求，获取头部信息
        '''
        import json
        #print json.dumps(text)
        request_line = text.splitlines()[0]     # 获取HTTP头部： 'GET /hello HTTP/1.1'
        request_line = request_line.rstrip('\r\n')

        (self.request_method,
         self.path,
         self.request_version
        ) = request_line.split()

    def get_environ(self):
        '''使用请求 数据构造 env字典
        字典内容遵循 WSGI规范（PEP333）
        '''
        env = {}

        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_code'] = False

        env['REQUEST_METHOD'] = self.request_method
        env['PATH_INFO'] = self.path
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = str(self.server_port)

        return env

    def start_response(self, status, response_headers, exc_info=None):
        '''该函数就是上面提到的 回调函数
        '''
        server_headers = [
            ('DATE', 'Tue, 31 Mar 2015 12:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]

        self.headers_set = [status, response_headers + server_headers]

    def finish_response(self, body):
        '''给客户端返回结果
        '''
        try:
            status, response_headers = self.headers_set
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)

            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\nCotent: {body}\r\n'.format(body=body[0])
            print 'Response:'
            print(''.join(
                '> {line}\n'.format(line=line)
                for line in response.splitlines()
            ))
            self.client_connection.sendall(response)
        finally:
            self.client_connection.close()

SERVER_ADDRESS = (HOST, PORT) = '', 8888

def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)

    return server

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')

    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)

    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.server_forever()
