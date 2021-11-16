import gzip
import os
import socket
from socket import *
from tqdm import *
import json
import argparse

#os.path.abspath
#os.path.join
#Create transferFile def
#port = 20000
buffer_size = 20480

def _argparse():
    parser = argparse.ArgumentParser(description="A")
    parser.add_argument('--port', action='store',required=True, dest='port', help='port')

    return parser.parse_args()

def main():
    parser = _argparse()
    port = int(parser.port)

    server_port = port
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', server_port))
    server_socket.listen()

    #serverSoc = socket(AF_INET, SOCK_STREAM)
    #serverSoc.bind(("",port))
    #serverSoc.listen()
    #print("Listening...")

    connectSoc, clientAddr = server_socket.accept()
    print("Client connected from ",clientAddr)

    recv_data = connectSoc.recv(buffer_size).decode()
    item = recv_data.split("@")
    filename = item[0]
    filesize = int(item[1])
    filepath = item[2]

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

    with gzip.open(filepath+"recv_"+filename+'.gz', 'rb') as fid:
        read_data = fid.read()
        with open(filepath+"recv_"+filename, 'wb') as f:
            f.write(read_data)
    os.remove(filepath+"recv_" + filename + '.gz')

if __name__ == "__main__":
    main()

