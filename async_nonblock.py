#!/usr/bin/env python3
# coding: utf-8

'''
版本: 1.0
功能: 异步非阻塞IO
Python 版本: Python3.6
'''

import sys
import socket
import selectors
from selectors import EVENT_READ, EVENT_WRITE

# 创建selector对象，监视文件描述符
selector = selectors.DefaultSelector()


class Server(object):
    def __init__(self, address):
        # 创建监听描述符
        address = address
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(address)
        server.listen(5)
        server.setblocking(False)

        # 注册读事件 
        # data=self.connection 表示将connection方法绑定至data参数
        # 返回SelectorKey实例
        a = selector.register(
            fileobj=server,
            events=EVENT_READ,
            data=self.connection)

        print('EVENT_READ of accept', a)

    def connection(self, server, mask):
        conn, addr = server.accept()   
        print('Conncetion: ', conn, 'from', addr)
        print()
        conn.setblocking(False)
        b = selector.register(fileobj=conn, 
            events=EVENT_READ, 
            data=self.handle_request
        )

        print('EVENT_READ of recv', b)

    def handle_request(self, conn, mask):
        data = conn.recv(1024)
        print(data)
        if data == '\r\n':
            print('Data can not is null. closing', conn)
            selector.unregister(conn)
            conn.close()
        elif data == b'exit\r\n':
            print('closing', conn)
            
            # 关闭TCP连接前需取消事件注册
            selector.unregister(conn)
            conn.close()
        else:
            print('Recived data: %s from', conn)
            response = b'hello\r\n'
            conn.sendall(response)

    def send_data(self, conn):
        print('Recived data: %s from', conn)
        response = b'hello\r\n'
        conn.sendall(response)
        selector.unregister(conn)
        conn.close()

            
def loop():
    ''' 事件循环
    '''
    while True:
        # 等待已注册事件进入就绪状态
        # select()返回(key, events)元组
        # key 是一个已就绪文件对象的SelectorKey实例
        # events 是这个文件对象上准备好的事件位掩码
        events = selector.select(1)
        print('Events is ----> ', events)
        for key, mask in events:
            # 回调：对于每个事件，发送到其对应的处理函数
            callback = key.data
            callback(key.fileobj, mask)
            
if __name__ == '__main__':
    address = ('', 8080)
    server = Server(address)
    loop()
