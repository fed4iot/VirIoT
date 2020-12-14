#!/usr/bin/python3
import requests
import argparse
import json
import time

def init_args(_parser):
    # insert here the parser argument. This function is used by parent f4i.py
    _parser.add_argument('-s', action='store', dest='serverUrl',
                         help='Server url (default: http://13.80.153.4:9090/api/v1)', default='http://13.80.153.4:9090/api/v1')
    _parser.add_argument('-c', action='store', dest='container',
                         help='k8s container name (default: none, means all containers of the pod)', default='')
    _parser.add_argument('-p', action='store', dest='pod',
                         help='k8s pod name (default: vernemq-0)', default='vernemq-0')
    _parser.set_defaults(func=run)


def run(args):
    payload = {}
    headers= {}
    url_cpu = args.serverUrl+"/query?query=irate(container_cpu_usage_seconds_total{namespace=\"default\",pod=\""+args.pod+"\",container=\""+args.container+"\"}[5m])"
    url_mem = args.serverUrl+"/query?query=container_memory_working_set_bytes{namespace = \"default\", pod = \""+args.pod+"\", container=\""+args.container+"\"}"
    url_netin = args.serverUrl+"/query?query=irate(container_network_receive_bytes_total{namespace = \"default\", pod = \""+args.pod+"\",}[5m])"
    url_netout = args.serverUrl+"/query?query=irate(container_network_transmit_bytes_total{namespace = \"default\", pod = \"" + args.pod + "\"}[5m])"

    #print(url_netout)
    while True:
        response_cpu = requests.request("GET", url_cpu, headers=headers, data=payload)
        response_mem = requests.request("GET", url_mem, headers=headers, data=payload)
        response_netin = requests.request("GET", url_netin, headers=headers, data=payload)
        response_netout = requests.request("GET", url_netout, headers=headers, data=payload)
        if response_cpu.status_code==200 and response_mem.status_code==200 :
            r_cpu=json.loads(response_cpu.text)
            r_mem = json.loads(response_mem.text)
            r_netin = json.loads(response_netin.text)
            r_netout = json.loads(response_netout.text)
            if len(r_cpu['data']['result'])>0:
                print(str(r_cpu['data']['result'][0]['value'][0])+
                      "\t"+r_cpu['data']['result'][0]['value'][1]+
                      "\t"+r_mem['data']['result'][0]['value'][1]+
                      "\t"+r_netin['data']['result'][0]['value'][1]+
                      "\t"+r_netout['data']['result'][0]['value'][1]
                      )
            time.sleep(5)
            #print(response_mem.text.encode('utf8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    init_args(parser)
    args = parser.parse_args()
    args.func(args)
