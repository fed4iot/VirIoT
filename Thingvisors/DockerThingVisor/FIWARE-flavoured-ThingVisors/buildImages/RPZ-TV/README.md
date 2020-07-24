# License

ThingVisor source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# README

This ThingVisor obtains regulated parking zones information (RPZ) from a FIWARE's Orion Context Broker (OCB) using NGSIv2 API.
The [Test.md](./Test.md) describe how to test the ThingVisor.

## How To Run

### Local Docker deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -i fed4iot/fiware-rpz-tv -n thingVisorID_RPZ -d "thingVisorID_RPZ" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>'}"
```

### Kubernetes deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n thingVisorID_RPZ -d "thingVisorID_RPZ" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>'}" -y "yaml/thingVisor-murcia-rpz.yaml"
```

## NGSI-LD data model

Each parkingmeter obtained from OCB is represented by an NGSI-LD entity like the following one:

```json
{
  "id":"urn:ngsi-ld:parkingmeter:Parquimetro:20",
  "type":"parkingmeter",
  "name":{
    "type":"Property",
    "value":"PUERTA%20NUEVA"
  },
  "parkingProbability":{
    "type":"Property",
    "value":0.399899396
  },
  "sector":{
    "type":"Relationship",
    "object":"urn:ngsi-ld:sector:Sector:1"
  },
  "location":{
    "type":"GeoProperty",
    "value":{
      "type":"Point",
      "coordinates":[-1.128053634,37.99128625]
    }
  },
  "@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
              "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/parkingmeter-context.jsonld"]
}
```

Each sector obtained from OCB is represented by an NGSI-LD entity like the following one:

```json
{
  "id":"urn:ngsi-ld:sector:Sector:1",
  "type":"sector",
  "name":{
    "type":"Property",
    "value":"Sector 1"
  },
  "observedAt":{
    "type":"Property",
    "value":{
      "@type":"DateTime",
      "@value":"2020-07-10T11:47:53Z"
    }
  },
  "policy":{
    "type":"Relationship",
    "object":"urn:ngsi-ld:policy:Parkingmeter"
  },
  "policyPHolidays":{
    "type":"Relationship",
    "object":"urn:ngsi-ld:policy:Parkingmeter"
  },
  "location":{
    "type":"GeoProperty",
    "value":{
      "type":"Polygon",
      "coordinates":[[
        [-1.134584,37.996461],[-1.127803,37.997983],[-1.126236,37.995582],[-1.124928,37.994753],[-1.124348,37.992825],
        [-1.125099,37.991743],[-1.124992,37.989257],[-1.127395,37.989561],[-1.130271,37.989341],[-1.131193,37.990711],
        [-1.131386,37.992098],[-1.134584,37.996461]
      ]]
    }
  },
  "@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
              "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/sector-context.jsonld"]
}
```


Each policy obtained from OCB is represented by an NGSI-LD entity like the following one:

```json
{
  "id":"urn:ngsi-ld:policy:Parkingmeter",
  "type":"policy",
  "appliesDuring":{
    "type":"Property",
    "value":[
      {
        "startTime":"09:00",
        "endTime":"14:00",
        "parkingRateWeekDay":[
          {
            "forDuration":{"minutes":30},
            "fromDuration":1,
            "toDuration":30,
            "monetaryCost":0.15,
            "minParkingCharge":{"minutes":30},
            "maxParkingCost":0.15
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":30,
            "toDuration":60,
            "monetaryCost":0.012,
            "minParkingCharge":0,
            "maxParkingCost":0.35
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":60,
            "toDuration":90,
            "monetaryCost":0.022,
            "minParkingCharge":0,
            "maxParkingCost":0.65
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":90,
            "toDuration":120,
            "monetaryCost":0.02,
            "minParkingCharge":0,
            "maxParkingCost":0.6
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":120,
            "toDuration":150,
            "monetaryCost":0.042,
            "minParkingCharge":0,
            "maxParkingCost":1.25
          }
        ],
        "parkingRateWeekEnd":[
          {
            "forDuration":{"minutes":30},
            "fromDuration":1,
            "toDuration":30,
            "monetaryCost":0.15,
            "minParkingCharge":{"minutes":30},
            "maxParkingCost":0.15
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":30,
            "toDuration":60,
            "monetaryCost":0.012,
            "minParkingCharge":0,
            "maxParkingCost":0.35
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":60,
            "toDuration":90,
            "monetaryCost":0.022,
            "minParkingCharge":0,
            "maxParkingCost":0.65
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":90,
            "toDuration":120,
            "monetaryCost":0.02,
            "minParkingCharge":0,
            "maxParkingCost":0.6
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":120,
            "toDuration":150,
            "monetaryCost":0.042,
            "minParkingCharge":0,
            "maxParkingCost":1.25
          }
        ],
        "parkingRatePHolidays":[],
        "parkingRateWeekDayDis":[],
        "parkingRateWeekEndDis":[],
        "parkingRatePHolidaysDis":[]
      },
      {
        "startTime":"16:30",
        "endTime":"20:00",
        "parkingRateWeekDay":[
          {
            "forDuration":{"minutes":30},
            "fromDuration":1,
            "toDuration":30,
            "monetaryCost":0.15,
            "minParkingCharge":{"minutes":30},
            "maxParkingCost":0.15
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":30,
            "toDuration":60,
            "monetaryCost":0.012,
            "minParkingCharge":0,
            "maxParkingCost":0.35
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":60,
            "toDuration":90,
            "monetaryCost":0.022,
            "minParkingCharge":0,
            "maxParkingCost":0.65
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":90,
            "toDuration":120,
            "monetaryCost":0.02,
            "minParkingCharge":0,
            "maxParkingCost":0.6
          },
          {
            "forDuration":{"minutes":1},
            "fromDuration":120,
            "toDuration":150,
            "monetaryCost":0.042,
            "minParkingCharge":0,
            "maxParkingCost":1.25
          }
        ],
        "parkingRateWeekEnd":[],
        "parkingRatePHolidays":[],
        "parkingRateWeekDayDis":[],
        "parkingRateWeekEndDis":[],
        "parkingRatePHolidaysDis":[]
      }
    ]
  },
  "currency":{"type":"Property","value":"EUR"},
  "exclPHolidays":{"type":"Property","value":false},
  "gracePeriod":{"type":"Property","value":{"minutes":0}},
  "maxDuration":{"type":"Property","value":{"minutes":150}},
  "@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
              "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/policy-context.jsonld"]
}
```