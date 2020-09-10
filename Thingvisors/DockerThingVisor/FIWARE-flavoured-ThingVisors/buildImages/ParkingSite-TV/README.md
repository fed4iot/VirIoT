# License

ThingVisor source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# README

This ThingVisor obtains parking sites information from a FIWARE's Orion Context Broker (OCB) using NGSIv2 API.
The [Test.md](./Test.md) describe how to test the ThingVisor.

## How To Run

### Local Docker deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -i fed4iot/fiware-parkingsite-tv -n thingvisorid-parkingsite -d "thingvisorid-parkingsite" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>'}"
```

### Kubernetes deployment

Use the VirIoT CLI as admin and run the following command, you must define OCB endpoint.

```bash  
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n thingvisorid-parkingsite -d "thingvisorid-parkingsite" -p "{'ocb_ip':'<OCB_Public_IP>', 'ocb_port':'<OCB_Port>'}" -y "yaml/thingVisor-murcia-parkingsite.yaml"
```

## NGSI-LD data model

Each parking site obtained from OCB is represented by an NGSI-LD entity like the following one:

```json
{
  "id":"urn:ngsi-ld:parkingsite:Aparcamiento:101",
  "type":"parkingsite",
  "name":{
    "type":"Property",
    "value":"Libertad"
  },
  "observedAt":{
    "type":"Property",
    "value":{
      "@type":"DateTime",
      "@value":"2020-05-13T09:44:07Z"
    }
  },
  "disSpaceMc":{ 
    "type":"Property",
    "value":0
  },
  "disSpaceMcCapacity":{
    "type":"Property",
    "value":0
  },
  "disSpacePC":{
    "type":"Property",
    "value":0
  },
  "disSpacePCCapacity":{
    "type":"Property",
    "value":14
  },
  "EVSpaceMc":{
    "type":"Property",
    "value":0
  },
  "EVSpaceMcCapacity":{
    "type":"Property",
    "value":0
  },
  "EVSpacePC":{
    "type":"Property",
    "value":0
  },
  "EVSpacePCCapacity":{
    "type":"Property",
    "value":0
  },
  "numSpaceMc":{
    "type":"Property",
    "value":0
  },
  "totSpaceMcCapacity":{
    "type":"Property",
    "value":0
  },
  "numSpacePC":{
    "type":"Property",
    "value":"55"
  },
  "totSpacePCCapacity":{
    "type":"Property",
    "value":"330"
  },
  "maxHeight":{
    "type":"Property",
    "value":2.3
  },
  "maxLength":{
    "type":"Property",
    "value":5.1
  },
  "maxWidth":{
    "type":"Property",
    "value":2.3
  },
  "payMthd":{
    "type":"Property",
    "value":["Cash","PayPal"]
  },
  "payMthdCreditCard":{
    "type":"Property",
    "value":["AmericanExpress","Discover","MasterCard","VISA"]
  },
  "policyMc":{
    "type":"Relationship",
    "object":"urn:ngsi-ld:policy:Parkingsite2940"
  },
  "policyPC":{
    "type":"Relationship",
    "object":"urn:ngsi-ld:policy:Parkingsite2940"
  },
  "policyMcPHolidays":{
    "type":"Relationship",
    "object":"urn:ngsi-ld:policy:Parkingsite2940"
  },
  "policyPCPHolidays":{
    "type":"Relationship",
    "object":"urn:ngsi-ld:policy:Parkingsite2940"
  },
  "isOpen":{
    "type":"Property",
    "value":true
  },
  "monday":{
    "type":"Property",
    "value":[{"opens":"00:00","closes":"23:59"}]
  },
  "tuesday":{
    "type":"Property",
    "value":[{"opens":"00:00","closes":"23:59"}]
  },
  "wednesday":{
    "type":"Property",
    "value":[{"opens":"00:00","closes":"23:59"}]
  },
  "thursday":{
    "type":"Property",
    "value":[{"opens":"00:00","closes":"23:59"}]
  },
  "friday":{
    "type":"Property",
    "value":[{"opens":"00:00","closes":"23:59"}]
  },
  "saturday":{
    "type":"Property",
    "value":[{"opens":"00:00","closes":"23:59"}]
  },
  "sunday":{
    "type":"Property",
    "value":[{"opens":"00:00","closes":"23:59"}]
  },
  "pHolidays":{
    "type":"Property",
    "value":[{"opens":"00:00","closes":"23:59"}]
  },
  "carWash":{
    "type":"Property",
    "value":true
  },
  "valet":{
    "type":"Property",
    "value":false
  },
  "EVCharger":{
      "type":"Property",
      "value":{"mediumEVCharger":0,"quickEVCharger":0,"standardEVCharger":0}
  },
  "phoneNumber":{
      "type":"Property",
      "value":[
                {
                  "phoneType":"Work Phone",
                  "countryCode":"34",
                  "areaCode":"968",
                  "contactNumber":"281344"
                }
              ]
  },
  "webSite":{
    "type":"Property",
    "value":"https://aparcamientosnewcapital.es/pf/avenida-libertad-murcia/#info"
  },
  "mail":{
    "type":"Property",
    "value":"info@newcapital2000.es"
  },
  "address":{
      "type":"Property",
      "value":{
                "country":"Spain",
                "state":"Murcia",
                "city":"Murcia",
                "citySection":"San Miguel",
                "streetType":"Avenida",
                "streetDirection":"Libertad",
                "streetNumber":"S/N",
                "postalCode":"30008"
              }
  },
  "location":{
      "type":"GeoProperty",
      "value":{
                "type":"Point",
                "coordinates":[-1.1336517,37.9894006]
              }
  },
  "@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
              "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/parkingsite-context.jsonld"]

}
```


Each policy obtained from OCB is represented by an NGSI-LD entity like the following one:


```json
{
  "id":"urn:ngsi-ld:policy:Parkingsite2940",
  "type":"policy",
  "appliesDuring":{
    "type":"Property",
    "value":[
        {
          "startTime":"00:00",
          "endTime":"23:59",
          "parkingRateWeekDay":[
            {
              "forDuration":{"minutes":1},
              "fromDuration":1,
              "toDuration":300,
              "monetaryCost":0.042,
              "minParkingCharge":{"minutes":5},
              "maxParkingCost":12.6
            },
            {
              "forDuration":{"minutes":1},
              "fromDuration":300,
              "toDuration":720,
              "monetaryCost":0.04,
              "minParkingCharge":{"minutes":0},
              "maxParkingCost":16.8
            },
            {
              "forDuration":{"minutes":1},
              "fromDuration":720,
              "toDuration":1440,
              "monetaryCost":0,
              "minParkingCharge":0,
              "maxParkingCost":0
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
  "currency":{
    "type":"Property",
    "value":"EUR"
  },
  "exclPHolidays":{
    "type":"Property",
    "value":false
  },
  "gracePeriod":{
    "type":"Property",
    "value":{"minutes":5}
  },
  "maxDuration":{
    "type":"Property",
    "value":{"minutes":1440}
  },
  "@context":["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
              "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/policy-context.jsonld"]
}
```