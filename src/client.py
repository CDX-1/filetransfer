import socket
import os

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

class Client:
    def __init__(self, main, host, port):
        self.main = main
        self.host = host
        self.port = port

    def send_files(self, files):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                self.main.log(f"Connected to {self.host}:{self.port}")

                count = 0
                for path in files:
                    if not os.path.exists(path):
                        self.main.log(f"File {path} does not exist")
                        continue

                    filesize = os.path.getsize(path)
                    filename = os.path.basename(path)

                    header = f"{filename}{SEPARATOR}{filesize}\n"
                    s.send(header.encode())

                    with open(path, "rb") as f:
                        while True:
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read:
                                break
                            s.sendall(bytes_read)
                    count += 1

                s.send("DONE".encode())
                self.main.log(f"Successfully uploaded {count}/{len(files)} files")
        except ConnectionResetError:
            self.main.error(f"Failed to connect to {self.host}:{self.port}")
        except Exception as e:
            self.main.error(str(e))