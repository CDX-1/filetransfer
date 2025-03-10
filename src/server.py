import os
import asyncio
import threading
import socket

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
END_OF_FILE = "<END_OF_FILE>"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

class Server:
    def __init__(self, main):
        self.main = main
        self.port = None
        self.dropbox = None
        self.running = False
        self.server = None
        self.loop = None

    def set_port(self, port):
        if self.running:
            return
        self.port = int(port)

    def set_dropbox(self, dropbox):
        if self.running:
            return
        self.dropbox = dropbox

    def start(self):
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            server_thread = threading.Thread(
                target=lambda: self.loop.run_until_complete(self.run_server())
            )
            server_thread.start()
        except Exception as e:
            self.main.error(str(e))

    def stop(self):
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)

    async def run_server(self):
        self.server = await asyncio.start_server(
            self.handle_client,
            "",
            self.port
        )

        ip = get_local_ip()
        self.main.log(f"Server listening at {ip}:{self.port}")
        self.running = True

        async with self.server:
            await self.server.serve_forever()

    async def read_line(self, reader):
        line = bytearray()
        while True:
            byte = await reader.read(1)
            if not byte:  # EOF
                return None
            if byte == b'\n':
                break
            line.extend(byte)
        return line.decode()

    async def handle_client(self, reader, writer):
        ip, port = writer.get_extra_info('peername')
        self.main.log(f"Connection from {ip}:{port}")

        def log(message):
            self.main.log(f"[{ip}:{port}]: {message}")

        try:
            while True:
                header = await self.read_line(reader)
                if not header:
                    log("Connection closed")
                    break
                    
                if header == "DONE":
                    log("All files received")
                    break

                try:
                    filename, filesize = header.strip().split(SEPARATOR)
                    filesize = int(filesize)
                    log(f"Receiving {filename} ({filesize} B)")

                    filepath = os.path.join(self.dropbox, filename)
                    bytes_received = 0

                    with open(filepath, "wb") as f:
                        while bytes_received < filesize:
                            chunk_size = min(BUFFER_SIZE, filesize - bytes_received)
                            data = await reader.read(chunk_size)
                            if not data:
                                break
                            f.write(data)
                            bytes_received += len(data)

                    end_marker = await self.read_line(reader)
                    if end_marker != END_OF_FILE:
                        raise ValueError(f"Expected end of file marker, got: {end_marker}")

                    log(f"Received {filename} successfully")

                except ValueError as e:
                    log(f"Error processing file: {str(e)}")
                    continue

        except Exception as e:
            log(f"Error occurred: {str(e)}")
        finally:
            writer.close()
            await writer.wait_closed()