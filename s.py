import hashlib
from socket import *
import struct
import sys
from threading import Thread,Lock

LOCK = Lock()
TIMEOUT = 4000

interfaces = {
    "03": {"host": "10.10.3.2", "port": 10003},
    "30": {"host": "10.10.3.1", "port": 10030},
    "01": {"host": "10.10.1.2", "port": 10001},
    "10": {"host": "10.10.1.1", "port": 10010},
    "20": {"host": "10.10.2.2", "port": 10020},
    "02": {"host": "10.10.2.1", "port": 10002}
}


s03 = socket(AF_INET, SOCK_DGRAM)
s1 = socket(AF_INET, SOCK_DGRAM)
s2 = socket(AF_INET, SOCK_DGRAM)
s3 = socket(AF_INET, SOCK_DGRAM)
s01 = socket(AF_INET, SOCK_DGRAM)
s02 = socket(AF_INET, SOCK_DGRAM)
s1.settimeout(TIMEOUT/1000)
s2.settimeout(TIMEOUT/1000)
s3.settimeout(TIMEOUT/1000)

seqnumber = 0
buf = 984
addr1 = (interfaces['01']['host'], interfaces['01']['port'])
addr2 = (interfaces['02']['host'], interfaces['02']['port'])
addr3 = (interfaces['03']['host'], interfaces['03']['port'])

datas = []
s3.bind(("", 10030))
s2.bind(("", 10020))
s1.bind(("", 10010))
file_name = sys.argv[1]


SOCKETS = [True,True]

def md5(d):
    return hashlib.md5(d).hexdigest()




def sendR1(data,index):
    s01.sendto(data,addr1)
    try:
        ack = s1.recv(buf)
        if not ack:
            return
        ack = struct.unpack("i", ack[0:4])[0]
        if ack == index:
            LOCK.acquire()
            SOCKETS[0] = True
            LOCK.release()
    except Exception as err:
        sendR1(data,index)


def sendR2(data, index):
    s02.sendto(data, addr2)

    try:
        ack = s2.recv(buf)
        if not ack:
            return
        ack = struct.unpack("i", ack[0:4])[0]
        if ack == index:
            LOCK.acquire()
            SOCKETS[1] = True
            LOCK.release()
    except:
        sendR2(data, index)

def sendR3(data, index):
    s03.sendto(data, addr3)

    try:
        ack = s3.recv(buf)
        if not ack:
            return
        ack = struct.unpack("i", ack[0:4])[0]
        if ack == index:
             return
    except:
        sendR3(data, index)

def R1R2(filename):
    fp = open(filename,"rb")
    index = 0
    t1 = None
    t2 = None
    data = fp.read(buf)
    while data:
        packetseqnumber = struct.pack("i", index)
        datatosent = struct.pack("{}s".format(len(data)), data)
        packetlength = struct.pack("i", len(data))
        datachecksum = struct.pack("32s", md5(data).encode())
        data = datachecksum + packetseqnumber + packetlength + datatosent
        while not (True in SOCKETS):
            pass
        if SOCKETS[0]:
            LOCK.acquire()
            SOCKETS[0] = False
            LOCK.release()
            if datatosent:
                ddd = data
            else:
                ddd = "-1".encode()
            t1 = Thread(target=sendR1,args=(ddd,index))
            t1.start()
            if t2:
                t2.join()
                t2 = None
        elif SOCKETS[1]:
            LOCK.acquire()
            SOCKETS[1] = False
            LOCK.release()
            if datatosent:
                ddd = data
            else:
                ddd = "-1".encode()
            t2 = Thread(target=sendR2,args=(ddd,index))
            t2.start()
            if t1:
                t1.join()
                t1 = None
        index += 1
        data = fp.read(buf)
    packetseqnumber = struct.pack("i", -1)
    datatosent = struct.pack("984s", data)
    packetlength = struct.pack("i", len(data))
    datachecksum = struct.pack("32s", md5(data).encode())
    data = datachecksum + packetseqnumber + packetlength + datatosent
    while not SOCKETS[0]:
        ...

    sendR1(data, index)

    fp.close()


def R3(filename):

    fp = open(filename,"rb")
    index = 0
    data = fp.read(buf)
    while data != b'':
        packetseqnumber = struct.pack("i", index)
        datatosent = struct.pack("1024s", data)
        packetlength = struct.pack("i", len(data))
        datachecksum = struct.pack("32s", md5(data).encode())
        data = datachecksum + packetseqnumber + packetlength + datatosent
        sendR3(data,index)
        index += 1
        data = fp.read(buf)
    packetseqnumber = struct.pack("i", -1)
    datatosent = struct.pack("1024s", data)
    packetlength = struct.pack("i", len(data))
    datachecksum = struct.pack("32s", md5(data).encode())
    data = datachecksum + packetseqnumber + packetlength + datatosent
    sendR3(data, index)
    fp.close()


def main(numberOfExperiments=1):
    firstFilename = sys.argv[1]
    secondFilename = sys.argv[2]
    for i in range(numberOfExperiments):
        t1 = Thread(target=R1R2,args=(firstFilename,))
        t2 = Thread(target=R3,args=(secondFilename,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()


if __name__ == "__main__":

    main()

