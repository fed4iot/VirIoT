from pymongo import MongoClient
from collections import OrderedDict
import os
import sys
import yaml
import shutil 
#import kubernetes

MongoIP = ''
MongoPORT = 27017

CMD = ['register-sf', 'list-sf', 'delete-sf', 
       'create-sfc', 'show-sfc', 'delete-sfc', 
       'create-yaml', 'show-yaml', 'delete-yaml',
       'schedule-pod','deploy-pod', 'delete-pod']

sensor = ['camera', 'labcam']

pod_temp_file = './template/pod_template.yml'
deploy_pod_dir = './deployPod/'

topic_prefix = "kafka:/"

def represent_odict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())

#def setup_yaml():
#    yaml.add_representer(OrderedDict, represent_odict)

def registerSF(sfinfo):

    print ("**********************************")
    client = MongoClient(MongoIP, int(MongoPORT))
    print (client)

    #access db for tvf_db
    db = client.tvf_db

    #access collection
    col = db.sfc_collection

    col.insert_one({'name': sfinfo[0], 'image': sfinfo[1]})

    print ("register sf complete")

    client.close()
    print ("**********************************")
 
def deleteSF():

    print ("**********************************")
    client = MongoClient(MongoIP, int(MongoPORT))
    print (client)

    #access db for tvf_db
    db = client.tvf_db

    #access collection
    col = db.sfc_collection

    print ("Show register SF lists")
    print ("register SFC name:")
    num=1
    for data in col.find():
        print ("{}: {}".format(num, data['name']))
        num = num + 1

    print ("Please input service name that you want to delete")
    serviceName = input()
    result = col.delete_many({'name': serviceName})
    print (result)

    client.close()
    print ("**********************************")


def showSF():

    print ("**********************************")
    client = MongoClient(MongoIP, int(MongoPORT))
    print (client)

    #access db for tvf_db
    db = client.tvf_db

    #access collection
    col = db.sfc_collection

    print ("Show register SF lists")
    print ("register SF name:")
    num=1
    for data in col.find(projection={'_id':0}):
        print ("{}: {}".format(num, data))
        num = num + 1

    client.close()
    print ("**********************************")
 

def createSFC():

    print ("**********************************")
    print ("Please input your id/name")
    userName = input()

    sfc = {"user name": userName}

    while True:
        print ("Please input number of SFs you want to create SFC")
        numSFs = input()
        if(numSFs.isdecimal() == True):
            numSFs = int(numSFs)
            break
        
    client = MongoClient(MongoIP, int(MongoPORT))
    print (client)

    #access db for tvf_db
    db = client.tvf_db

    #access collection
    col = db.sfc_collection

    print ("Show register SF lists")
    print ("register SF name:")
    num=1
    for data in col.find():
        print ("{}: {}".format(num, data['name']))
        num = num + 1

    temp = []

    i = 0
    while i < numSFs:
        
        i = i + 1

        if (i==1):

            print ("Please select {}st SF name ".format(i))
            print ("Please select from {}".format(sensor))
            sensorName = input()

            if sensorName in sensor:
                temp.append({"name": sensorName})
            else: 
                print ("Request SF are not registered")
                print ("Please select appropriate SF name")
                i = i - 1
        else:
            if (i==2):
                print ("Please select {}nd SF name".format(i))
            elif (i==3):
                print ("Please select {}rd SF name".format(i))
            else :
                print ("Please select {}th SF name".format(i))

            requestSF = input()
            foundSF = {}
            for data in col.find(filter={'name':requestSF},projection={'_id':0}):
                foundSF = data
            if ('name' in foundSF):
                if (foundSF['name'] == 'mosaic'):
                    print ("Please input Tag Name to perform mosaic")
                    tag = input()
                    print ("Please input target Service Name for detection")
                    service = input()
                    foundSF.update({"service": service, "tag": tag})
                if (foundSF['name'] == 'counter'):
                    print ("Please input Tag name to count numbers")
                    tag = input()
                    print ("Please input target Service Name for detection")
                    service = input()
                    foundSF.update({"service": service, "tag": tag})
                temp.append(foundSF)
            else:
                print ("Request SF are not registered")
                print ("Please select appropriate SF name")
                i = i - 1

    sfc.update({"sfc": temp})
    print ("Request SFC: {}".format(sfc))

    #access collection
    col = db.sfc_request

    col.insert_one(sfc)

    print ("sfc request complete")

    client.close()
    print ("**********************************")
 

