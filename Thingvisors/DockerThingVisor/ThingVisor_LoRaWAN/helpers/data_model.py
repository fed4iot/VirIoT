import json


class NgsiLdEntity :
    def __init__(self,id):
        self.id = id
        self.baseid = ""

    def get_fullid(self):
        return f"{self.baseid}:{self.id}"

    def serialize(self):
        payload = self.get_payload()
        return json.dumps(payload)

    def get_payload(self):
        payload = {"id":self.get_fullid()}
        payload.update(self._get_payload())
        return payload

    def _get_payload(self):
        return {}

    
class Context :
    def __init__(self):
        self.entities = set()

    def register(self, entity):
        self.entities.add(entity)

    def serialize(self):
        return json.dumps([e.get_payload() for e in self.entities])

class Site(NgsiLdEntity):
    def __init__(self,id):
        NgsiLdEntity.__init__(self,id)
        self.temperature = None
        self.humidity = None

    def _get_payload(self):
        return {                        #TODO: fix missing ObservedBy relation
        	"temperature":{
		        "type":"Property",
		        "value":self.temperature
            },   
        	"humidity":{
		        "type":"Property",
		        "value":self.humidity
            }
        }
    
class CameraEventDetector(NgsiLdEntity) :
    def __init__(self, id, camera):
        NgsiLdEntity.__init__(self, id)
        self.baseid = "urn:ngsi-ld:Sensor"
        self.camera = camera
        
    def _get_payload(self):
        return {
            "type": "Sensor",
            "connectsTo": {
                "type": "Relationship",
                "object": self.camera.get_fullid()
            },
            "@context": [
                "http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "http://models.eglobalmark.com/grasse/waste-management-context.jsonld"
            ]
        }

       
class SmartCamera(NgsiLdEntity) :
    def __init__(self, id):
        NgsiLdEntity.__init__(self, id)
        self.baseid = "urn:ngsi-ld"
        self.id = id
        self.site = None
        self.location = None #array [latitude, longitude]
        self.observation_space = None #array [[longitude,latitude], [longitude,latitude], ...]

    def set_site(self, site):
        self.site = site

    def set_location(self, location):
        self.location = location

    def set_observation_space(self, observation_space):
        self.observation_space = observation_space
        
    def _get_payload(self) :
        payload = {
            "type":"Device",
            "name":{
                "type":"Property",
                "value":"Grasse Camera"
            },
            "@context":[
                "http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "http://models.eglobalmark.com/grasse/waste-management-context.jsonld"
            ]
        }
        if (self.site):
            payload["monitors"]={
                "type":"Relationship",
                "object":f"urn:ngsi-ld:Site:{self.id_site}"
            }

        if (self.location is not None) :
            payload["location"] = {
                "type":"GeoProperty",
                "value":{
                    "type":"Point",
                    "coordinates": self.location
                }
            }
            
        
        if (self.observation_space is not None) :
            payload["observationSpace"] = {
                    "type":"GeoProperty",
                    "value":{
                        "type":"Polygon",
                        "coordinates":self.observation_space
                    }
                }

            # "numberOfPictures":{
            #     "type":"Property",
            #     "value":10,
            #     "unitCode": "5K"
            # },
            
        return payload



class Thermometer(NgsiLdEntity) :
    def __init__(self, id):
        NgsiLdEntity.__init__(self, id)
        self.baseid = "urn:ngsi-ld"
        self.id = id
        self.site = None
        self.location = None #array [latitude, longitude]

    def set_site(self, site):
        self.site = site

    def set_location(self, location):
        self.location = location

    def _get_payload(self) :
        payload = {
            "type":"Device",
            "name":{
                "type":"Property",
                "value":"Grasse Camera"
            },
            "@context":[
                "http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "http://models.eglobalmark.com/grasse/waste-management-context.jsonld"
            ]
        }
        if (self.site):
            payload["monitors"]={
                "type":"Relationship",
                "object":f"urn:ngsi-ld:Site:{self.site.id}"
            }

        if (self.location is not None) :
            payload["location"] = {
                "type":"GeoProperty",
                "value":{
                    "type":"Point",
                    "coordinates": self.location
                }
            }
            
        
        return payload
