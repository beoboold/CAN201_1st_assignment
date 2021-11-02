
import argparse
import time
from socket import *
import json
import numpy

def _argparse():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--port', action='',required=True, dest='port', help='port')

    return parser.parse_args()

def get_time():
    return{'command': 'time', 'feedback': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}

def get_name():
    return{'command': 'name', 'feedback': 'Jin'}

protocol_command={'time':get_time(),'name':get_name()}

def main():
    parser = _argparse()
    port = int(parser.port)

    server_port = port
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('',server_port))
    server_socket.listen(2)

    while True:
        connection_socket, client_addr = server_socket.accept()
        print(client_addr)
        json_bin_recv = connection_socket.recv(20000)
        json_recv_dict = json.loads(json_bin_recv.decode())
        feedback_msg = {}
        if 'command' in json_recv_dict:
            command = json_recv_dict['command']
            if command in protocol_command:
                feedback_msg = protocol_command[command]()
            else:
                feedback_msg = {'command': json_recv_dict['command'], 'feedback':'404'}
        else:
            feedback_msg = {'command': '', 'feedback': '400'}

            connection_socket.send(json.dumps(feedback_msg).encode())

if __name__ == '__main__':
    main()