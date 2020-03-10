from socket import *
from threading import Thread
interfaces = {
    "02": {"host": "10.10.2.1", "port": 10002},
    "24": {"host": "10.10.5.2", "port": 10024},
    "42": {"host": "10.10.5.1", "port": 10042},
    "20": {"host": "10.10.2.2", "port": 10020}
}



def r04():
    host="0.0.0.0"
    port = 10002
    s = socket(AF_INET,SOCK_DGRAM)
    s1 = socket(AF_INET,SOCK_DGRAM)

    s.bind((host,port))

    buf=1024
    addr1=(interfaces['24']['host'],interfaces['24']['port'])
    while True:
        data,addr = s.recvfrom(buf)
        s1.sendto(data,addr1)
        if (not data):
            break

def r40():
    host="0.0.0.0"
    port = 10042
    s = socket(AF_INET,SOCK_DGRAM)
    s1 = socket(AF_INET,SOCK_DGRAM)

    s.bind((host,port))

    buf=1024
    addr1=(interfaces['20']['host'],interfaces['20']['port'])
    while True:
        data,addr = s.recvfrom(buf)
        s1.sendto(data,addr1)
        if (not data):
            break

if __name__ == '__main__':
    t1 = Thread(target=r04)
    t2 = Thread(target=r40)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
