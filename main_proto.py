import socket
from socket import *
from tqdm import *

port = 20000
buffer_size = 1024
data_format = "utf-8"

def main():
    serverSoc = socket(AF_INET, SOCK_STREAM)
    serverSoc.bind(("",port))
    serverSoc.listen()
    print("Listening...")

    connectSoc, clientAddr = serverSoc.accept()
    print("Client connected from ",clientAddr)

    data = connectSoc.recv(buffer_size).decode(data_format)
    item = data.split("_")
    filename = item[0]
    filesize = int(item[1])

    print("File data received.")
    connectSoc.send("File data received".encode(data_format))

    bar = tqdm(range(filesize), f"sending {filename}", unit="B", unit_scale=True, unit_divisor=buffer_size)

    with open(f"recv_{filename}", 'wb') as fid:
        while True:
            data = connectSoc.recv(buffer_size)

            if not data:
                break

            fid.write(data)
            connectSoc.send("Data received".encode(data_format))

            bar.update(len(data))

    connectSoc.close()
    serverSoc.close()

if __name__ == "__main__":
    main()

