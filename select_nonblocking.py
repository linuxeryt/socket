#!/usr/bin/env python
# coding: utf-8

'''
Python version: 2
function:  socket non-blockging IO
'''

import sys
import Queue
import socket
import select
import json

HOST, PORT = '', 8080


def handle_request(conn):
    ''' handle data recv and send
    '''
    data = conn.recv(1024)
    print('recive data: ', data)

    response = b'hello'
    conn.sendall(response)


def forever_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'sock type is', type(sock)
    sock.setblocking(False)
    sock.bind((HOST, PORT))
    sock.listen(5)
    readlist = [sock]
    writelist = []
    message_queues = {}
    
    while readlist:
        #for i in readlist:
        #    print '{} --- {}'.format(i, i.fileno())

        readable, writeable, exceptional = select.select(
            readlist, writelist, readlist
        )

        for s in readable:
            if s is sock:
                '''s是监听套接字对象，则调用accept()。
                readable 中的第一个文件描述符是监听套接字描述符
                '''

                conn, addr = sock.accept()  # accept()会返回一个全新的描述符.这个描述符为 已连接套接字描述符
                print 'accept from', addr
                conn.setblocking(0)
                readlist.append(conn)
                message_queues[conn] = Queue.Queue()
            else:   
                # s 是已连接套接字描述符，则调用 recv()从内核缓冲区中获取数据.
                data = s.recv(1024)
                response = 'Hello Wrold\r\n'

                if data != b'exit\r\n':     #使用telnet工具发送数据，传输的为二进制
                    print "Recieved data: {}  from {}".format(data, addr)
                    # 将发送数据存入队列
                    message_queues[s].put(response)

                    # 某个已连接套接字描述符已经接收数据，可以调用send()，则放入 writelist中
                    if s not in writelist:
                        writelist.append(s)
                else:
                    if s in writelist:
                        writelist.remove(s)
                    readlist.remove(s)
                    s.close()
                    del message_queues[s]

        for s in writeable:
            try:
                #next_msg = message_queues[s].get_nowait()
                next_msg = message_queues[s].get(block=False)
            except Queue.Empty:
                writelist.remove(s)
            else:
                s.send(next_msg)

        for s in exceptional:
            readlist.remove(s)
            if s in writelist:
                writelist.remove(s)
            s.close()
            del message_queues[s]

if __name__ == '__main__':
    print('Server listen on ', PORT)
    forever_server()
