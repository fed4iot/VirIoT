/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

module.exports = {
    
    parkingsite: {
                    "id" : "urn:ngsi-ld:parkingsite:---",
                    "type" : "parkingsite",
                    "name": { "type": "Text", "value":"" },

                    "timestamp": { "type": "DateTime",  "value": "" },

                    "disSpaceMc": { "type": "Number", "value": 0 },
                    "disSpaceMcCapacity": { "type": "Number", "value": 0 },
                    "disSpacePC": { "type": "Number", "value": 0 },
                    "disSpacePCCapacity": { "type": "Number", "value": 0 },
                    "EVSpaceMc": { "type": "Number", "value": 0 },
                    "EVSpaceMcCapacity": { "type": "Number", "value": 0 },
                    "EVSpacePC": { "type": "Number", "value": 0 },
                    "EVSpacePCCapacity": { "type": "Number", "value": 0 },
                    "numSpaceMc": { "type": "Number", "value": 0 },
                    "totSpaceMcCapacity": { "type": "Number", "value": 0 },
                    "numSpacePC" : { "type":"Number", "value": 0 },
                    "totSpacePCCapacity" : { "type": "Number", "value": 0 },

                    "maxHeight": {"type": "Number", "value": 1.80 },
                    "maxLength": {"type": "Number", "value": 5.10 },
                    "maxWidth": {"type": "Number", "value": 2.30 },

                    "payMthd": { "type": "StructuredValue", "value": [ "Cash", "PayPal"] },
                    "payMthdCreditCard": { "type": "StructuredValue", "value": ["AmericanExpress","Discover","MasterCard","VISA"] },

                    "policyMc": { "type": "Relationship", "value": "" },
                    "policyPC": { "type": "Relationship", "value": "" },
                    "policyMcPHolidays": { "type": "Relationship", "value": "" },
                    "policyPCPHolidays": { "type": "Relationship", "value": "" },

                    "isOpen": { "type": "boolean", "value": true},
                    "monday": { "type": "StructuredValue", "value": [ { "opens": "00:00", "closes": "23:59" } ] },
                    "tuesday": { "type": "StructuredValue", "value": [ { "opens": "00:00", "closes": "23:59" } ] },
                    "wednesday": { "type": "StructuredValue", "value": [ { "opens": "00:00", "closes": "23:59" } ] },
                    "thursday": { "type": "StructuredValue", "value": [ { "opens": "00:00", "closes": "23:59" } ] },
                    "friday": { "type": "StructuredValue", "value": [ { "opens": "00:00", "closes": "23:59" } ] },
                    "saturday": { "type": "StructuredValue", "value": [ { "opens": "00:00", "closes": "23:59" } ] },
                    "sunday": { "type": "StructuredValue", "value": [ { "opens": "00:00", "closes": "23:59" } ] },
                    "pHolidays": { "type": "StructuredValue", "value": [ { "opens": "00:00", "closes": "23:59" } ] },

                    "carWash": { "type": "boolean", "value": true},
                    "valet": { "type": "boolean", "value": true},
                    "EVCharger": { "type": "StructuredValue", "value": { "mediumEVCharger": 0, "quickEVCharger": 0, "standardEVCharger": 0 } },

                    "phoneNumber": { "type": "StructuredValue", 
                                    "value": [ 
                                               {
                                                "phoneType": "",
                                                "countryCode": "",
                                                "areaCode": "",
                                                "contactNumber": ""
                                                }
                                           ] 
                                    },
                    "webSite": { "type": "Text", "value": "" },
                   
                    "mail": { "type": "Text", "value": "" },

                    "address": { "type": "StructuredValue", 
                                "value": {  
                                            "country": "",
                                            "state": "",
                                            "city": "",
                                            "citySection": "",
                                            "streetType": "",
                                            "streetDirection": "",
                                            "streetNumber": "",
                                            "postalCode": ""
                                        } 
                                },
                    "location": { "type": "geo:json", "value": { "type": "Point",  "coordinates": [0,0] } },

                    "@context" : {
                        "type" : "StructuredValue",
                        "value" : [
                            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                            "https://gitlab.com/Odins/fed4iot/contextfiles/-/blob/master/parkingsite-context.jsonld"
                        ]
                    }
    },
    parkingmeter: {},
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
    sector: {}
}
