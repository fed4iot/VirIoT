# ThingVisor HomeThermometer

This ThingVisor creates vThings whose data can be collected by Oregon Scientific Weather Stations. It can represent these type of data:
- Indoor temperature
- Outdoor temperature
- Indoor humidity
- Outdoor humidity

The data can be sent by POST HTTP Requests in one of these three endpoints:
- /home_temperature
- /home_humidity
- /sensor 


### Build locally with Docker (optional)

Docker can be used to build locally the image of the ThingVisor and then use it to deploy it.

```bash
docker build -t domussapiens/homethermometer-tv VirIoT/Thingvisors/DockerThingVisor/ThingVisor_HomeThermometer/
```

### Local Docker deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.
PS: If you want to be able to use the actuation with this thingvisor you have to set the backendUri (hostname only), backendPort (either 80 or 443 or anything), username (admin user with access to the DB) and password (of the admin user) of your backend. 

```bash
python3 f4i.py add-thingvisor -i domussapiens/homethermometer-tv -n home-thermometer-tv -d "HomeThermometer thingvisor" -p '{"backendUri": "####", "backendPort": "##", "username": "####", "password": "####"}'
```

### Kubernetes deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.
PS: If you want to be able to use the actuation with this thingvisor you have to set the backendUri (hostname only), backendPort (either 80 or 443 or anything), username (admin user with access to the DB) and password (of the admin user) of your backend. 

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -y "../yaml/thingVisor-homethermometer.yaml" -n home-thermometer-tv -p '{"backendUri": "####", "backendPort": "##", "username": "###", "password": "###"}'
```



### Data injection
Linux http (or similar apps such as curl and Postman) can be used to inject data using the samples provided.

```bash
http POST <thingVisorIP>:<thingVisorPort>/deep_sleep < samples/deep_sleep.json
http POST <thingVisorIP>:<thingVisorPort>/heart_rate < samples/heart_rate.json
http POST <thingVisorIP>:<thingVisorPort>/light_sleep < samples/light_sleep.json
http POST <thingVisorIP>:<thingVisorPort>/motion_intensity < samples/motion_intensity.json
```

## NGSI-LD data model
 
In this section, it is shown an example of valid input and output for each vthing.

### home_temperature

#### Example of a valid input

```bash
curl --location --request POST '<ip_thingvisor>:<port_thingvisor>/home_temperature' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "email": "paziente41@sferainnovazione.it",
        "room": "studio",
        "location": "indoor",
        "startTimeInSeconds": 123456700,
        "frequencyInSeconds": 60,
        "value": "23"
    },
    {
        "email": "paziente14@sferainnovazione.it",
        "room": "studio",
        "location": "indoor",
        "startTimeInSeconds": 123456760,
        "frequencyInSeconds": 60,
        "value": "22"
    }
]
```

### Example of an NGSI-LD entity of type home_temperature

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-oregon:home_temperature:paziente14@sferainnovazione.it:studio:indoor",
        "type": "home_temperature",
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1636705968
        },
        "email": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "frequencyInSeconds": {
            "type": "Property",
            "value": 60
        },
        "isIndoor": {
            "type": "Property",
            "value": true
        },
        "isLatest": {
            "type": "Property",
            "value": "True"
        },
        "queryDate": {
            "type": "Property",
            "value": 1636705968
        },
        "room": {
            "type": "Property",
            "value": "studio"
        },
        "startTimeInSeconds": {
            "type": "Property",
            "value": 123456700
        },
        "temperatureCelsiusOffsetMap": {
            "type": "Property",
            "value": {
                "0": 23,
                "60": 22
            }
        },
        "userEmail": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "measuredBySensor": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:sensors:1"
        },
        "commands": {
            "type": "Property",
            "value": "query"
        },
        "endTimeInSeconds": {
            "type": "Property",
            "value": 123456760
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "home-thermometer-tv/home_temperature"
        },
        "query": {
            "type": "Property",
            "value": {}
        },
        "query-result": {
            "type": "Property",
            "value": {}
        },
        "query-status": {
            "type": "Property",
            "value": {}
        }
    }
```

### home_humidity

#### Example of a valid input

