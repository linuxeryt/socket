#!/usr/bin/env python3
# coding: utf-8

'''
异步非阻塞
'''

import sys
import socket
import selectors
from selectors import EVENT_READ, EVENT_WRITE

selector = selectors.DefaultSelector()

class Server(object):
    def __init__(self, address):
        address = address
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server.bind(address)
        server.listen(5)
        server.setblocking(False)

        selector.register(server, EVENT_READ, self.accept)  #返回SelectorKey实例。

    def accept(self, server, mask):
        conn, addr = server.accept()   
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        selector.register(conn, EVENT_READ, self.handle_request)

    def handle_request(self, conn, mask):
        data = conn.recv(1024)
        if data:
            print('echoing', repr(data), 'to', conn)
            response = b'hello'
            conn.sendall(response)
        else:
            print('closing', conn)
            selector.unregister(conn)
            conn.close()

def loop():
    while True:
        events = selector.select()

        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)

if __name__ == '__main__':
    address = ('', int(sys.argv[1]))
    server = Server(address)
    loop()
