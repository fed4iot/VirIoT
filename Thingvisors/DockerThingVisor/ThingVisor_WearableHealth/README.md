# ThingVisor WearableHealth

This ThingVisor creates a vThing whose data are medical measures from the Garmin International. It rappresent these type of data:
- summaries (heart_rate)
- epochs (motion_intensity)
- sleeps (pulse_ox, light_sleep, rem_sleep, awake_periods, deep_sleep)
- pulse_ox (pulse_ox)

The data can be sent by POST HTTP Requests in one of these eight endpoints:
- /deep_sleep
- /light_sleep
- /rem_sleep
- /awake_period
- /motion_intensity
- /heart_rate
- /pulse_ox
- /sensor

## How To Run

### Build locally with Docker (optional)

Docker can be used to build locally the image of the ThingVisor and then use it to deploy it.

```bash
docker build -t domussapiens/wearablehealth-tv VirIoT/Thingvisors/DockerThingVisor/ThingVisor_WearableHealth/
```

### Local Docker deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.
PS: If you want to be able to use the actuation with this thingvisor you have to set the backendUri (hostname only), backendPort (either 80 or 443 or anything), username (admin user with access to the DB) and password (of the admin user) of your backend. 

```bash
python3 f4i.py add-thingvisor -i domussapiens/wearable-health-tv -n wearable-health-tv -d "Wearable Health thingvisor" -p '{"backendUri": "####", "backendPort": "##", "username": "####", "password": "####"}'
```

### Kubernetes deployment

Use the VirIoT CLI and run the following command to run the ThingVisor example.
PS: If you want to be able to use the actuation with this thingvisor you have to set the backendUri (hostname only), backendPort (either 80 or 443 or anything), username (admin user with access to the DB) and password (of the admin user) of your backend. 

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -y "../yaml/thingVisor-wearablehealth.yaml" -n wearable-health-tv -p '{"backendUri": "####", "backendPort": "##", "username": "###", "password": "###"}'
```

## NGSI-LD data model
 
In this section, it is shown an example of valid input and output for each vthing.

### heart_rate

#### Example of a valid input

```bash
curl --location --request POST '<ip_thingvisor>:<port_thingvisor>/heart_rate' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "summary_id": "x315ee18-5d8e8840",
        "startTimeInSeconds": 1636375017,
        "durationInSeconds": "24360",
        "value": { "2040": "87" },
        "email": "paziente14@sferainnovazione.it"
    },
    {
        "summary_id": "x315ee18-5d8e8840",
        "startTimeInSeconds": 1569652080,
        "durationInSeconds": "24360",
        "value": { "2460": "81" },
        "email": "paziente14@sferainnovazione.it"
    }
]
```

### Example of an NGSI-LD entity of type heart_rate

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-garmin:heart_rate:paziente14@sferainnovazione.it",
        "type": "heart_rate",
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1636375017
        },
        "durationInSeconds": {
            "type": "Property",
            "value": 24360
        },
        "email": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "isLatest": {
            "type": "Property",
            "value": "True"
        },
        "queryDate": {
            "type": "Property",
            "value": 1636703927
        },
        "startTimeInSeconds": {
            "type": "Property",
            "value": 1636585200
        },
        "timeOffsetHeartRateSamples": {
            "type": "Property",
            "value": {
                "2040": 87,
                "2460": 81
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
            "value": 1636375017
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "wearable-health-tv/heart_rate"
        }
    }
```


### pulse_ox

#### Example of a valid input

```bash
curl --location --request POST '<ip_thingvisor>:<port_thingvisor>/pulse_ox' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "summary_id": "x315ee18-5d8e8840",
        "startTimeInSeconds": 1636375017,
        "durationInSeconds": "24360",
        "value": { "2040": "95" },
        "email": "paziente14@sferainnovazione.it"
    },
    {
        "summary_id": "x315ee18-5d8e8840",
        "startTimeInSeconds": 1569652080,
        "durationInSeconds": "24360",
        "value": { "2460": "97" },
        "email": "paziente14@sferainnovazione.it"
    }
]
```

