import socket
import os

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

def receive_files(dropbox, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", int(port)))
    s.listen(1)
    print(f"Listening on 0.0.0.0:{port}")

    conn, addr = s.accept()
    print(f"Connected to {addr}")

    count = 0

    def recv_header(header_conn):
        header_bytes = b""
        while b"\n" not in header_bytes:
            header_chunk = header_conn.recv(1)
            if not header_chunk:
                break
            header_bytes += header_chunk
        return header_bytes.decode().strip()

    while True:
        header = recv_header(conn)
        if header == "DONE":
            print("File transfer complete, closing connection")
            break

        try:
            filename, filesize = header.split(SEPARATOR)
            filesize = int(filesize)
        except ValueError:
            print("Invalid header received, closing connection")
            break

        save_path = os.path.join(dropbox, filename)
        print(f"Saving {filename} (${filesize} bytes) to {save_path}")

        received_bytes = 0
        with open(save_path, "wb") as f:
            while received_bytes < filesize:
                chunk = conn.recv(BUFFER_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                received_bytes += len(chunk)

        count += 1
        print(f"Saved {filename} (${filesize} bytes) to {save_path}")

    conn.close()
    s.close()
    print("Server closed")
    return count
