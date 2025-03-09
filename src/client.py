import socket
import os

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

class Client:
    def __init__(self, host, port, logger):
        self.host = host
        self.port = int(port)
        self.logger = logger
        
    def send_files(self, files):
        for file in files:
            self.logger.log(file)

    def send_files_x(self, files):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                self.logger.log(f"Connected to {self.host}:{self.port}")
                
                for file_path in files:
                    if not os.path.exists(file_path):
                        self.logger.error(f"File {file_path} does not exist")
                        continue
                        
                    filesize = os.path.getsize(file_path)
                    filename = os.path.basename(file_path)
                    
                    header = f"{filename}{SEPARATOR}{filesize}\n"
                    s.send(header.encode())
                    
                    with open(file_path, "rb") as f:
                        while True:
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read:
                                break
                            s.sendall(bytes_read)
                    self.logger.log(f"Completed sending {filename}")
                
                s.send("DONE".encode())
                self.logger.log("All files sent successfully")
                
        except ConnectionRefusedError:
            self.logger.error(f"Could not connect to {self.host}:{self.port}")
        except Exception as e:
            self.logger.error(f"{str(e)}")
