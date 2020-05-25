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
                    "location": { "type": "geo:json", "value": { "type": "Point",  "coordinates": [0,0] } },
                    "@context" : {
                        "type" : "StructuredValue",
                        "value" : [
                            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                            "https://odins.es/smartParkingOntology/rpz-context.jsonld"
/*  Can replace "https://odins.es/smartParkingOntology/parkingsite-context.jsonld" link
                            {
                                "name": "http://purl.org/goodrelations/v1#name" ,
                                "location": "https://schema.org/location"
                            }
*/                            
                        ]
                    }
    }   
}
