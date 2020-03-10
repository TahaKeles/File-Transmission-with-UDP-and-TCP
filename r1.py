from socket import *
from threading import Thread

interfaces={
    "01": {"host":"10.10.1.2","port":10001},
    "14": {"host":"10.10.4.2","port":10014},
    "41": {"host":"10.10.4.1","port":10041},
    "10": {"host":"10.10.1.1","port":10010}
}




def r04():
    host="0.0.0.0"
    port = 10001
    s = socket(AF_INET,SOCK_DGRAM)
    s1 = socket(AF_INET,SOCK_DGRAM)

    s.bind((host,port))

    buf=1024
    addr1=(interfaces['14']['host'],interfaces['14']['port'])
    while True:
        data,addr = s.recvfrom(buf)
        s1.sendto(data,addr1)
        if (not data):
            break

def r40():
    host="0.0.0.0"
    port = 10041
    s = socket(AF_INET,SOCK_DGRAM)
    s1 = socket(AF_INET,SOCK_DGRAM)

    s.bind((host,port))

    buf=1024
    addr1=(interfaces['10']['host'],interfaces['10']['port'])
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
