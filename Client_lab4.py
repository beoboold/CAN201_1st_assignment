
import argparse
import time
from socket import *
import json
import numpy

def _argparse():
    parser = argparse.ArgumentParser(description='A')
    parser.add_argument('--ip', action='store', required=True,dest='ip',help='ip address')
    parser.add_argument('--port', action='store', required=True, dest='port', help='port')

    return parser.parse_args()

def main():
    parser = _argparse()
    ip = parser.ip
    port = int(parser.port)

    server_ip = ip
    server_port = port

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    request_dict = {'command': 'time'}

    client_socket.send(json.dumps(request_dict).encode())
    print(client_socket.recv(20000).decode())

if __name__ == '__main__':
    main()