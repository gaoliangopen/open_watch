import socket 
import _thread 
import json
import array
sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #连接
sock_tcp.connect(("192.168.1.110",60000)) #填写对应端口号
l = ["aaaa","bbbbb","ccc","eeee"]
l = json.dumps(l) #转换成字符串
sock_tcp.sendall(bytes(l, "utf-8")) #发送数据
