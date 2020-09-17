import sys, socket, json, base64

#add import files
import http.client, urllib.request
import urllib.parse, urllib.error, urllib
#####

class SF():

    def __init__(self):

        #read config file
        with open('config.json', "r") as fp:
            setting = json.load(fp)

        self.host = setting["host"]
        self.port = setting["port"]
        self.segSize = setting["segSize"]
        self.faceKey = setting["faceKey"]
        self.faceUrl = setting["faceUrl"]

    #define service function
    def callServiceFunction(self):
        
        #Request headers.
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': self.faceKey
        }

        #Request parameters.
        params = urllib.parse.urlencode({
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            #'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
            'returnFaceAttributes': 'age,gender,emotion'    
        })

        #Request data.
        body = self.revData

        try:
            conn = http.client.HTTPSConnection(self.faceUrl)
            conn.request("POST", "/face/v1.0/detect?%s" % params, body, headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()

            temp = data.decode()

            if (temp == []):
                temp = "[null]"
        
            print (temp)

            return temp.encode()

        except Exception as e:
            print ("[callServiceFunction] FaceAPI error")
            #print ("[Error {}{}".format(e.errorno, e.strerror))

            return "error"

    def run(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(10)

            while True:

                print ("[callServiceFunction] waiting")
                clientsock, client_address = s.accept()

                try:
                    print ("[callServiceFunction] accepted")

                    self.revData = b''

                    while True:

                        data = clientsock.recv(self.segSize)

                        if not data:
                            break
                        self.revData += data

                    print ("[callServiceFunction] received")

                    print ("[callServiceFunction] callServiceFunction")

                    result = self.callServiceFunction()

                    print ("[callServiceFunction] send results")
                    clientsock.send(result)

                    print ("[callServiceFunction] send complete")

                except Exception as e:
                    print ("[callServiceFunction] error")
                    print (e)

                finally:
                    clientsock.close()


if __name__ == '__main__':

    sf = SF()
    sf.run()