### Example of an NGSI-LD entity of type heart_rate

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-garmin:pulse_ox:paziente14@sferainnovazione.it",
        "type": "pulse_ox",
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1636375017
        },
        "durationInSeconds": {
            "type": "Property",
            "value": 24360
        },
        "email": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "isLatest": {
            "type": "Property",
            "value": "True"
        },
        "queryDate": {
            "type": "Property",
            "value": 1636703927
        },
        "startTimeInSeconds": {
            "type": "Property",
            "value": 1636585200
        },
        "timeOffsetHeartRateSamples": {
            "type": "Property",
            "value": {
                "2040": 95,
                "2460": 97
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
            "value": 1636375017
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "wearable-health-tv/pulse_ox"
        }
    }
```


### motion_intensity

#### Example of a valid input

```bash
curl --location --request POST '<ip_thingvisor>:<port_thingvisor>/motion_intensity' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "summary_id":"x314c08b-5d6ee698-6aa178",
        "email": "paziente14@sferainnovazione.it",
        "startTimeInSeconds":"1569963000",
        "durationInSeconds":"29340",
        "timestamp": 1571470200,
        "activity_type": "SEDENTARY",
        "intensity": "SEDENTARY",
        "mean_motion_intensity": 1,
        "max_motion_intensity": 3,
        "distance_in_meters": 3,
        "steps": 0
    },
    {
        "summary_id":"x314c08b-5d6ee698-6aa16",
        "startTimeInSeconds":"1569963900",
        "durationInSeconds":"29340",
        "timestamp": 1571470200,
        "email": "paziente4@sferainnovazione.it",
        "activity_type": "SEDENTARY",
        "intensity": "SEDENTARY",
        "mean_motion_intensity": 1,
        "max_motion_intensity": 2,
        "distance_in_meters": 1,
        "steps": 0
    }
]
```

### Example of a valid NGSI-LD entity for motion_intensity

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-garmin:motion_intensity:paziente14@sferainnovazione.it",
        "type": "motion_intensity",
        "activityType": {
            "type": "Property",
            "value": {
                "0": "SEDENTARY",
                "900": "SEDENTARY",
                "27000": "SEDENTARY",
                "27900": "SEDENTARY"
            }
        },
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1571470200
        },
        "distanceInMeters": {
            "type": "Property",
            "value": {
                "0": 3,
                "900": 1
            }
        },
        "durationInSeconds": {
            "type": "Property",
            "value": 29340
        },
        "email": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "intensity": {
            "type": "Property",
            "value": {
                "0": "SEDENTARY",
                "900": "SEDENTARY"
            }
        },
        "isLatest": {
            "type": "Property",
            "value": "True"
        },
        "maxMotionIntensity": {
            "type": "Property",
            "value": {
                "0": 3,
                "900": 2
            }
        },
        "meanMotionIntensity": {
            "type": "Property",
            "value": {
                "0": 1,
                "900": 1
            }
        },
        "queryDate": {
            "type": "Property",
            "value": 1571470200
        },
        "startTimeInSeconds": {
            "type": "Property",
            "value": 1571470200
        },
        "steps": {
            "type": "Property",
            "value": {
                "0": 0,
                "900": 0
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
            "value": 1571500020
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "wearable-health-tv/motion_intensity"
        }
    }
```

### deep_sleep

#### Example of a valid input

```bash
curl --location --request POST '<ip_thingvisor>:<port_thingvisor>/deep_sleep' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "summary_id": "x315ee18-5d8e8840-5f28",
        "startTimeInSeconds": "1569622080",
        "durationInSeconds": "24360",
        "value": {
            "endTimeInSeconds": 1569625380,
            "startTimeInSeconds": 1569622560
        },
        "deepSleepInSeconds": 3000,
        "email": "paziente2@sferainnovazione.it"
    },
    {
        "summary_id": "x315ee18-5d8e8840-5f28",
        "startTimeInSeconds": "1569622080",
        "durationInSeconds": "24360",
        "value": {
            "endTimeInSeconds": 1569625700,
            "startTimeInSeconds": 1569625500
        },
        "deepSleepInSeconds": 3000,
        "email": "paziente2@sferainnovazione.it"
    }
]
```

