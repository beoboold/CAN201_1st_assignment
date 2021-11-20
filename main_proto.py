import gzip
import multiprocessing
import os
import time
from socket import *
from tqdm import *
import threading
from multiprocessing import *
import json
import argparse

port = 20000
buffer_size = 1024
filename = ''
filepath = os.path.abspath(".\\share")


# filesize = os.path.getsize(filepath+filename)

def _argparse():
    parser = argparse.ArgumentParser(description="A")
    parser.add_argument('--ip', action='store', required=True, dest='ip', help='ip address')
    # parser.add_argument('--port', action='store',required=True, dest='port', help='port')

    return parser.parse_args()


class run():
    def server_side(slef):
        parser = _argparse()
        server_port = port
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('', server_port))
        server_socket.listen(2)
        print('Server is listening...')

        while True:
            connectSoc, clientAddr = server_socket.accept()
            print("Client connected from ", clientAddr)

            recv_data = connectSoc.recv(buffer_size).decode()
            item = recv_data.split("@")
            filename = item[0]
            filesize = int(item[1])
            filepath = item[2]

            print("File information received.")
            connectSoc.send("File information received".encode())

            bar = tqdm(range(filesize), ('Receiving ' + filename), unit="B", unit_scale=True, unit_divisor=buffer_size)
            # f"Receiving {filename}"

            with open("recv_" + filename + '.gz', 'wb') as fid:
                while True:
                    recv_Bdata = connectSoc.recv(buffer_size)

                    if not recv_Bdata:
                        break

                    fid.write(recv_Bdata)
                    # connectSoc.send("Data received".encode())

                    bar.update(len(recv_Bdata))
                print('Finish file transfer')

            with gzip.open(filepath + filename + '.gz', 'rb') as fid:
                read_data = fid.read()
                with open(filepath + filename, 'wb') as f:
                    f.write(read_data)
            os.remove(filepath + filename + '.gz')

    # if __name__ == "__main__":
    #    main()

    def client_side(self):
        print('Client start running')
        parser = _argparse()
        ip = parser.ip
        server_ip = ip
        server_port = port
        print(ip, port)

        client = socket(AF_INET, SOCK_STREAM)
        client.connect((server_ip, server_port))
        print(f'Client trying to connect with {server_ip}, {server_port}')

        orFile = open(filepath + filename, 'rb')  # open original file
        comFile = orFile.read()  # read file to compress
        orFile.close()

        with gzip.open(filename + '.gz', 'wb') as fc:  # fc:file compress
            fc.write(comFile)  # write compress file as filename.gz
        new_filesize = os.path.getsize(filename + '.gz')
        infoData = (f"{filename}@{new_filesize}@{filepath}")
        client.send(infoData.encode())
        print('Client sent file information')
        msg = client.recv(buffer_size).decode()
        print("SERVER: ", msg)

        bar = tqdm(range(new_filesize), ('Sending ' + filename), unit="B", unit_scale=True, unit_divisor=buffer_size)
        # f"sending {filename}"

        with open(filename + '.gz', "rb") as fid:
            while True:
                bData = fid.read(buffer_size)

                if not bData:
                    break

                client.send(bData)
                # msg = client.recv(buffer_size).decode()

                bar.update(len(bData))

        client.close()
        print('Client close/compressed file remove')
        os.remove(filename + '.gz')


# if __name__ == "__main__":
#    main()

def main():
    while True:
        s = threading.Thread(target=run().server_side)
        time.sleep(5)
        c = threading.Thread(target=run().client_side)

        s.start()
        c.start()


if __name__ == "__main__":
    main()
    # s = threading.Thread(target=client_side())
    # c = threading.Thread(target=server_side())

    # s.start()
    # c.start()
