from socket import *

def send_msg(s:socket, msg:str):
    msg_bytes = msg.encode('utf-8')
    s.send(msg_bytes)