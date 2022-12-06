import scapy.all
from scapy.layers.inet import *
from scapy.all import *

#pkt = IP(src="192.168.200.140",dst="192.168.200.1",ttl=22,options=[("MSS",123)])
#ls(pkt)

#pkt2 = IP()/TCP()/"GET HTTP/1.0\r\n\r\n"
#ls(pkt2)

pkt = IP(src='192.168.5.145', dst='192.168.5.183')/TCP(sport=12345,dport=80,options=[('MSS',14)])

send(pkt, inter=1, count=1)