import requests
import json
import socketio
import threading

class WebSocketClient(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        sio = socketio.Client()
    
        @sio.event
        def connect():
            print('connection established')
        
        @sio.event
        def my_message(data):
            print('message received with ', data)
            sio.emit('my response', {'response': 'my response'})
        
        @sio.event
        def disconnect():
            print('disconnected from server')
    
        sio.connect(self.url)
        sio.wait()


class ContextEntity:
    def __init__(self):
        self.id = ""
        self.type = ""        
        self.attributes = {}
        self.metadata = {}
    
    def toJSON(self):
        ctxElement = {}
    
        ctxElement['entityId'] = {}
        ctxElement['entityId']['id'] = self.id
        ctxElement['entityId']['type'] = self.type        
        ctxElement['entityId']['isPattern'] = False        
        
        ctxElement['attributes'] = self.attributes
        ctxElement['metadata'] = self.metadata

        return json.dumps(ctxElement)
        
class FogFlowClient:
    def init(self, url):        
        self.fogflowURL = url

        wsclient = WebSocketClient(url)
        wsclient.start()

    # synchronized remote call
    def remoteCall(self, serviceTopology):
        response = requests.get(self.fogflowURL + '/remoteCall?serviceTopology=' + serviceTopology)
        print(response.text)
        
    # asynchronize way to trigger a fog function
    def start(self, serviceTopology, callback):
        response = requests.get(self.fogflowURL + '/start?serviceTopology=' + serviceTopology)
        print(response.text)
            
    # asynchronize way to trigger a fog function
    def stop(self, serviceTopology):
        response = requests.get(self.fogflowURL + '/stop?serviceTopology=' + serviceTopology)
        print(response.text)            
    
    def sendIntent(self, serviceTopology):
        intent = {}
        intent['topology'] = serviceTopology
        intent['priority'] = {
            'exclusive': False,
            'level': 50
        };        
        intent['geoscope'] = {
            'scopeType': "global",
            'scopeValue': "global"
        };            
        
        headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}                
        response = requests.post(self.fogflowURL + '/intent', data=json.dumps(intent), headers=headers)
        if response.status_code != 200:
            print('failed to update context')
            print(response.text)
            return False    
        else:
            print('send intent')        
            return True    
       
    def removeIntent(self, intentEntityId):
        paramter = {}
        paramter['id'] = intentEntityId
    
        headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}                
        response = requests.delete(self.fogflowURL + '/intent', data=json.dumps(paramter), headers=headers)
        if response.status_code != 200:
            print('failed to remove intent')
            print(response.text)
            return False    
        else:
            print('remove intent')        
            return True    

    def put(self, ctxEntity):
        headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
        response = requests.post(self.fogflowURL + '/updateContext', data=ctxEntity.toJSON(), headers=headers)
        if response.status_code != 200:
            print('failed to update context')
            print(response.text)
            return False    
        else:
            print('update context')        
            return True

    def get(self, entityID):
    
        print(entityID)
        
        return True  
        
                
    def delete(self, entityID):
        print(entityID)
        return True      