### Example of a valid NGSI-LD entity for deep_sleep

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-garmin:deep_sleep:paziente14@sferainnovazione.it",
        "type": "deep_sleep",
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1636703925
        },
        "deepSleepInSeconds": {
            "type": "Property",
            "value": 6000
        },
        "deepSleepMap": {
            "type": "Property",
            "value": [
                {
                    "startTimeInSeconds": 1569622560,
                    "endTimeInSeconds": 1569625380
                },
                {
                    "startTimeInSeconds": 1569625500,
                    "endTimeInSeconds": 1569625700
                }
            ]
        },
        "durationInSeconds": {
            "type": "Property",
            "value": 6000
        },
        "email": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "isLatest": {
            "type": "Property",
            "value": "True"
        },
        "queryDate": {
            "type": "Property",
            "value": 1636703925
        },
        "startTimeInSeconds": {
            "type": "Property",
            "value": 1569622560
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
            "value": 1569625700
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "wearable-health-tv/deep_sleep"
        }
    }
```

### rem_sleep

#### Example of a valid input

```bash
curl --location --request POST '<ip_thingvisor>:<port_thingvisor>/rem_sleep' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "summary_id": "x315ee18-5d8e8840-5f28",
        "startTimeInSeconds": "1569622080",
        "durationInSeconds": "24360",
        "value": {
            "endTimeInSeconds": 1569625380,
            "startTimeInSeconds": 1569622560
        },
        "remSleepInSeconds": 3000,
        "email": "paziente2@sferainnovazione.it"
    },
    {
        "summary_id": "x315ee18-5d8e8840-5f28",
        "startTimeInSeconds": "1569622080",
        "durationInSeconds": "24360",
        "value": {
            "endTimeInSeconds": 1569625700,
            "startTimeInSeconds": 1569625500
        },
        "remSleepInSeconds": 3000,
        "email": "paziente2@sferainnovazione.it"
    }
]
```

### Example of a valid NGSI-LD entity for rem_sleep

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-garmin:rem_sleep:paziente14@sferainnovazione.it",
        "type": "rem_sleep",
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1636703925
        },
        "remSleepInSeconds": {
            "type": "Property",
            "value": 6000
        },
        "remSleepMap": {
            "type": "Property",
            "value": [
                {
                    "startTimeInSeconds": 1569622560,
                    "endTimeInSeconds": 1569625380
                },
                {
                    "startTimeInSeconds": 1569625500,
                    "endTimeInSeconds": 1569625700
                }
            ]
        },
        "durationInSeconds": {
            "type": "Property",
            "value": 6000
        },
        "email": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "isLatest": {
            "type": "Property",
            "value": "True"
        },
        "queryDate": {
            "type": "Property",
            "value": 1636703925
        },
        "startTimeInSeconds": {
            "type": "Property",
            "value": 1569622560
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
            "value": 1569625700
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "wearable-health-tv/rem_sleep"
        }
    }
```


### light_sleep

#### Example of a valid input

```bash
curl --location --request POST '<ip_thingvisor>:<port_thingvisor>/light_sleep' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "summary_id": "x315ee18-5d8e8840-5f28",
        "startTimeInSeconds": "1569622080",
        "durationInSeconds": "24360",
        "value": {
            "endTimeInSeconds": 1569625380,
            "startTimeInSeconds": 1569622560
        },
        "lightSleepInSeconds": 3000,
        "email": "paziente2@sferainnovazione.it"
    },
    {
        "summary_id": "x315ee18-5d8e8840-5f28",
        "startTimeInSeconds": "1569622080",
        "durationInSeconds": "24360",
        "value": {
            "endTimeInSeconds": 1569625700,
            "startTimeInSeconds": 1569625500
        },
        "lightSleepInSeconds": 3000,
        "email": "paziente2@sferainnovazione.it"
    }
]
```

