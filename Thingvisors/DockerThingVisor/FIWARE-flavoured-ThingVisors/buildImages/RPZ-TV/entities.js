/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

module.exports = {
    
    parkingsite: {},
    parkingmeter: {
                    "id" : "urn:ngsi-ld:parkingmeter:---",
                    "type" : "parkingmeter",
                    "name": { "type": "Text", "value":"" },
                    "parkingProbability": { "type": "Number", "value": 0 },
                    "sector": {"type": "Relationship", "value": ""  },
                    "location": { "type": "geo:json", "value": { "type": "Point",  "coordinates": [0,0] } },
                    "@context" : {
                        "type" : "StructuredValue",
                        "value" : [
                            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                            "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/parkingmeter-context.jsonld"
                        ]
                    }
    },
    policy: { 
                "id": "urn:ngsi-ld:policy:---",
                "type": "policy",
                "appliesDuring": {
                    "type": "StructuredValue",
                    "value": [
                        {
                            "startTime": "00:00",
                            "endTime": "23:59",
                            "parkingRateWeekDay": [
                                {
                                    "forDuration": { "minutes": 1 },
                                    "fromDuration": 0,
                                    "toDuration": 0,
                                    "monetaryCost": 0,
                                    "minParkingCharge": { "minutes": 0 },
                                    "maxParkingCost": 0
                                }
                            ],
                            "parkingRateWeekEnd": [],
                            "parkingRatePHolidays": [],
                            "parkingRateWeekDayDis": [],
                            "parkingRateWeekEndDis": [],
                            "parkingRatePHolidaysDis": []
                        }
                    ]
                },
                "currency": { "type": "Text", "value": "EUR" },
                "exclPHolidays": { "type": "boolean", "value": false },
                "gracePeriod": {
                    "type": "StructuredValue",
                    "value": { "minutes": 0 }
                },
                "maxDuration": {
                    "type": "StructuredValue",
                    "value": { "minutes": 0 }
                },
                "@context": {
                    "type": "StructuredValue",
                    "value": [
                        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                        "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/policy-context.jsonld"
                    ]
                 }
    },
    sector: {
                "id": "urn:ngsi-ld:sector:---",
                "type": "sector",
                "name": { "type": "Text", "value":"" },
                "timestamp": { "type": "DateTime",  "value": "" },
                "policy": { "type": "Relationship", "value": "" },
                "policyPHolidays": { "type": "Relationship", "value":"" },
                "location": {
                    "type": "geo:json",
                    "value": { "type": "Polygon", "coordinates": [ [  [-1, 1], [-1, -1], [1,-1], [1,1] ] ]
                    }
                },
                "@context": {
                    "type": "StructuredValue",
                    "value": [
                        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                        "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/sector-context.jsonld"
                    ]
                }
    }  
}
