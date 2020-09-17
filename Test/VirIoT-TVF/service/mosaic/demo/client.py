import socket
import base64
import sys
import json

HOST = 'localhost'
PORT = 33103
revSize = 4096

with open(sys.argv[1], 'rb') as f:
    img = f.read()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.connect((HOST, PORT))

    print ("send")
    s.sendall(img)
    print ("complete")
    s.shutdown(1)
    print ("complete2")

    revData = b''

    while True:
        data = s.recv(revSize)
        if not data:
            break
        revData += data

    result = revData.decode()
    result = json.loads(result)

    print(result)

