# -*- encoding=utf-8

import socket, json

import os, sys

# 配置工作路径为上一级目录

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))

from os.pool import ThreadPool as tp

from os.task import AsyncTask

from computer_network.processor.parser import IPParser

from computer_network.processor.trans import UDPParser, TCPParser


class ProcessTask(AsyncTask):

    def __init__(self, packet, *args, **kwargs):

        self.packet = packet

        # 调用父类的方法

        super(ProcessTask, self).__init__(func=self.process, *args, **kwargs)

    def process(self):

        # UDP报文解析测试

        headers = {'network_header': None, 'transport_header': None}

        ip_header = IPParser.parse(self.packet)

        headers['network_header'] = ip_header

        # 判断是否是TCP协议

        if ip_header['protocol'] == 6:

            headers['transport_header'] = TCPParser.parse(self.packet)

        # 判断是否是UDP协议

        elif ip_header['protocol'] == 17:

            headers['transport_header'] = UDPParser.parse(self.packet)

        return headers


class Server:

    def __init__(self):

        # 工作自协议类型、套接字类型、工作具体的协议

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                  socket.IPPROTO_IP)

        self.ip = '192.168.5.141'

        self.port = 8888

        self.sock.bind((self.ip, self.port))

        # 设置混杂模式

        self.sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

        # 新建线程池

        self.pool = tp(10)

        self.pool.start()

    def loop_serve(self):

        while True:

            # 1、接受

            packet, addr = self.sock.recvfrom(65535)

            # 2、生成Task

            task = ProcessTask(packet)

            # 3、提交

            self.pool.put(task)

            # 4、获取

            result = task.get_result()

            # 对数据显示进行缩进

            result = json.dumps(result, indent=4)

            print(result)


if __name__ == '__main__':

    server = Server()

    server.loop_serve()
