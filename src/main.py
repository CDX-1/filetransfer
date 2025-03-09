import socket
import tkinter as tk
from tkinter.filedialog import askdirectory
import os
import threading

from client import upload_files
from server import receive_files

def main():
    root = tk.Tk()
    root.title("File Transfer")
    root.geometry("650x300")

    for i in range(3):
        root.grid_columnconfigure(i, weight=1)

    # CLIENT

    def do_upload():
        client_status_var.set("Uploading...")
        addr = client_addr_var.get()
        host, port = addr.split(":")
        count = upload_files(host, port)

        if count == -1:  # File transfer cancelled
            client_status_var.set("Pending files...")
            return

        client_status_var.set(f"Uploaded {count} files")

    client_label = tk.Label(root, text="Client")
    client_label.grid(column=0, row=0, columnspan=3, padx=10, pady=10)

    client_addr_label = tk.Label(root, text="Address: ")
    client_addr_label.grid(column=0, row=1, padx=10, pady=10)

    client_addr_var = tk.StringVar()
    client_addr = tk.Entry(root, textvariable=client_addr_var)
    client_addr.grid(column=1, row=1, padx=10, pady=10)

    upload_button = tk.Button(root, text="Upload files", command=do_upload)
    upload_button.grid(column=2, row=1, padx=10, pady=10)

    client_status_var = tk.StringVar(value="Pending files...")
    client_status_label = tk.Label(root, textvariable=client_status_var)
    client_status_label.grid(column=0, row=2, columnspan=3, padx=10, pady=10)

    # SERVER

    def set_dropbox_dir():
        path = askdirectory()
        if not(os.path.isdir(path)):
            return
        dropbox_dir.set(path)

    def update_server_toggle(_0, _1, _2):
        if server_toggle_var.get():
            server_toggle_label_var.set("Stop server")
        else:
            server_toggle_label_var.set("Start server")

    def server_start():
        if dropbox_dir.get() == "":
            server_status_var.set("Dropbox directory is empty")
            return

        server_toggle_var.set(True)
        host = socket.gethostbyname(socket.gethostname())
        port = server_port_var.get()

        if port == "":
            server_status_var.set("Port is empty")
            return
        try:
            int(port)
        except ValueError:
            server_status_var.set("Port is invalid")
            return

        server_status_var.set(f"Server running at {host}:{port}")

        def run_server():
            received = receive_files(dropbox_dir.get(), server_port_var.get())
            root.after(0, lambda: server_status_var.set(f"Received {received} files"))
            root.after(0, lambda: server_toggle_var.set(False))

        threading.Thread(target=run_server, daemon=True).start()

    server_label = tk.Label(root, text="Server")
    server_label.grid(column=0, row=3, columnspan=3, padx=10, pady=10)

    dropbox_label = tk.Label(root, text="Dropbox: ")
    dropbox_label.grid(column=0, row=4, padx=10, pady=10)

    dropbox_dir = tk.StringVar(value="")
    dropbox_dir_label = tk.Label(root, textvariable=dropbox_dir)
    dropbox_dir_label.grid(column=1, row=4, padx=10, pady=10)

    dropbox_button = tk.Button(root, text="Select Dropbox", command=set_dropbox_dir)
    dropbox_button.grid(column=2, row=4, padx=10, pady=10)

    server_port_label = tk.Label(root, text="Port: ")
    server_port_label.grid(column=0, row=5, padx=10, pady=10)

    server_port_var = tk.StringVar()
    server_port = tk.Entry(root, textvariable=server_port_var)
    server_port.grid(column=1, row=5, padx=10, pady=10)

    server_toggle_var = tk.BooleanVar(value=False)
    server_toggle_label_var = tk.StringVar(value="Start server")
    server_toggle_var.trace('w', update_server_toggle)
    server_toggle = tk.Button(root, textvariable=server_toggle_label_var, command=server_start)
    server_toggle.grid(column=2, row=5, padx=10, pady=10)

    server_status_var = tk.StringVar(value="Set dropbox directory")
    server_status_label = tk.Label(root, textvariable=server_status_var)
    server_status_label.grid(column=0, row=6, columnspan=3, padx=10, pady=10)

    root.mainloop()

if __name__ == '__main__':
    main()
