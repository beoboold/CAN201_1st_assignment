import gzip
import multiprocessing
import os
import sys
import threading
import time
from socket import *
from tqdm import *
import argparse

#D=actual data transfer/M= list match/S=Server has data client has not/C=Client has data server has not

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
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Kill occupied process to run other process
    server_socket.bind(('', server_port))
    server_socket.listen()
    print('Server is listening...')
    while True:
        filelist = os.listdir(folderpath)
        print(f'Server filelist = {filelist}')
        c_filelist = []
        connectSoc, clientAddr = server_socket.accept()
        print("S: Client connected from ", clientAddr)
        connectSoc.send('Connected'.encode())  # Welcome msg
        recv_num = connectSoc.recv(buffer_size).decode()
        print(f'recv_num= {recv_num}')
        listquantity = int(recv_num)
        if listquantity > 0 :
            connectSoc.send('ACK'.encode())
        else:
            connectSoc.send('NAK'.encode())
        for i in range(0, listquantity):
            list_data = connectSoc.recv(buffer_size).decode()  # Get file list from client
            if list_data:
                c_filelist.append(list_data)
                print(f'Get list data from {clientAddr} client {c_filelist}')
        filelist.sort()
        c_filelist.sort()
        print(filelist)
        print(f'{clientAddr},{c_filelist}')
        request_list = []


        if len(filelist) > len(c_filelist):#when server list len is bigger
            print('if 1 line 55')
            for i in range(0, len(filelist)):
                if not filelist[i] in c_filelist:
                    request_list.append(filelist[i])
        elif len(filelist) < len(c_filelist):#when client list len is bigger
            print('if 2 line 61')
            for i in range(0, len(c_filelist)):
                if not c_filelist[i] in filelist:
                    request_list.append(c_filelist[i])
        else:#When list len is same
            print('else line 67')
            if filelist == c_filelist:  # If filelists are same wait leave it
                connectSoc.send('M@Syn well'.encode())
            else:
                for i in range(0, len(filelist)):
                    for j in range(0, len(c_filelist)):
                        if not filelist[i] == c_filelist[j]:
                            request_list.append(c_filelist[j])

        print(f'request list = {request_list}')
        sendlist = []
        recvlist = []
        for i in range(0,len(request_list)):
            #filesearch = os.path.join(folderpath, request_list[i])
            if request_list[i] in filelist:#When server has file to send
                sendlist.append(request_list[i])
            if request_list[i] in c_filelist:#When client needs to send file
                recvlist.append(request_list[i])
        sendlist.sort()
        recvlist.sort()
        print(f'Sendlist = {sendlist}')
        print(f'Recvlist = {recvlist}')
        #send M=match, S=server will send, C=client will send
        if len(sendlist) >= 1:
            connectSoc.send('S@S: Server will send data'.encode())
            print('send S to the client')
        elif len(recvlist) >= 1:
            connectSoc.send('C@S: Client need to send data'.encode())
            print('send C to the client')

        recv_msg = connectSoc.recv(buffer_size).decode()
        item = recv_msg.split('@')
        if 'D' in item[0]:#Server receive data
            filenumber = int(item[1])
            connectSoc.send('ACK'.encode())
            for i in range(0, filenumber):
                recv_data = connectSoc.recv(buffer_size).decode()  # Get file information for bar process
                item = recv_data.split('@')
                filename = item[0]
                filesize = int(item[1])
                filepath = os.path.join(folderpath, filename)

                bar = tqdm(range(filesize), ('Receiving ' + filename), unit="B", unit_scale=True,unit_divisor=buffer_size)
                connectSoc.send('ACK'.encode())
                with open(filepath, 'wb') as fid:  # Get actual file data and write in share folder
                    while True:
                        recv_Bdata = connectSoc.recv(buffer_size)
                        if not recv_Bdata:
                            break
                        fid.write(recv_Bdata)
                        bar.update(len(recv_Bdata))
                    filelist = os.listdir(folderpath)#update filelist
                    print(f'Received file transfer filename: {filename}')
                    filelist.sort()
                    c_filelist.sort()
                    print(f'This is current files in folder {filelist}')
                    print(f'This is current client filelist {c_filelist}')
        elif 'R' in item[0]:#Server send data
            print(f'Client :{item[1]}')
            for i in range(0, len(sendlist)):
                print(f'Client: {item[1]}')
                connectSoc.send(f'D@{len(sendlist)}'.encode())
                response_msg = connectSoc.recv(buffer_size).decode()
                if 'ACK' in response_msg:
                    filename = sendlist[i]
                    getFsize = os.path.join(folderpath, filename)
                    filesize = os.path.getsize(getFsize)
                    print(f'File size is {filesize}')
                    connectSoc.send(f'{filename}@{filesize}'.encode())
                    bar = tqdm(range(filesize), ('Sending ' + filename), unit="B", unit_scale=True,unit_divisor=buffer_size)
                    response_msg = connectSoc.recv(buffer_size).decode()
                    if 'ACK' in response_msg:
                        with open(filepath, 'rb') as fid:
                            while True:
                                send_bData = fid.read(buffer_size)
                                if not send_bData:
                                    print('Done')
                                    break
                                connectSoc.send(send_bData)
                                bar.update(len(send_bData))
                            print(f'Server sent {filename}')
                            final_msg = connectSoc.recv(buffer_size).decode()
                            if 'ACK' in final_msg:
                                print(f'C: {final_msg}')
                            else:
                                print('need to send again')
                            ns_filelist = os.listdir(folderpath)
                            print(f'S: {ns_filelist}')


