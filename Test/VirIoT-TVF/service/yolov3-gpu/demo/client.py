import socket
import base64

with open("dog.jpg", 'rb') as f:
    img = f.read()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.connect(('localhost', 33101))

    #img = base64.b64encode(img).decode('utf-8')

    s.sendall(img)
    s.shutdown(1)

    data = s.recv(10000)
    result = data.decode()

    #print(result)

    temp = result.split("_")
    numDetect = len(temp)

    YOLO = []

    #Ignore the last detection
    for i in range(numDetect-1):

        temp2 = temp[i].split(",")
        dict_body ={'tagName': temp2[0],
                    'probability': temp2[1],
                    'boundingBox': {'left': temp2[2],
                                    'top': temp2[3],
                                    'width': temp2[4],
                                    'height': temp2[5]
                                    }
                    }
        YOLO.append(dict_body)

    print (YOLO)
