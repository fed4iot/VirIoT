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
/*
                    "policyMc": {
                        "type": "RelationShip",
                        "object": "urn:ngsi-ld:policy:Aparcamiento:101:Motorcycle"
                    },
                    "policyPC": {
                        "type": "RelationShip",
                        "object": "urn:ngsi-ld:policy:Aparcamiento:101:PrivateCar"
                    },
                    "policyMcPHolidays": {
                        "type": "RelationShip",
                        "object": "urn:ngsi-ld:policy:Aparcamiento:101:MotorcyclePublicHoliday"
                    },
                    "policyPCPHolidays": {
                        "type": "RelationShip",
                        "object": "urn:ngsi-ld:policy:Aparcamiento:101:PrivateCarPublicHoliday"
                    },
*/
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
/*
                    "forzado": {
                        "type": "Property",
                        "value": "0"
                    },
*/
                    "phoneNumber": { "type": "StructuredValue", "value": { } },
                    "webSite": { "type": "Text", "value": "" },
                   
                    "mail": { "type": "Text", "value": "" },
                    "address": { "type": "StructuredValue", "value": { } },
                    "location": { "type": "geo:json", "value": { "type": "Point",  "coordinates": [] } },

                    "@context" : {
                        "type" : "StructuredValue",
                        "value" : [
                            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                            "https://odins.es/smartParkingOntology/parkingsite-context.jsonld"
/* Can replace "https://odins.es/smartParkingOntology/parkingsite-context.jsonld" link
                            {
                                "name" : "http://purl.org/goodrelations/v1#name",
                                //**********Places&Occupancy**********
                                "disSpaceMc" : "http://ontology.eil.utoronto.ca/icity/Parking/hasNumDisSpaceMotorcycle",
                                "disSpaceMcCapacity" : "http://ontology.eil.utoronto.ca/icity/Parking/hasVehicleCapacity",
                                "disSpacePC" : "http://ontology.eil.utoronto.ca/icity/Parking/hasNumDisSpacePrivateCar",
                                "disSpacePCCapacity" : "http://ontology.eil.utoronto.ca/icity/Parking/hasVehicleCapacity",
                                "EVSpaceMc" : "http://ontology.eil.utoronto.ca/icity/Parking/hasNumEVSpaceMotorcycle",
                                "EVSpaceMcCapacity" : "http://ontology.eil.utoronto.ca/icity/Parking/hasVehicleCapacity",
                                "EVSpacePC" : "http://ontology.eil.utoronto.ca/icity/Parking/hasNumEVSpacePrivateCar",
                                "EVSpacePCCapacity" : "http://ontology.eil.utoronto.ca/icity/Parking/hasVehicleCapacity",
                                "numSpaceMc" : "http://ontology.eil.utoronto.ca/icity/Parking/hasNumSpaceMotorcycle",
                                "totSpaceMcCapacity" : "http://ontology.eil.utoronto.ca/icity/Parking/hasVehicleCapacity",
                                "numSpacePC" : "http://ontology.eil.utoronto.ca/icity/Parking/hasNumSpacePrivateCar",
                                "totSpacePCCapacity" : "http://ontology.eil.utoronto.ca/icity/Parking/hasVehicleCapacity",
                                //**********Maximumdimensions**********
                                "maxHeight" : "http://ontology.eil.utoronto.ca/icity/Parking/maxAdmittableHeight",
                                "maxLength" : "http://ontology.eil.utoronto.ca/icity/Parking/maxAdmittableLength",
                                "maxWidth" : "http://ontology.eil.utoronto.ca/icity/Parking/maxAdmittableWidth",
                                //**********AcceptedPaymentMethods**********
                                "payMthd" : "http://purl.org/goodrelations/v1#acceptedPaymentMethods",
                                "payMthdCreditCard" : "http://purl.org/goodrelations/v1#acceptedPaymentMethods",
                                //**********Policy&Rate**********
//                                "policyMc" : "http://ontology.eil.utoronto.ca/icity/Parking/ParkingPolicy",
//                                "policyPC" : "http://ontology.eil.utoronto.ca/icity/Parking/ParkingPolicy",
//                                "policyMcPHolidays" : "http://ontology.eil.utoronto.ca/icity/Parking/ParkingPolicy",
//                                "policyPCPHolidays" : "http://ontology.eil.utoronto.ca/icity/Parking/ParkingPolicy",
                                
                                //**********Openhours**********
                                "isOpen" : "http://ontology.eil.utoronto.ca/icity/Parking/isOpen",
                                "monday" : "http://purl.org/goodrelations/v1#Monday",
                                "tuesday" : "http://purl.org/goodrelations/v1#Tuesday",
                                "wednesday" : "http://purl.org/goodrelations/v1#Wednesday",
                                "thursday" : "http://purl.org/goodrelations/v1#Thursday",
                                "friday" : "http://purl.org/goodrelations/v1#Friday",
                                "saturday" : "http://purl.org/goodrelations/v1#Saturday",
                                "sunday" : "http://purl.org/goodrelations/v1#Sunday",
                                "opens" : "http://purl.org/goodrelations/v1#opens",
                                "closes" : "http://purl.org/goodrelations/v1#closes",
                                "pHolidays" : "http://purl.org/goodrelations/v1#PublicHolidays",
                                
                                //**********Services**********
                                "carWash" : "http://ontology.eil.utoronto.ca/icity/Parking/CarWash",
                                "valet" : "http://ontology.eil.utoronto.ca/icity/Parking/Valet",
                                "EVCharger" : "http://ontology.eil.utoronto.ca/icity/Parking/EVCharger",
                                "mediumEVCharger" : "http://ontology.eil.utoronto.ca/icity/Parking/MediumEVCharger",
                                "quickEVCharger" : "http://ontology.eil.utoronto.ca/icity/Parking/QuickEVCharger",
                                "standardEVCharger" : "http://ontology.eil.utoronto.ca/icity/Parking/StandardEVCharger",
                                
//                                "forzado" : "https://odins.es/smartParkingOntology/parkingProbability",
                                
                                //**********Contacts**********
                                "phoneNumber" : "http://ontology.eil.utoronto.ca/icontact.owl#PhoneNumber",
                                "phoneType" : "http://ontology.eil.utoronto.ca/icontact.owl#hasPhoneType",
                                "areaCode" : "http://ontology.eil.utoronto.ca/icontact.owl#hasAreaCode",
                                "countryCode" : "http://ontology.eil.utoronto.ca/icontact.owl#hasCountryCode",
                                "contactNumber" : "http://ontology.eil.utoronto.ca/icontact.owl#hasPhoneNumber",
                                "webSite" : "http://ontology.eil.utoronto.ca/icontact.owl#hasWebSite",
                                "mail" : "http://ontology.eil.utoronto.ca/icontact.owl#hasEmail",
                                
                                //**********Location**********
                                "address" : "http://ontology.eil.utoronto.ca/icontact.owl#Address",
                                "country" : "http://ontology.eil.utoronto.ca/icontact.owl#hasCountry",
                                "state" : "http://ontology.eil.utoronto.ca/icontact.owl#hasState",
                                "city" : "http://ontology.eil.utoronto.ca/icontact.owl#hasCity",
                                "citySection" : "http://ontology.eil.utoronto.ca/icontact.owl#hasCitySection",
                                "streetType" : "http://ontology.eil.utoronto.ca/icontact.owl#hasStreetType",
                                "streetDirection" : "http://ontology.eil.utoronto.ca/icontact.owl#hasStreetDirection",
                                "streetNumber" : "http://ontology.eil.utoronto.ca/icontact.owl#hasStreetNumber",
                                "postalCode" : "http://ontology.eil.utoronto.ca/icontact.owl#hasPostalCode",
                                "location" : "https://schema.org/location"
                                }
*/                                
                        ]
                    }
    },
    parkingmeter: {}   
}
