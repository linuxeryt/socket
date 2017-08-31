#!/usr/bin/env python3
# coding: utf-8

import socket
import concurrent.futures


class Server:
    def __init__(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(address)
        self.sock.listen(5)
        print('Server {} listen on {}'.format(*address))
        self.connection()
        
    def connection(self):
        '''accept connection
        accetp() 不会阻塞
        '''
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
            while True:
                conn, addr = self.sock.accept()
                print('Connection from', addr)
                # 返回Future 实例
                self.future = executor.submit(self.read, conn)

                # 执行完read()后才会执行下面语句
                print('future result is: ', self.future.result())
                conn.close()

    def read(self, conn):
        print('fadfas')
        # 此处的 recv会被阻塞
        data = conn.recv(1024)
        print(data)
        return data     # 返回给future


if __name__ == '__main__':
    HOST, PORT = '', 8080
    address = (HOST, PORT)
    server = Server(address)
