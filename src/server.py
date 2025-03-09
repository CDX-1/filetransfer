import socket
import os

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

class Server:
    def __init__(self, port, dropbox_dir, logger):
        self.port = int(port)
        self.dropbox_dir = dropbox_dir
        self.logger = logger
        self.running = False
        self.socket = None
        
    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
        
    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('', self.port))
            self.socket.listen()
            self.socket.settimeout(1.0)  # 1 second timeout for accept()
            self.running = True
            self.logger.log(f"Server listening on port {self.port}")
            
            while self.running:
                try:
                    conn, addr = self.socket.accept()
                    self.logger.log(f"Connection from {addr}")
                    
                    with conn:
                        while True:
                            header = conn.recv(BUFFER_SIZE).decode()
                            
                            if header == "DONE":
                                self.logger.log("Client finished sending files")
                                break
                                
                            filename, filesize = header.strip().split(SEPARATOR)
                            filesize = int(filesize)
                            
                            filepath = os.path.join(self.dropbox_dir, filename)
                            
                            with open(filepath, "wb") as f:
                                bytes_received = 0
                                while bytes_received < filesize:
                                    bytes_read = conn.recv(BUFFER_SIZE)
                                    if not bytes_read:
                                        break
                                    f.write(bytes_read)
                                    bytes_received += len(bytes_read)
                                    
                            self.logger.log(f"Received {filename}")
                except socket.timeout:
                    continue  # Check running flag every second
                            
        except Exception as e:
            self.logger.error(f"{str(e)}")
        finally:
            if self.socket:
                self.socket.close()
            self.running = False
