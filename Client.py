# Client side

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

server_ip = '127.0.0.1'
server_port = 20000
buffer_size = 1024

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_ip, server_port))

with open('xjtlu.jpg','rb') as fid:
    image_bin = fid.read()
    print('Finished convert to binary')

client_socket.send(image_bin)
print('Client sent image to server')
print('Client wait for server response')
image_bin_rec = client_socket.recv(buffer_size)
if image_bin_rec:
    print('Server sent image')
    with open('xjtlu2.jpg','wb') as fid:
        fid.write(image_bin_rec)

client_socket.close()