### Example of a valid NGSI-LD entity for light_sleep

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-garmin:light_sleep:paziente14@sferainnovazione.it",
        "type": "light_sleep",
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1636703925
        },
        "lightSleepInSeconds": {
            "type": "Property",
            "value": 6000
        },
        "lightSleepMap": {
            "type": "Property",
            "value": [
                {
                    "startTimeInSeconds": 1569622560,
                    "endTimeInSeconds": 1569625380
                },
                {
                    "startTimeInSeconds": 1569625500,
                    "endTimeInSeconds": 1569625700
                }
            ]
        },
        "durationInSeconds": {
            "type": "Property",
            "value": 6000
        },
        "email": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "isLatest": {
            "type": "Property",
            "value": "True"
        },
        "queryDate": {
            "type": "Property",
            "value": 1636703925
        },
        "startTimeInSeconds": {
            "type": "Property",
            "value": 1569622560
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
            "value": 1569625700
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "wearable-health-tv/light_sleep"
        }
    }
```



### awake_periods

#### Example of a valid input

```bash
curl --location --request POST '<ip_thingvisor>:<port_thingvisor>/awake_periods' \
--header 'Content-Type: application/json' \
--data-raw '[
    {
        "summary_id": "x315ee18-5d8e8840-5f28",
        "startTimeInSeconds": "1569622080",
        "durationInSeconds": "24360",
        "value": {
            "endTimeInSeconds": 1569625380,
            "startTimeInSeconds": 1569622560
        },
        "awakeInSeconds": 3000,
        "email": "paziente2@sferainnovazione.it"
    },
    {
        "summary_id": "x315ee18-5d8e8840-5f28",
        "startTimeInSeconds": "1569622080",
        "durationInSeconds": "24360",
        "value": {
            "endTimeInSeconds": 1569625700,
            "startTimeInSeconds": 1569625500
        },
        "awakeInSeconds": 3000,
        "email": "paziente2@sferainnovazione.it"
    }
]
```

### Example of a valid NGSI-LD entity for awake_periods

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-garmin:awake_periods:paziente14@sferainnovazione.it",
        "type": "awake_periods",
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1636703925
        },
        "awakeInSeconds": {
            "type": "Property",
            "value": 6000
        },
        "awakeMap": {
            "type": "Property",
            "value": [
                {
                    "startTimeInSeconds": 1569622560,
                    "endTimeInSeconds": 1569625380
                },
                {
                    "startTimeInSeconds": 1569625500,
                    "endTimeInSeconds": 1569625700
                }
            ]
        },
        "durationInSeconds": {
            "type": "Property",
            "value": 6000
        },
        "email": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "isLatest": {
            "type": "Property",
            "value": "True"
        },
        "queryDate": {
            "type": "Property",
            "value": 1636703925
        },
        "startTimeInSeconds": {
            "type": "Property",
            "value": 1569622560
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
            "value": 1569625700
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "wearable-health-tv/awake_periods"
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
    }
]
```

### Example of a valid NGSI-LD entity for sensor

```json
    {
        "@context": "https://gitlab.com/sferainnovazione/garminconnect/-/raw/staging/VirIoT_fork/Context/context.jsonld",
        "id": "urn:ngsi-ld:clinica1-production-garmin:sensors:paziente14@sferainnovazione.it",
        "type": "sensor",
        "address": {
            "type": "Property",
            "value": "-"
        },
        "createdAtTimestamp": {
            "type": "Property",
            "value": 1636721809
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
        "ownerEmail": {
            "type": "Property",
            "value": "paziente14@sferainnovazione.it"
        },
        "queryDate": {
            "type": "Property",
            "value": 1636721809
        },
        "generatedByVThing": {
            "type": "Property",
            "value": "wearable-health-tv/sensor"
        },
        "status": {
            "type": "Property",
            "value": 0
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