def showSFC():

    print ("**********************************")
    client = MongoClient(MongoIP, int(MongoPORT))
    print (client)

    #access db for tvf_db
    db = client.tvf_db

    #access collection
    col = db.sfc_request

    print ("Show request SFC lists")
    print ("request SFC name:")
    num=1
    for data in col.find(projection={'_id':0}):
        print ("{}: {}".format(num, data))
        num = num + 1

    client.close()
    print ("**********************************")
 

def deleteSFC():

    print ("**********************************")
    client = MongoClient(MongoIP, int(MongoPORT))
    print (client)

    #access db for tvf_db
    db = client.tvf_db

    #access collection
    col = db.sfc_request

    print ("Show request SFC lists")
    print ("request SFC name:")
    num=1
    for data in col.find(projection={'_id':0}):
        print ("{}: {}".format(num, data))
        num = num + 1

    print ("Please input user name that you want to delete")
    userName = input()
    result = col.delete_many({'user name': userName})
    print (result)

    client.close()
    print ("**********************************")
 
def createYAML():

    yaml.add_representer(OrderedDict, represent_odict)

    print ("**********************************")
    client = MongoClient(MongoIP, int(MongoPORT))
    print (client)

    #access db for tvf_db
    db = client.tvf_db

    #access collection
    col = db.sfc_request

    print ("Show request SFC lists")
    print ("request SFC name:")
    num=1
    for data in col.find(projection={'_id':0}):
        print ("{}: {}".format(num, data))
        num = num + 1

    print ("Please input user name that you want to create Pod")
    userName = input()

    requestSFC = col.find_one(filter={'user name':userName},projection={'_id':0})
    print (requestSFC)

    ## Prepare directory for storing yaml files
    yaml_dir = deploy_pod_dir + userName + "/" 
    if os.path.exists(yaml_dir) == True:
        shutil.rmtree(yaml_dir)
    os.makedirs(yaml_dir)

    with open(pod_temp_file) as f:
        dict_temp_pod = yaml.load(f)

    yaml_obj = yaml.dump(dict_temp_pod, default_flow_style=False)
    #print (yaml_obj)

    sfc_info = requestSFC['sfc']
    topic_name = ""
    pre_topic_name = ""
    dict_pod_marge = []

    for i in range(len(sfc_info)):

        #reset dict_pod
        dict_pod = dict_temp_pod
        pod_env = []

        if i == 0:
            print ("currently sensor is not managed by docker")
            print ("so skip")
            pre_topic_name = sfc_info[i]['name']
        else:
            pod_name = sfc_info[i]['name'] + '-' + userName
            dict_pod['metadata']['name'] = pod_name
            dict_pod['metadata']['labels']['app'] = pod_name
            dict_pod['spec']['selector']['matchLabels']['app'] = pod_name
            dict_pod['spec']['template']['metadata']['labels']['app'] = pod_name

            #Current assumption: 1 pod to 1 image
            dict_pod_cnt = dict_pod['spec']['template']['spec']['containers'][0]
            dict_pod_cnt['name'] = sfc_info[i]['name']
            dict_pod_cnt['image'] = sfc_info[i]['image']

            ## Define ENV
            
            ## If tag is specified, then the tag name is added to topic name.
            if ('tag' in sfc_info[i]):
                env_tag = {"name": "TAG", "value": sfc_info[i]['tag']}
                pod_env.append(env_tag)
                topic_name = sfc_info[i]['tag'] + sfc_info[i]['name'] + '/' + pre_topic_name
            else:
                topic_name = sfc_info[i]['name'] + '/' + pre_topic_name
  
            if ('service' in sfc_info[i]):
                env_service = {"name": "SERVICE", "value": sfc_info[i]['service']}
                pod_env.append(env_service)

            env_topic = {"name": "TOPIC", "value": topic_prefix+topic_name}
            pod_env.append(env_topic)

            dict_pod_cnt.update({"env": pod_env})

            pre_topic_name = topic_name

            dict_pod_marge.append(dict_pod)

            # dict -> yaml
            pod_yaml_name = yaml_dir + pod_name + ".yaml"
            with open(pod_yaml_name, 'w') as f:
                yaml.dump(dict_pod, f, default_flow_style=False)
            yaml_pod = yaml.dump(dict_pod, default_flow_style=False)
            print (yaml_pod)

    upload_info = {"user name": userName, "pod info": dict_pod_marge}

    #access collection
    col = db.pod_yaml
    col.insert_one(upload_info)
    print ("register pod complete")

    client.close()
    print ("pod create complete")
    print ("**********************************")

