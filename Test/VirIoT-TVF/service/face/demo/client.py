import socket
import base64
import sys

HOST = 'localhost'
PORT = 33102

with open(sys.argv[1], 'rb') as f:
    img = f.read()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.connect((HOST, PORT))

    #img = base64.b64encode(img).decode('utf-8')

    print ("send")
    s.sendall(img)
    print ("complete")
    s.shutdown(1)
    print ("complete2")

    data = s.recv(10000)

    print(data.decode())

