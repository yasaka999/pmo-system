# -*- encoding=utf-8

import struct

# header = {

#   "flag":{}

# }

# header['ke'] = 'va'

# header['flag']['ka'] = 'va'


class A:

    def __init__(cls, packet):

        cls.packet = packet

    def getPacket(cls):

        return cls.packet


print(A('hello,world').getPacket())

#八个字节

bin_str = b'ABCD1234'

print(bin_str)

# 输出ascii值

result = struct.unpack('>BBBBBBBB', bin_str)

print(result)

result = struct.unpack('>HHHH', bin_str)

print(result)

result = struct.unpack('>LL', bin_str)

print(result)

result = struct.unpack('>8s', bin_str)

print(result)

result = struct.unpack('>BBHL', bin_str)

print(result)
