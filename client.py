import socket
import os
from tkinter.filedialog import askopenfilenames

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

def upload_files(host, port):
    files = askopenfilenames()
    if not files:
        return -1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    print(f"Connected to server {host}:{port}")

    count = 0

    for path in files:
        filename = os.path.basename(path)
        filesize = os.path.getsize(path)
        print(f"Uploading {filename} ({filesize} bytes)...")

        header = f"{filename}{SEPARATOR}{filesize}\n"
        s.send(header.encode())

        with open(path, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                s.sendall(bytes_read)

        count += 1
        print(f"Finished uploading {filename}")

    s.send("DONE".encode())
    s.close()
    print("Finished sending all files")
    return count