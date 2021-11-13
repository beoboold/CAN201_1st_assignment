import gzip
import os
import socket
from socket import *
from tqdm import *

port = 20000
buffer_size = 1024

def main():
    serverSoc = socket(AF_INET, SOCK_STREAM)
    serverSoc.bind(("",port))
    serverSoc.listen()
    print("Listening...")

    connectSoc, clientAddr = serverSoc.accept()
    print("Client connected from ",clientAddr)

    recv_data = connectSoc.recv(buffer_size).decode()
    item = recv_data.split("/")
    filename = item[0]
    filesize = int(item[1])

    print("File information received.")
    connectSoc.send("File information received".encode())

    bar = tqdm(range(filesize), ('Receiving '+filename), unit="B", unit_scale=True, unit_divisor=buffer_size)
    #f"Receiving {filename}"

    with open("recv_"+filename+'.gz', 'wb') as fid:
        while True:
            recv_Bdata = connectSoc.recv(buffer_size)

            if not recv_Bdata:
                break

            fid.write(recv_Bdata)
            #connectSoc.send("Data received".encode())

            bar.update(len(recv_Bdata))
        print('Finish file transfer')

    with gzip.open("recv_"+filename+'.gz', 'rb') as fid:
        read_data = fid.read()
        with open("recv_"+filename, 'wb') as f:
            f.write(read_data)
    connectSoc.close()
    os.remove("recv_" + filename + '.gz')
    serverSoc.close()

if __name__ == "__main__":
    main()