def showYAML():

    print ("**********************************")
    client = MongoClient(MongoIP, int(MongoPORT))
    print (client)

    #access db for tvf_db
    db = client.tvf_db

    #access collection
    col = db.pod_yaml

    print ("Show request SFC lists")
    print ("request SFC name:")
    num=1
    for data in col.find(projection={'_id':0}):
        print ("{}: {}".format(num, data))
        num = num + 1

    client.close()
    print ("**********************************")

def deleteYAML():

    print ("**********************************")
    client = MongoClient(MongoIP, int(MongoPORT))
    print (client)

    #access db for tvf_db
    db = client.tvf_db

    #access collection
    col = db.pod_yaml

    print ("Show request SFC for YAML")
    print ("request SFC name:")
    num=1
    for data in col.find(projection={'_id':0}):
        print ("{}: {}".format(num, data))
        num = num + 1

    print ("Please input user name that you want to delete")
    userName = input()
    result = col.delete_many({'user name': userName})
    print (result)

    client.close()
    print ("**********************************")
 

def schedulePod():

    print ("**********************************")

    print ("dummy")

    print ("**********************************")

def deployPod():

    print ("**********************************")

    print ("dummy")

    print ("**********************************")

def deletePod():

    print ("**********************************")

    print ("dummy")

    print ("**********************************")


if __name__ == '__main__':
    
    while True:

        print ("Please specify command")
        print ("command lists: {}".format(CMD))
        print ("If you want to quit, please type: exit")
        print ("*** input command ***")

        inputCMD = input()

        if (inputCMD == "exit"):
            sys.exit(1)

        if (inputCMD == CMD[0]):

            while True:
                print ("You request to register SF")
                print ("Please specify sf info")
                print ("Please input service name")
                sfinfo =[]
                sfinfo.append(input())
                print ("Please input image name")
                sfinfo.append(input())
                print ("input info: {}".format(sfinfo))
                print ("If it is fine, please type: yes")
                print ("If you want to return, please type: no")
                if input() == "yes":
                    registerSF(sfinfo)
                    break
                if input() == "no":
                    break

        if (inputCMD == CMD[1]):
            showSF()

        if (inputCMD == CMD[2]):
            deleteSF()

        if (inputCMD == CMD[3]):
            createSFC()

        if (inputCMD == CMD[4]):
            showSFC()

        if (inputCMD == CMD[5]):
            deleteSFC()

        if (inputCMD == CMD[6]):
            createYAML()

        if (inputCMD == CMD[7]):
            showYAML()

        if (inputCMD == CMD[8]):
            deleteYAML()

        if (inputCMD == CMD[9]):
            schedulePod()

        if (inputCMD == CMD[10]):
            deployPod()

        if (inputCMD == CMD[11]):
            deletePod()

        if (inputCMD not in CMD):
            print ("Input command is not implemented")
