# Chirpstack LoRaWAN server ThingVisor

Provide a framework to implement thingVisors connecting vThings to devices through a LoRaWAN network.

## Startup and configuration

The base command is like this:
```bash
python f4i.py add-thingvisor -c http://127.0.0.1:8090 -i fed4iot/lorawan-tv -n cscam01 -p "{'chirpstack_mqtt_server':'172.17.0.2','chirpstack_mqtt_port':'8883', 'chirpstack_cafile':$(base64 -w0 '/path/to/ca.crt'), 'chirpstack_crtfile':$(base64 -w0 '/path/to/user.crt'), 'chirpstack_keyfile':$(base64 -w0 '/path/to/user.key'), 'devices=[{{'type':'smartcam', 'label':'SC-ABC', 'appid':'12', 'deveui':'0123456789ABCDEF'}}]}
```

The thingVisor connects to the MQTT broker of the Chirpstack LoRaWAN server, it thus needs to know the server address and port (variables chirpstack_mqtt_server, chirpstack_mqtt_port). Optionally it can also identify itself using a certificate (variables chirpstack_cafile, chirpstack_crtfile, chirpstack_keyfile), note that it's the content of these files which is base64 encoded into the parameters string. 

When the thingVisor is connected to the Chirpstack server, the vThings are created based on the content of the list named _devices_ in the parameters.  Each vThing is associated to a LoRaWAN device, it is thus identified using the Chirstack application id (_appid_) and the _deveui_ of the device; for the thingVisor to properly integrate it in the Viriot platform, we require also a _label_ and a _type_ of device. This latter parameter has a predefined set of values, which tells to the thingVisor which data structures are used into the communications.

For now, the only supported type is 'smartcam'.

## NGSI-LS data model

```json
{
   "id": "urn:ngsi-ld:Device:smartcam01",
   "type":"Device",
   "name":{
     "type":"Property",
	 "value":"Grasse Camera"
	},
	"monitors": {
                "type":"Relationship",
                "object":f"urn:ngsi-ld:Site:{self.id_site}"
            },
	"location": {
                "type":"GeoProperty",
                "value":{
                    "type":"Point",
                    "coordinates": self.location
                }
            },
	"observationSpace": {
                    "type":"GeoProperty",
                    "value":{
                        "type":"Polygon",
                        "coordinates":self.observation_space
                    }
                }
	"@context":[
		"http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
		"http://models.eglobalmark.com/grasse/waste-management-context.jsonld"
	]
}

{
	"id": "urn:ngsi-ld:Sensor:PersonCounter01",
	"type": "Sensor",
	"connectsTo": {
		"type": "Relationship",
		"object": "urn:ngsi-ld:Device:smartcam01"
	},
	"@context": [
		"http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
		"http://models.eglobalmark.com/grasse/waste-management-context.jsonld"
	]
}

{
	"id":"urn:ngsi-ld:Site:01",
	"type":"Site",
	"location":{
		"type":"GeoProperty",
		"value":{
			"type":"Point",
			"coordinates":[
				-8.5,
				41.2
			]
		}
	},
	"name":{
		"type":"Property",
		"value":"Sophia"
	},
	"personNumber":{
		"type":"Property",
		"value":150,
		"unitCode": "IE",
		"observedAt": "2020-03-10T13:44:38.000Z",
		"observedBy":{
			"type":"Relationship",
			"object":"urn:ngsi-ld:Sensor:PersonCounter01"
		}
	},
	"@context":[
      "http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
      "http://models.eglobalmark.com/grasse/waste-management-context.jsonld"
   ]
}
```


