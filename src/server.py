import os
import asyncio
import threading
import socket

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

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
            self.loop = asyncio.get_event_loop()
            asyncio.set_event_loop(self.loop)

            server_thread = threading.Thread(
                target = lambda: self.loop.run_until_complete(self.run_server())
            )
            server_thread.start()
        except Exception as e:
            self.main.error(str(e))

    def stop(self):
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop())

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

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        self.main.log(f"Connection from {addr}")

        def log(message):
            self.main.log(f"[{addr}]: {message}")

        try:
            while True:
                header_bytes = await reader.read(BUFFER_SIZE)
                header = header_bytes.decode()

                if not header or header.strip() == "DONE":
                    log("File transfer complete")
                    break

                filename, filesize = header.strip().split(SEPARATOR)
                filesize = int(filesize)

                filepath = os.path.join(self.dropbox, filename)

                with open(filepath, "wb") as f:
                    bytes_received = 0
                    while bytes_received < filesize:
                        bytes_read = await reader.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        f.write(bytes_read)
                        bytes_received += len(bytes_read)

                log(f"Received {filename} ({filesize} B)")
        except Exception as e:
            log("Error occurred")
            self.main.error(str(e))
        finally:
            writer.close()
            await writer.wait_closed()