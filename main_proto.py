import gzip
import multiprocessing
import os
import sys
import threading
import time
from socket import *
from tqdm import *
from threading import *
from multiprocessing import *
import json
import argparse

port = 20000
buffer_size = 1024
filename = ''
folderpath = os.path.abspath("share")

def _argparse():
    parser = argparse.ArgumentParser(description="A")
    parser.add_argument('--ip', action='store', required=True, dest='ip', help='ip address')
    return parser.parse_args()

def server_side():
    server_port = port
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)#Kill occupied process to run other process
    server_socket.bind(('', server_port))
    server_socket.listen()
    print('Server is listening...')
    filelist = os.listdir(folderpath)
    c_filelist = []
    while True:
        connectSoc, clientAddr = server_socket.accept()
        print("S: Client connected from ", clientAddr)
        connectSoc.send('Connected'.encode())#Welcome msg
        recv_num = connectSoc.recv(buffer_size).decode()
        listquantity = int(recv_num)
        for i in range(0,listquantity):
            list_data = connectSoc.recv(buffer_size).decode()#Get file list from client
            if list_data:
                c_filelist.append(list_data)
                print(f'Get list data from client {c_filelist}')
        filelist.sort()
        c_filelist.sort()
        print(filelist)
        print(c_filelist)
        if filelist == c_filelist:#If filelists are same wait leave it
            connectSoc.send('M@Syn well'.encode())
        else:#Else doing file transmission
            connectSoc.send('U@Need file transmission'.encode())
        recv_msg = connectSoc.recv(buffer_size).decode()
        print(f'{recv_msg}-line 53')
        item = recv_msg.split('@')
        if 'F' in item[0]:
            filenumber = int(item[1])
            for i in range(0,filenumber):
                recv_data = connectSoc.recv(buffer_size).decode()#Get file information for bar process
                item = recv_data.split('@')
                filename = item[0]
                filesize = int(item[1])
                filepath = os.path.join(folderpath, filename)

                bar = tqdm(range(filesize), ('Receiving ' + filename), unit="B", unit_scale=True, unit_divisor=buffer_size)

                with open(filepath, 'wb') as fid:#Get actual file data and write in share folder
                    while True:
                        recv_Bdata = connectSoc.recv(buffer_size)
                        if not recv_Bdata:
                            break
                        fid.write(recv_Bdata)
                        bar.update(len(recv_Bdata))
                    print(f'Received file transfer filename: {filename}')

def client_side():
    print('Client start running')
    parser = _argparse()#Get server ip
    ip = parser.ip
    server_ip = ip
    server_port = port

    client = socket(AF_INET, SOCK_STREAM)
    client.connect((server_ip, server_port))
    print(f'Client trying to connect with {server_ip}, {server_port}')

    welcome_msg = client.recv(buffer_size).decode()#Welcome msg from server
    print(f'From server : {welcome_msg}')
    filelist = os.listdir(folderpath)
    filequantity = len(filelist)
    if len(filelist) >= 1:#If file exist send data to server to compare
        client.send(str(filequantity).encode())
        for i in range(0,len(filelist)):#Looping and sending filenames to make file list
            print('Sending filelist')
            filename = filelist[i]
            client.send(filename.encode())
    else:#Else wait until new file exist
        print("Share folder has no data")
    list_result = client.recv(buffer_size).decode() #Get comparison result from the server
    item = list_result.split('@')
    if 'M' in item[0]:#If result matches, leave it
        print(item[1])
    elif 'U' in item[0]:#Else when unmathes start transmission process
        print(f'Server : {item[1]}')
        client.send(f'F@{len(filelist)}'.encode())#Send quantity of files
        for i in range(0,len(filelist)):#Send fileinfo and data
            filename = filelist[i]
            filepath = os.path.join(folderpath, filename)
            filesize = os.path.getsize(filepath)
            datainfo = (f'{filename}@{filesize}')#Send file information
            client.send(datainfo.encode())
            print(f'Client sent file information of {filename}')

            bar = tqdm(range(filesize), ('Sending ' + filename), unit="B", unit_scale=True, unit_divisor=buffer_size)
            print(f'Sending {filename} data')

            with open(filepath, 'rb') as fid:#Send actual file data
                while True:
                    bData = fid.read(buffer_size)
                    if not bData:
                        break
                    client.send(bData)
                    bar.update(len(bData))
            client.close()
            print(f'{filename} sent')

def main():#Using multiprocessing run two servers and client
        s = multiprocessing.Process(target=server_side)
        c = multiprocessing.Process(target=client_side)

        s.start()
        time.sleep(3)
        c.start()

if __name__ == "__main__":
    main()