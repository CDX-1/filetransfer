# File Transfer

A little Python program I made to transfer files between my Mac and PC

#### Specifications

* Written using Python v3.11 (Tested on v3.12 & 3.13)
* tkinter
* socket
* threading
* os

## Usage

### Server (Receiver)

1. Select the dropbox directory (the folder where files will be stored)
2. Enter a port to run your server on
3. Share the address provided in your status bar

Received files will be saved in your dropbox directory, you can stop the server at any time

### Client (Sender)

1. Enter the server's address (host:port)
2. Select the files you want to upload through the upload files button

## Notes

- A computer can act as a server and client at the same time
- This program was only intended for local networks and thus has only been tested for local networks
- This program is not battle-tested nor intended for commercial use, use at your own risk