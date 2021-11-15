#! /usr/bin/python3 
import requests
import json
import base64
import sys
import time
import ast

SLEEP = 5

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

    if (len(cmd) != 4):
        print("please input propert arguments")
        print("[Usage] $python3 **.py <vsilo ip> <vsilo port> <vthing name>")
        print("[example] $python3 **.py vm1 30141 cbpf-murcia/cbpf/01")
        sys.exit(-1)
    else:
        pass

    vsilo_ip = cmd[1]
    vsilo_port = cmd[2]
    v_thing_name = cmd[3].replace('/', ':')

    end_point = "http://"+vsilo_ip+":"+vsilo_port+"/Mobius/"+v_thing_name+"/"+v_thing_name
    url = end_point + "/msg?rcn=4"
    #url = end_point + "/createdAt?rcn=4"

    print (end_point)
    print (url)

    base_time = time.time()
    next_time = 0
    count = 0

    while True:

        ts1 = time.time()
        response = requests.request("GET", url, headers=headers)
        ts2 = time.time()

        if (count == 0):
            dict_data = ast.literal_eval(response.text)
            print (json.dumps(dict_data, indent=2))
        else:
            pass
        print("count response time {} {}".format(count, (ts2-ts1)))

        count = count + 1

        next_time = ((base_time - time.time()) % SLEEP) or SLEEP
        time.sleep(next_time)


if __name__ == '__main__':

    main()
