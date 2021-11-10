# Server side

import argparse
import time
from socket import *
import json
import numpy

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(2)
print('The server is waiting for connection')

conSocket, clientAddr = serverSocket.accept()
print('Connected from ',clientAddr)
noti = "Server is connected"
conSocket.sendto(noti.encode(),clientAddr)
