import socket
import os

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
END_OF_FILE = "<END_OF_FILE>"

class Client:
    def __init__(self, main, host, port):
        self.main = main
        self.host = host
        self.port = int(port)

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
                    s.sendall(header.encode())

                    with open(path, "rb") as f:
                        while True:
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read:
                                break
                            s.sendall(bytes_read)

                    s.sendall(END_OF_FILE.encode() + b"\n")
                    count += 1
                    self.main.log(f"Sent {filename}")

                s.sendall("DONE\n".encode())
                self.main.log(f"Successfully uploaded {count}/{len(files)} files")
        except ConnectionRefusedError:
            self.main.error(f"Failed to connect to {self.host}:{self.port}")
        except Exception as e:
            self.main.error(str(e))