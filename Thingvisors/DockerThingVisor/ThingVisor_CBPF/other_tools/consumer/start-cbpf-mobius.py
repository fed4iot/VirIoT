#! /usr/bin/python3 
import requests
import json
import base64
import sys
import time
import ast

headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': 'S',
        'content-type': "application/vnd.onem2m-res+json;ty=4",
        'cache-control': "no-cache",
}

payload = {
        'm2m:cin': {
        'con': {
            'cmd-value': 'null',
	    'cmd-qos':'2',
            'cmd-params': 'null'
	    }
        }
}

def main():

    cmd = sys.argv

    if (len(cmd) != 6):
        print("please input propert arguments")
        print("[Usage] $python3 **.py <vsilo ip> <vsilo port> <vthing name> <request image name> <command>")
        print("[example] $python3 **.py vm1 30141 cbpf-murcia/cbpf/01 test.jpg start")
        print("Available commands: <start> and <close>")
        sys.exit(-1)
    else:
        pass

    vsilo_ip = cmd[1]
    vsilo_port = cmd[2]
    v_thing_name = cmd[3].replace('/', ':')
    request_img = cmd[4]
    command = cmd[5]

    end_point = "http://"+vsilo_ip+":"+vsilo_port+"/Mobius/"+v_thing_name+"/"+v_thing_name

    print (end_point)

    if command == "close":
        url = end_point + "/" + command
        payload['m2m:cin']['con']['cmd-value'] = command 

    elif command == "start":
        url = end_point + "/" + command

        with open(request_img, 'rb') as f:
            srcImg = f.read()

        binImg = base64.b64encode(srcImg).decode('utf-8')
        params = {"content": {"value": binImg},
                "file name": {"value": request_img}}

        payload['m2m:cin']['con']['cmd-value'] = command
        payload['m2m:cin']['con']['cmd-params'] = params

    else:
        print ("input command is not available") 
        sys.exit(-1)
    
    print (url)

    ts1 = time.time()
    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
    ts2 = time.time()

    result = ast.literal_eval(response.text)
    #print(response.text.encode('utf8'))
    print (json.dumps(result, indent=2))
    print ("response time {}".format(ts2-ts1))

if __name__ == '__main__':

    main()
