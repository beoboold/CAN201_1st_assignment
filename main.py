# Server side

import os
import sys
from socket import *
import shutil
import struct
import hashlib
import math
#import tqdm
import numpy
import threading
import multiprocessing
import gzip
import zlib
import zipfile
import time

serverPort = 20000
bufferSize = 1024
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(2)
print('The server is waiting for connection')
while True:
    conSocket, clientAddr = serverSocket.accept()
    print('Connected from ',clientAddr)

    image_bin_recv = conSocket.recv(bufferSize)
    print(image_bin_recv)
    if not image_bin_recv:
        print('data dose not exist')
    else:
        print('server received data')
        with open('xjtlu1.jpg','wb') as fid:
            fid.write(image_bin_recv)
        with open('xjtlu1.jpg','rb') as fid:
            image_bin = fid.read()

    conSocket.send(image_bin)
    conSocket.close()