import socket
import datetime

UDP_IP = "172.30.0.83"
UDP_PORT = 5005
MESSAGE = "start"

print(datetime.datetime.now())

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
