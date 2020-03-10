from socket import *
from threading import Thread

interfaces={
    "03": {"host":"10.10.3.2","port":10003},
    "34": {"host":"10.10.7.1","port":10034},
    "43": {"host":"10.10.7.2","port":10043},
    "30": {"host":"10.10.3.1","port":10030}
}




def r04():
    host="0.0.0.0"
    port = 10003
    s = socket(AF_INET,SOCK_DGRAM)
    s1 = socket(AF_INET,SOCK_DGRAM)

    s.bind((host,port))

    buf=1024
    addr1=(interfaces['34']['host'],interfaces['34']['port'])
    while True:
        data,addr = s.recvfrom(buf)
        s1.sendto(data,addr1)
        if not data:
            break
    
    s1.close()
    s.close()
    
def r40():
    host="0.0.0.0"
    port = 10043
    s = socket(AF_INET,SOCK_DGRAM)
    s1 = socket(AF_INET,SOCK_DGRAM)

    s.bind((host,port))

    buf=1024
    addr1=(interfaces['30']['host'],interfaces['30']['port'])
    while True:
        data,addr = s.recvfrom(buf)
        s1.sendto(data,addr1)
        if (not data):
            break
    
    s.close()
    s1.close()

if __name__ == '__main__':
    t1 = Thread(target=r04)
    t2 = Thread(target=r40)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
