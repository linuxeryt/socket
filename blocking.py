#!/usr/bin/env python
# coding: utf-8

'''
版本: 1.0
功能: 阻塞型IO
Python 版本: Python3.6
'''

import socket

HOST, PORT = '', 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)
sock.setblocking(0)
print('Server {} listen on {}'.format(HOST, PORT))

while True:
    '''接收多个TCP连接。但是需要前一个连接处理完才能接收下一个连接
    '''
    conn, addr = sock.accept()
    conn.setblocking(0)
    print('Connection from ', addr)

    while True:
        '''同一连接多次数据交互；收到exit则退出关闭当前连接
        '''
        data = conn.recv(1024)
        print(addr, 'send data:', data)
        if data == b'\r\n':
            '''data is '\r\n'
            '''
            conn.sendall(b'Send content can not null.\r\n')
        elif data == b'exit\r\n':
            break
        else:
            conn.sendall(data)
conn.close()
