import os
from socket import *
from tqdm import *
import gzip
import argparse

ip = "127.0.0.1"
port = 20000
ADDR = (ip, port)
buffer_size = 20480
filename = "15mb.exe"
filesize = os.path.getsize(filename)
filepath = os.path.abspath(".\\share")

def _argparse():
    parser = argparse.ArgumentParser(description='A')
    parser.add_argument('--ip', action='store', required=True,dest='ip',help='ip address')
    #parser.add_argument('--port', action='store', required=True, dest='port', help='port')

    return parser.parse_args()

def main():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(ADDR)

    orFile = open(filepath+filename, 'rb') #open original file
    comFile = orFile.read() #read file to compress
    orFile.close()

    with gzip.open(filename+'.gz', 'wb') as fc: #fc:file compress
        fc.write(comFile) #write compress file as filename.gz
    new_filesize = os.path.getsize(filename+'.gz')
    infoData = (f"{filename}@{new_filesize}@{filepath}")
    client.send(infoData.encode())
    print('Client sent file information')
    msg = client.recv(buffer_size).decode()
    print("SERVER: ",msg)

    bar = tqdm(range(new_filesize), ('Sending '+filename), unit="B", unit_scale=True, unit_divisor=buffer_size)
    #f"sending {filename}"

    with open(filename+'.gz', "rb") as fid:
        while True:
            bData = fid.read(buffer_size)

            if not bData:
                break

            client.send(bData)
            #msg = client.recv(buffer_size).decode()

            bar.update(len(bData))

    client.close()
    print('Client close/compressed file remove')
    os.remove(filename + '.gz')

if __name__ == "__main__":
    main()