def client_side():
    print('Client start running')
    parser = _argparse()  # Get server ip
    ip = parser.ip
    server_ip = ip
    server_port = port
    while True:
        client = socket(AF_INET, SOCK_STREAM)
        client.connect((server_ip, server_port))

        print(f'Client trying to connect with {server_ip}, {server_port}')
        welcome_msg = client.recv(buffer_size).decode()  # Welcome msg from server
        print(f'From server : {welcome_msg}')

        filelist = os.listdir(folderpath)
        print(f'Client filelist = {filelist}')
        filequantity = len(filelist)
        print(f'client filequantity is {filequantity}')
        if filequantity >= 1:  # If file exist send data to server to compare
            client.send(str(filequantity).encode())
            recv_msg = client.recv(buffer_size).decode()
            if 'ACK' in recv_msg:
                for i in range(0, len(filelist)):  # Looping and sending filenames to make file list
                    print('Sending filelist')
                    filename = filelist[i]
                    client.send(filename.encode())
            elif 'NAK' in recv_msg:
                client.send(str(filequantity).encode())
        else:  # Else wait until new file exist
            print("Share folder has no data")
        list_result = client.recv(buffer_size).decode()  # Get comparison result from the server
        item = list_result.split('@')
        if 'M' in item[0]:  # If result matches, leave it
            print(item[1])
            time.sleep(1)
            client.close()
        elif 'C' in item[0]:  # Else when unmathes start transmission process
            print(f'Server : {item[1]}')
            client.send(f'D@{len(filelist)}'.encode())  # Send quantity of files
            recv_msg = client.recv(buffer_size).decode()
            if 'ACK' in recv_msg:
                for i in range(0, len(filelist)):  # Send fileinfo and data
                    filename = filelist[i]
                    filepath = os.path.join(folderpath, filename)
                    filesize = os.path.getsize(filepath)
                    datainfo = (f'{filename}@{filesize}')  # Send file information
                    client.send(datainfo.encode())
                    print(f'Client sent file information of {filename}')

                    bar = tqdm(range(filesize), ('Sending ' + filename), unit="B", unit_scale=True, unit_divisor=buffer_size)
                    print(f'Sending {filename} data')
                    recv_msg = client.recv(buffer_size).decode()
                    if 'ACK' in recv_msg:
                        with open(filepath, 'rb') as fid:  # Send actual file data
                            while True:
                                bData = fid.read(buffer_size)
                                if not bData:
                                    break
                                client.send(bData)
                                bar.update(len(bData))
                        client.close()
                        print(f'{filename} sent')
        elif 'S' in item[0]:#Server will give file(s)
            print(f'Server: {item[1]}')
            client.send('R@Client request file transfer process'.encode())
            time.sleep(1)
            recv_msg = client.recv(buffer_size).decode()
            print(f'Client recv_msg is {recv_msg}')
            item = recv_msg.split('@')
            if 'D' in item[0]:
                client.send('ACK'.encode())
                filelen = int(item[1])
                for i in range(0, filelen):
                    fileinfo = client.recv(buffer_size).decode() # get file info
                    print(f'fileinfo = {fileinfo}')
                    info_item = fileinfo.split('@')
                    filename = info_item[0]
                    filesize = int(info_item[1])
                    filepath = os.path.join(folderpath, filename)

                    bar = tqdm(range(filesize),('C: Receiving ' +filename), unit="M",unit_scale=True,unit_divisor=buffer_size)
                    client.send('ACK'.encode())
                    print(f'Client receiving {filename} now file size is {filesize}')
                    with open(filepath, 'wb') as fid:
                        while True:
                            recv_bData = client.recv(buffer_size)
                            if not recv_bData:
                                break
                        fid.write(recv_bData)
                        bar.update(recv_bData)
                        client.send('ACK'.encode())
                    nc_filelist = os.listdir(folderpath)
                    print('C:'+nc_filelist)
                client.close()


def main():  # Using multiprocessing run two servers and client
    s = multiprocessing.Process(target=server_side)
    c = multiprocessing.Process(target=client_side)

    s.start()
    time.sleep(2)
    c.start()

if __name__ == "__main__":
    main()