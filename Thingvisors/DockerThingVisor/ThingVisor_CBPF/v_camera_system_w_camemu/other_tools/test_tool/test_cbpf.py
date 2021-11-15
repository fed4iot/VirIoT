import requests
import sys
import base64
import json

REST_HOST = ""

API = "/api"

testImg = "test.jpg"

headers = {'Content-Type': 'application/octet-stream'}

def callReadImg():

    with open(testImg, 'rb') as f:
        srcImg = f.read()
    
    binImg = base64.b64encode(srcImg).decode('utf-8')

    up_img = {"content": {"value": binImg},
              "file name": {"value": testImg}}

    return up_img

def main():

    args = sys.argv
    
    if (len(args) != 2):
        print ("[Usage] python3 **.py <cmd>")
        print ("start, close, upload, get_result, remove")
        sys.exit(1)

    if args[1] == "upload":
        cmd = "/upload"
        headers = {'Content-Type': 'application/json'}
        data = callReadImg()
        data = json.dumps(data)
        end_point = 'http://' + REST_HOST + API + str(cmd)
        response = requests.post(end_point, headers=headers, data=data)

        print (response.json())

    elif args[1] == "get_result":
        cmd = "/get_result"
        end_point = 'http://' + REST_HOST + API + str(cmd)
        response = requests.get(end_point)

        if (response.json() is not None):
            result = json.loads(response.json())
            print (json.dumps(result, indent=2))
        else:
            print (response.json())

    elif args[1] == "remove":
        cmd = "/remove_img=all"
        end_point = 'http://' + REST_HOST + API + str(cmd)
        response = requests.get(end_point)

        print (response.json())

    else:
        cmd = "/face_rec=" + args[1]
        #headers = {'Content-Type': 'text/plain'}
        end_point = 'http://' + REST_HOST + API + str(cmd)
        response = requests.get(end_point)

        print (response.json())


if __name__ == '__main__':

    main()