```bash
curl --location --request POST '<ip_thingvisor>:<port_thingvisor>/home_humidity' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "email": "paziente41@sferainnovazione.it",
        "room": "studio",
        "location": "indoor",
        "startTimeInSeconds": 123456700,
        "frequencyInSeconds": 60,
        "value": "50"
    },
    {
        "email": "paziente14@sferainnovazione.it",
        "room": "studio",
        "location": "indoor",
        "startTimeInSeconds": 123456760,
        "frequencyInSeconds": 60,
        "value": "45"
    }
]
```

### Example of an NGSI-LD entity of type home_humidity

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-oregon:home_humidity:paziente14@sferainnovazione.it:studio:indoor",
        "type": "home_humidity",
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1636705968
        },
        "email": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "frequencyInSeconds": {
            "type": "Property",
            "value": 60
        },
        "isIndoor": {
            "type": "Property",
            "value": true
        },
        "isLatest": {
            "type": "Property",
            "value": "True"
        },
        "queryDate": {
            "type": "Property",
            "value": 1636705968
        },
        "room": {
            "type": "Property",
            "value": "studio"
        },
        "startTimeInSeconds": {
            "type": "Property",
            "value": 123456700
        },
        "temperatureCelsiusOffsetMap": {
            "type": "Property",
            "value": {
                "0": 50,
                "60": 45
            }
        },
        "userEmail": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "measuredBySensor": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:sensors:1"
        },
        "commands": {
            "type": "Property",
            "value": "query"
        },
        "endTimeInSeconds": {
            "type": "Property",
            "value": 123456760
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "home-thermometer-tv/home_humidity"
        },
        "query": {
            "type": "Property",
            "value": {}
        },
        "query-result": {
            "type": "Property",
            "value": {}
        },
        "query-status": {
            "type": "Property",
            "value": {}
        }
    }
```

### sensor

#### Example of a valid input

```bash
curl --location --request POST '<ip_thingvisor>:<port_thingvisor>/sensor' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "email": "paziente14@sferainnovazione.it",
        "owner": "Paziente 14",
        "address": "-",
        "geoPosition": "-",
        "status": 0
        "mac_address": "F1:53:DB:EF:B4:3A"
    }
]
```

### Example of a valid NGSI-LD entity for sensor

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-oregon:sensors:F153DBEFB43A",
        "type": "sensor",
        "address": {
            "type": "Property",
            "value": "-"
        },
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1636740590
        },
        "email": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "geoPosition": {
            "type": "Property",
            "value": "-"
        },
        "isLatest": {
            "type": "Property",
            "value": "True"
        },
        "owner": {
            "type": "Property",
            "value": "Paziente14"
        },
        "queryDate": {
            "type": "Property",
            "value": 1636740590
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "home-thermometer-tv/sensor"
        },
        "status": {
            "type": "Property",
            "value": 1
        }
    }
```

## Actuation

Every entity (except the ones created by the vThing "sensor") can be actuated on the property "query".
It requiries that you have a backend exposing the same APIs the Thingvisor expects to have. Plus,
the backend must be able to perform the query on the dataset where you store the data. You can do it in two ways:

- Temporal query. You will receive all the data in the time interval from "date" - 24 * 3600 to "date:
```bash
curl --location --request POST '<context_broker_ip>:<context_broker_port>/ngsi-ld/v1/entities/<id_entity>/attrs' \
--header 'Accept: application/ld+json' \
--header 'Content-Type: application/json' \
--data-raw '{
    "query" : {
        "type": "Property",
        "value": {
            "cmd-id": "query",
            "cmd-value": {
                "date": 1636704088,
                "hoursInterval": 24
            }
        }
    }
}'
```


- Getting the latest context data. If you want to get back the latest data stored in the context of the thingvisor you can perform this actuation:
```bash
curl --location --request POST '<context_broker_ip>:<context_broker_port>/ngsi-ld/v1/entities/<id_entity>/attrs' \
--header 'Accept: application/ld+json' \
--header 'Content-Type: application/json' \
--data-raw '{
    "query" : {
        "type": "Property",
        "value": {
            "cmd-id": "query",
            "cmd-value": {
                "date": "latest"
            }
        }
    }
}'
```