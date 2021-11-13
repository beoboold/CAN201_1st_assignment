import os
from socket import *
from tqdm import *

ip = "127.0.0.1"
port = 20000
ADDR = (ip, port)
buffer_size = 1024
data_format = "utf-8"
filename = "12345.exe"
filesize = os.path.getsize(filename)

def main():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(ADDR)

    data = f"{filename}_{filesize}"
    client.send(data.encode(data_format))
    msg = client.recv(buffer_size).decode(data_format)
    print(f"SERVER: {msg}")

    bar = tqdm(range(filesize), f"sending {filename}", unit="B", unit_scale=True, unit_divisor=buffer_size)

    with open(filename, "rb") as fid:
        while True:
            data = fid.read(buffer_size)

            if not data:
                break

            client.send(data)
            msg = client.recv(buffer_size).decode(data_format)

            bar.update(len(data))

        client.close()

if __name__ == "__main__":
    main()