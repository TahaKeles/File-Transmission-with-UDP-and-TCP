from threading import Thread
from time import time
import hashlib
from socket import *
import struct
import sys
import select
interfaces={
    "34": {"host":"10.10.7.1","port":10034},
    "43": {"host":"10.10.7.2","port":10043},
    "24": {"host":"10.10.5.2","port":10024},
    "42": {"host":"10.10.5.1","port":10042},
    "14": {"host":"10.10.4.2","port":10014},
    "41": {"host":"10.10.4.1","port":10041},
}

server3 = socket(AF_INET,SOCK_DGRAM)
server2 = socket(AF_INET,SOCK_DGRAM)
server1 = socket(AF_INET,SOCK_DGRAM)
client3 = socket(AF_INET,SOCK_DGRAM)
client2 = socket(AF_INET,SOCK_DGRAM)
client1 = socket(AF_INET,SOCK_DGRAM)
server3.bind(("0.0.0.0",interfaces['34']['port']))
server2.bind(("0.0.0.0",interfaces['24']['port']))
server1.bind(("0.0.0.0",interfaces['14']['port']))
addrForClient3 = (interfaces['43']['host'],interfaces['43']['port'])
addrForClient2 = (interfaces['42']['host'],interfaces['42']['port'])
addrForClient1 = (interfaces['41']['host'],interfaces['41']['port'])

buf=1024

isR1R2Working = True
isR3Working = True
gThreads  = []
timesRoman12 = []
timesRoman3 = []

def md51(d):
    return hashlib.md5(d).hexdigest()

output1={}
output2={}

def handleData3(data):
    cs = struct.unpack("32s",data[:32])[0]
    i = struct.unpack("i",data[32:36])[0]
    l = struct.unpack("i",data[36:40])[0]
    d = struct.unpack(str(l)+"s",data[40:40+l])[0]
    print(str(i)+". data come from "+str(addrForClient3))
    if md51(d).encode()==cs:
        output1[i] = d
        client3.sendto(data[32:36],addrForClient3)

def handleData2(data):
    cs = struct.unpack("32s",data[:32])[0]
    i = struct.unpack("i",data[32:36])[0]
    l = struct.unpack("i",data[36:40])[0]
    d = struct.unpack(str(l)+"s",data[40:40+l])[0]
    print(str(i)+". data come from "+str(addrForClient2))
    if md51(d).encode()==cs:
        output2[i] = d
        client2.sendto(data[32:36],addrForClient2)

def handleData1(data):
    cs = struct.unpack("32s",data[:32])[0]
    i = struct.unpack("i",data[32:36])[0]
    l = struct.unpack("i",data[36:40])[0]
    d = struct.unpack(str(l)+"s",data[40:40+l])[0]
    print(str(i)+". data come from "+str(addrForClient1))
    if md51(d).encode()==cs:
        output2[i] = d
        client1.sendto(data[32:36],addrForClient1)

def inputFromR3():
    global isR1R2Working,isR3Working
    isR3Working = True
    threads = []
    server3.settimeout(None)
    data,addr = server3.recvfrom(buf)
    startTime = time()
    server3.settimeout(2)
    while data and isR3Working:
        t3 = Thread(target=handleData3, args=[data])
        threads.append(t3)
        t3.start()
        try:
            data,addr = server3.recvfrom(buf)
            if struct.unpack("i",data[32:36])[0]==-1:
                endTime = time()
                timesRoman3.append(str(endTime-startTime))
                isR3Working=False
                client3.sendto(data[32:36],addrForClient3)
                break
        except Exception as ass:
            print(ass)
            pass
    isR3Working = False

    for t in threads:
        t.join()

def inputFromR2():
    global isR1R2Working,isR3Working
    isR1R2Working = True
    threads = []
    server1.settimeout(None)
    data,addr = server2.recvfrom(buf)
    startTime = time()
    server2.settimeout(2)
    while data and isR1R2Working:
        t2 = Thread(target=handleData2, args=[data])
        threads.append(t2)
        t2.start()
        try:
            data,addr = server2.recvfrom(buf)
            if struct.unpack("i",data[32:36])[0]==-1:
                endTime = time()
                timesRoman12.append(str(endTime-startTime))
                isR1R2Working = False
                client1.sendto(data[32:36],addrForClient1)
                client2.sendto(data[32:36],addrForClient2)
                break
        except Exception as ass:
            print(ass)
            pass
    isR1R2Working = False

    for t in threads:
        t.join()

def inputFromR1():
    global isR1R2Working,isR3Working
    isR1R2Working = True
    threads = []
    server1.settimeout(None)
    data,addr = server1.recvfrom(buf)
    startTime = time()
    server1.settimeout(2)
    while data and isR1R2Working:
        t1 = Thread(target=handleData1, args=[data])
        threads.append(t1)
        t1.start()
        try:
            data,addr = server1.recvfrom(buf)
            if struct.unpack("i",data[32:36])[0]==-1:
                endTime = time()
                timesRoman12.append(str(endTime-startTime))
                isR1R2Working = False
                client1.sendto(data[32:36],addrForClient1)
                client2.sendto(data[32:36],addrForClient1)
                break
        except Exception as ass:
            print(ass)
            pass
    isR1R2Working = False

    for t in threads:
        t.join()

def startThreads():
    global isR1R2Working,isR3Working
    global gThreads
    isR1R2Working = True
    isR3Working = True
    tInputFromR3 = Thread(target=inputFromR3)
    gThreads.append(tInputFromR3)
    tInputFromR3.start()

    tInputFromR2 = Thread(target=inputFromR2)
    gThreads.append(tInputFromR2)
    tInputFromR2.start()

    tInputFromR1 = Thread(target=inputFromR1)
    gThreads.append(tInputFromR1)
    tInputFromR1.start()
    while True:
        if (not isR1R2Working) and  (not isR3Working):
            print("joint")
            joinThreads()
            break
        else:
            pass

def joinThreads():
    global gThreads
    foutput1 = open("output1.txt",'wb')
    keyLength = len(output1.keys())
    for i in range(keyLength):
        foutput1.write(output1[i])
    foutput1.close()

    foutput2 = open("output2.txt",'wb')
    keyLength = len(output2.keys())
    for i in range(keyLength):
        foutput2.write(output2[i])
    foutput2.close()

    isR1R2Working = False
    isR3Working = False
    for t in gThreads:
        t.join()

if __name__ == '__main__':
    startThreads()
    server3.close()
    client3.close()
    server2.close()
    client2.close()
    server1.close()
    client1.close()
    foutput3 = open("timesRoman3.txt",'a')
    for i in timesRoman3:
        foutput3.write(i)
        foutput3.write("\n")
    foutput3.close()
    foutput12 = open("timesRoman12.txt",'a')
    for i in timesRoman12:
        foutput12.write(i)
        foutput12.write("\n")
    foutput12.close()
    print ("File Downloaded")
