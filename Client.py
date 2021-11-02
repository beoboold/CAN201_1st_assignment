# Client side

import argparse
import time
from socket import *
import json
import numpy

print("python3 main.py --ip ")
start = input();

serverName = start
serverPort = 12000
bufferSize = 1024
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

data,addr = clientSocket.recvfrom(bufferSize)
if data :
    print(data.decode())
else:
    print("Connection lost")
