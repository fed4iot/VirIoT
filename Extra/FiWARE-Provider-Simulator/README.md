# License

FiWARE Provider Simulator source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# README

This software deploys the need components to simulate a provider environment which contains an Orion Context Broker, an IotAgent, an MQTT broker and an implementation which simulates devices.


## How To Run

### Local Docker deployment

Access to the project folder and run:

```bash  
./build.sh
docker-compose up -d
```

You can see mqtt comunications in provider side running:
```bash  
./mqtt-provider-monitor.sh
``` 

Finally, provision the mqtt devices, to create the corresponding entities in Orion Context Broker of the provider environment. To do it, change to provisioning-devices subfolder and run:

```bash  
./device001.sh
``` 
NOTE: To obtain more entities in Orion Context Broker of provider you can run device002.sh and device003.sh too.


Finally, you can access to Orion Context Broker of provider to recover entities information, change directory to VirIoT/Extra/FiWARE-Provider-Simulator and run:

```bash
./broker-provider-monitor.sh
```

## NGSIv2 data model

Each entity obtained from OCB (NGSIv2) is represented following the next schema:


```json
{
  	"id":"<entity identifier>",
  	"type":"<entity type>",
  	"TimeInstant": {
            "type": "ISO8601",
            "value": "",
            "metadata": {}
        },
  	"attribute1":{
    	"type":"attribute type",
    	"value":"attribute value",
    	"metadata": {}
    },
  	...
  	"attributeN":{
    	"type":"attribute type",
    	"value":"attribute value",
    	"metadata": {}
    },
  	"command1": {
 		"type": "command",
		"value": "",
		"metadata": {}
	};
  	"command1_info": {
 		"type": "commandResult",
		"value": "",
		"metadata": {}
	};
  	"command1_status": {
 		"type": "commandStatus",
		"value": "",
		"metadata": {}
	};
  	...
  	"commandN": {
 		"type": "command",
		"value": "",
		"metadata": {}
	};
  	"commandN_info": {
 		"type": "commandResult",
		"value": "",
		"metadata": {}
	};
  	"commandN_status": {
 		"type": "commandStatus",
		"value": "",
		"metadata": {}
	}

}

```
