import os
import asyncio
import threading
import socket
from concurrent.futures import CancelledError

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
        self.server_task = None
        self.shutdown_event = None

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
            self.shutdown_event = asyncio.Event()

            server_thread = threading.Thread(
                target=self._run_server_thread
            )
            server_thread.start()
        except Exception as e:
            self.main.error(str(e))

    def _run_server_thread(self):
        try:
            self.server_task = self.loop.create_task(self.run_server())
            self.loop.run_forever()
        except Exception as e:
            self.main.error(f"Server thread error: {str(e)}")
        finally:
            try:
                # Cancel any pending tasks
                pending = asyncio.all_tasks(self.loop)
                for task in pending:
                    task.cancel()
                
                # Wait for all tasks to complete with a timeout
                if pending:
                    self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                self.server_task = None
                self.server = None
                self.loop.close()
            except Exception:
                pass

    async def stop_server(self):
        self.running = False
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
        if self.server_task and not self.server_task.done():
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass

    def stop(self):
        if not self.running or not self.loop:
            return

        async def _stop():
            await self.stop_server()
            self.loop.stop()

        try:
            future = asyncio.run_coroutine_threadsafe(_stop(), self.loop)
            future.result(timeout=5)  # Wait up to 5 seconds for shutdown
        except Exception as e:
            self.main.error(f"Error during shutdown: {str(e)}")
        finally:
            self.running = False

    async def run_server(self):
        try:
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
        except asyncio.CancelledError:
            self.main.log("Server shutdown initiated")
        except Exception as e:
            self.main.error(f"Server error: {str(e)}")
        finally:
            self.running = False
            self.main.log("Server stopped")

    async def read_line(self, reader):
        line = bytearray()
        while True:
            try:
                byte = await reader.read(1)
                if not byte: # EOF
                    return None
                if byte == b'\n':
                    break
                line.extend(byte)
            except asyncio.CancelledError:
                return None
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
                            try:
                                data = await reader.read(chunk_size)
                                if not data:
                                    break
                                f.write(data)
                                bytes_received += len(data)
                            except asyncio.CancelledError:
                                log("Transfer cancelled")
                                return

                    end_marker = await self.read_line(reader)
                    if end_marker != END_OF_FILE:
                        raise ValueError(f"Expected end of file marker, got: {end_marker}")

                    log(f"Received {filename} successfully")

                except ValueError as e:
                    log(f"Error processing file: {str(e)}")
                    continue

        except asyncio.CancelledError:
            log("Connection cancelled due to server shutdown")
        except Exception as e:
            log(f"Error occurred: {str(e)}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass