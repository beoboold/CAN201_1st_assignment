import gzip
import multiprocessing
import os
import shutil
import sys
import threading
import time
from socket import *
from tqdm import *
import argparse
import shutil

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
        elif 'R' in item[0]:#Server send data from client request
            connectSoc.send(f'D@{len(sendlist)}'.encode())
            response_msg = connectSoc.recv(buffer_size).decode()
            for i in range(0, len(sendlist)):
                if response_msg=='ACK':
                    filename = sendlist[i]
                    namesplit = filename.split('.')
                    if len(namesplit) == 1:
                        foldersize = 0
                        print(f'{filename} is folder')
                        newfolderpath = os.path.join(folderpath,filename)
                        print(f'{filename} path is {newfolderpath}')
                        for path, dirs, files in os.walk(newfolderpath):
                            for f in files:
                                fp = os.path.join(path,f)
                                foldersize += os.path.getsize(fp)
                        print(f'{filename} size is {foldersize}')
                        connectSoc.send(f'{filename}@{foldersize}'.encode())
                        response_msg = connectSoc.recv(buffer_size).decode()
                        print(response_msg)
                        if 'ACK' in response_msg:
                            connectSoc.send('ARC'.encode())
                            msg = connectSoc.recv(buffer_size).decode()
                            print(msg)
                            if msg == 'ARC':
                                print(f'Server start sending compressed archive to {clientAddr}')
                                shutil.make_archive(f'{newfolderpath}', 'zip', f'{newfolderpath}')#Zip folders
                                showlist = os.listdir(folderpath)
                                print(showlist)
                                newname = filename+'.zip'
                                newpath = os.path.join(folderpath, newname)
                                print(f'new server file path {newpath}')
                                with open(newpath, 'rb') as fol:
                                    while True:
                                        send_bData = fol.read(buffer_size)
                                        if not send_bData:
                                            break
                                        connectSoc.send(send_bData)
                                        final_msg = connectSoc.recv(buffer_size).decode()
                                        if not 'Archive' in final_msg:
                                            print('Wrong folder compressed file sending -line160')
                                    print('Zip file transfer finished')
                                    os.remove(newpath)
                            else:
                                print('wrong step')
                    else:
                        getFsize = os.path.join(folderpath, filename)
                        filesize = os.path.getsize(getFsize)
                        print(f'File size is {filesize}')
                        connectSoc.send(f'{filename}@{filesize}'.encode())
                        #bar = tqdm(range(filesize), ('Sending ' + filename), unit="B", unit_scale=True,unit_divisor=buffer_size)
                        response_msg = connectSoc.recv(buffer_size).decode()
                        if 'ACK' in response_msg:
                            connectSoc.send('F'.encode())
                            msg = connectSoc.recv(buffer_size).decode()
                            print(msg)
                            if 'F' in msg:
                                print(f'Server start sending file to {clientAddr}')
                                filepath = getFsize
                                print(f'new server file path {filepath}')
                                with open(filepath, 'rb') as fid:
                                    while True:
                                        send_bData = fid.read(buffer_size)
                                        if not send_bData:
                                            break
                                        connectSoc.send(send_bData)
                                        final_msg = connectSoc.recv(buffer_size).decode()
                                        if not 'File' in final_msg:
                                            print('Wrong file sending -line 183')
                                        #bar.update(len(send_bData))
                                    print(f'Server sent {filename}')

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
            print(recv_msg)
            if 'ACK' in recv_msg:
                for i in range(0, len(filelist)):  # Send fileinfo and data
                    filename = filelist[i]
                    filepath = os.path.join(folderpath, filename)
                    filesize = os.path.getsize(filepath)
                    datainfo = (f'{filename}@{filesize}')  # Send file information
                    client.send(datainfo.encode())
                    print(f'Client sent file information of {filename}')

                    #bar = tqdm(range(filesize), ('Sending ' + filename), unit="B", unit_scale=True, unit_divisor=buffer_size)
                    print(f'Sending {filename} data')
                    recv_msg = client.recv(buffer_size).decode()
                    print(recv_msg)
                    if 'ACK' in recv_msg:
                        with open(filepath, 'rb') as fid:  # Send actual file data
                            while True:
                                bData = fid.read(buffer_size)
                                if not bData:
                                    break
                                client.send(bData)
                                #bar.update(len(bData))
                        client.close()
                        print(f'{filename} sent')
        elif 'S' in item[0]:#Server will give file(s)
            print(f'Server: {item[1]}')
            client.send('R@Client request file transfer process'.encode())
            recv_msg = client.recv(buffer_size).decode()
            item = recv_msg.split('@')
            print(f'Client recv_msg is {recv_msg}')
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

                    bar = tqdm(range(filesize),('C: Receiving ' +filename), unit="B",unit_scale=True,unit_divisor=buffer_size)
                    client.send('ACK'.encode())
                    msg = client.recv(buffer_size).decode()
                    print(f'count is {filelen}')

                    if 'ARC' in msg: #A=Archive
                        client.send('ARC'.encode())
                        print('C: This file is compressed folder')
                        newname = filename+'.zip'
                        arcpath = os.path.join(folderpath, newname)
                        print(f'C: New client Archive path is {arcpath}')
                        with open(arcpath, 'wb') as a:
                            while True:
                                recv_bData = client.recv(buffer_size)
                                if not recv_bData:
                                    break
                                a.write(recv_bData)
                                client.send('Archive'.encode())
                                bar.update(len(recv_bData))
                        shutil.unpack_archive(arcpath,folderpath)
                        print(f'Client decompressed {newname} in path {folderpath}')

                    elif 'F' in msg:#F=File
                        client.send('F'.encode())
                        print(f'Client receiving {filename} now file size is {filesize}')
                        filepath = os.path.join(folderpath, filename)
                        print(f'New client file path is {filepath}')
                        with open(filepath, 'wb') as f:
                            while True:
                                recv_bData = client.recv(buffer_size)
                                if not recv_bData:
                                    break
                                f.write(recv_bData)
                                client.send('File'.encode())
                                bar.update(len(recv_bData))
                        print('Finished file receiving')
                client.close()


def main():  # Using multiprocessing run two servers and client
    s = multiprocessing.Process(target=server_side)
    c = multiprocessing.Process(target=client_side)

    s.start()
    time.sleep(1.5)
    c.start()

if __name__ == "__main__":
    main()