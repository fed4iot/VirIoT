/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

module.exports = {
/*
    port: process.env.PORT || 1030,
    db: process.env.MONGODB || 'mongodb://mongo:27019/fed4Iot',
//    enable_expires: process.env.ENABLE_EXPIRES || 0, actually not supported.
    enable_throttling: process.env.ENABLE_THROTTLING || 0,
    throttling: process.env.THROTTLING || 5,

    notificacion_protocol: process.env.HYPERVISOR_PROTOCOL,
    notificacion_ip: process.env.HYPERVISOR_IP,
    notificacion_port: process.env.HYPERVISOR_PORT,
    pathNotification: '/notification',
    pathNotificationMQTT: '/notificationMQTT',
    pathCreateVirtualEntity: '/createVirtualEntity',
    pathDeleteVirtualEntity: '/deleteVirtualEntity/:identifierID',
    pathDeleteVirtualEntityAll: '/deleteVirtualEntity/all',
    pathList: '/list',
*/  

    notificacion_port_container: '1030',

    pathNotification: '/notification',

//    MQTTbrokerIP: process.env.MQTTbrokerIP,
//    MQTTbrokerPort: process.env.MQTTbrokerPort,

    MQTTDataBrokerIP: process.env.MQTTDataBrokerIP,
    MQTTDataBrokerPort: process.env.MQTTDataBrokerPort,
    MQTTControlBrokerIP: process.env.MQTTControlBrokerIP,
    MQTTControlBrokerPort: process.env.MQTTControlBrokerPort,

    systemDatabaseIP: process.env.systemDatabaseIP,
    systemDatabasePort: process.env.systemDatabasePort,
    
    thingVisorID: process.env.thingVisorID,

    isGreedy: false,
    isAggregated: false,
    isGroupingByType: true, //This param will be considered only if isGreedy has true value.
    vThingLocalIDAggregated: 'parkingsite', //To define the topic to aggregatedValue use case. 

    providerParams: process.env.params,

    commandDestroyTV: 'destroyTV',
    commandDestroyTVAck: 'destroyTVAck',
    commandDeleteVThing: 'deleteVThing',
    commandCreateVThing: 'createVThing',
    commandGetContextRequest: 'getContextRequest',
    commandGetContextResponse: 'getContextResponse',

    // DEPRECATED
    //commandMappedPort: 'mapped_port', //Code not used, I will remove it when I confirm it's not necessary.

    MQTTbrokerApiKeyvThing: 'vThing',
    MQTTbrokerApiKeySilo: 'vSilo',
    MQTTbrokerApiKeyThingVisor: 'TV',
    
    MQTTbrokerTopicData: 'data',
    MQTTbrokerTopicDataOut: 'data_out',
    MQTTbrokerTopicDataIn: 'data_in',
    
    MQTTbrokerTopic_c_in_Control: 'c_in',
    MQTTbrokerTopic_c_out_Control: 'c_out',
    
    // DEPRECATED
    //ocb_type: 'parkingsite',
    //ocb_attrList: ['numSpacePC','totSpacePCCapacity'],
    //dest_ocb_type: 'parkingsite',
    //dest_ocb_attrList: ['freeParkingSpaces','totalParkingSpaces','@context','dateCreated','dateModified','timestamp','location'],

    //Greedy Flexible configuration... define data provider service
    //[] and regular expresions is NO SUPPORTED.
    //noGreedyListService: ['aparcamiento','bicis'],
    //noGreedyListService: ['aparcamiento','ora'],
    noGreedyListService: ['aparcamiento'],

    //Greedy Flexible configuration... define data provider servicePath in service
    //Wildcard : '/#' (to recover all servicePath into the service).
    noGreedyListServicePath: '/#',
    //TODO:
    //Improvement in consideration (NO SUPPORTED):
    //Considerer specific servicepaths in each service : noGreedyListServicePath: [['/murcia','madrid','barcelona'],['/murcia']],

    //Greedy Flexible configuration... define data provider types in service/servicepath
    //[], [''], or regular expresions is NO SUPPORTED.
    //noGreedyListTypes: [['Sensor'],['Sensor']],
    //noGreedyListTypes: [['Sensor','SensorBici'],['SensorTest','SensorBiciTest']],
    noGreedyListTypes: [['Sensor']],
    //noGreedyListTypes: [['Sensor'],['Sensor']],
    //TODO:
    //Improvement in consideration (NO SUPPORTED):
    //Considerer wildcard (all types into the service/servicepath.): noGreedyListTypes: [['.*'],['.*']],

    //Greedy Flexible configuration... define provider attributes list in service/servicepath/type
    //Wildcard : [] (to recover all attributes into the specific service/servicepath/type)
    //noGreedyListTypesAttributes: [[['libres','totales','geoposicion']],[['libres','geoposicion']]],
    //noGreedyListTypesAttributes: [[[],['libres','geoposicion']],[[],['libres','geoposicion']]],
    noGreedyListTypesAttributes: [[['nombre','libres','totales','geoposicion']]],
    //noGreedyListTypesAttributes: [[['nombre','libres','totales','geoposicion']],[[]]],

    //Greedy Flexible configuration... define destiny type for each data provider type
    //[], [''], or regular expresions is NO SUPPORTED.
    //noGreedyListDestTypes: [['parkingsite'],['bikeparkingsite']],
    //noGreedyListDestTypes: [['Sensor','SensorBici'],['parkingsite','parkingsitebike']],
    noGreedyListDestTypes: [['parkingsite']],
    //noGreedyListDestTypes: [['parkingsite'],['Point']],

    //Greedy Flexible configuration... define destiny attribute name for each data provider attributes list in service/servicepath/type
    //[], [''] or regular expresions is NO SUPPORTED.
    //noGreedyListDestAttributesTypes: [[['freeParkingSpaces','totalParkingSpaces','location']],[['freeParkingSpaces','location']]],
    //noGreedyListDestAttributesTypes: [[[],['freeParkingSpaces','location']],[[],['freeParkingSpaces2','location2']]],
    noGreedyListDestAttributesTypes: [[['name','numSpacePC','totSpacePCCapacity','location']]],
    //noGreedyListDestAttributesTypes: [[['name','numSpacePC','totSpacePCCapacity','location']],[[]]],

    /*
    If isGreedy: false, please REVIEW this conditions to a correct configuration:
        - noGreedyListService.length>0
        - noGreedyListService.length == noGreedyListTypes.length == noGreedyListTypesAttributes.length == noGreedyListDestTypes.length == noGreedyListDestAttributesTypes.length
        - noGreedyListTypes[i].length == noGreedyListTypesAttributes[i].length == == noGreedyListDestTypes[i].length == noGreedyListDestAttributesTypes[i].length
	    - noGreedyListTypes[i][k] != [] && noGreedyListTypes[i][k] != ''
	    - noGreedyListDestTypes[i][k] != [] && noGreedyListDestTypes[i][k] != ''
	    - noGreedyyListTypesAttributes[i][k].length == noGreedyListDestAttributesTypes[i][k].length
	    - noGreedyListTypesAttributes[i][k][l] != '' NO SUPPORTED
        - noGreedyListDestAttributesTypes[i][k][l] != '' NO SUPPORTED

    Example configuration (isGreedy: false && isAggregated: false):

        noGreedyListService: ['','test'],
        noGreedyListTypes: [['Sensor','SensorBici'],['SensorTest','SensorBiciTest']],
        noGreedyListTypesAttributes: [[[],['libres','geoposicion']],[[],['libres','geoposicion']]],
        noGreedyListDestTypes: [['Sensor','SensorBici'],['parkingsite','parkingsitebike']],
        noGreedyListDestAttributesTypes: [[[],['freeParkingSpaces','location']],[[],['freeParkingSpaces2','location2']]],

        Actions:

                    FROM  DATA PROVIDER                              |                  TO DATA VSILO
                                                                     |
        SERVICE         TYPE                ATTRIBUTES               |      SERVICE         TYPE                ATTRIBUTES
        ''              'Sensor'            [] --> All               |      '' --> Always   'Sensor'            All with same names
        ''              'SensorBici'        'libres','geoposicion'   |      '' --> Always   'SensorBici'        only 'freeParkingSpaces','location'
        'test'          'SensorTest'        [] --> All               |      '' --> Always   'parkingsite'       All with same names
        'test'          'SensorBiciTest'    'libres','geoposicion'   |      '' --> Always   'parkingsitebike'   only 'freeParkingSpaces2','location2'

    Example configuration (isGreedy: false && isAggregated: true):

        noGreedyListService: ['','test'],
        noGreedyListTypes: [['Sensor'],['SensorTest']],
        noGreedyListTypesAttributes: [[['libres']],[['libres']]],
        noGreedyListDestTypes: [['Sensor'],['SensorTest']],
        noGreedyListDestAttributesTypes: [[['freeParkingSpaces']],[['freeParkingSpaces']]],

        Actions:

                    FROM  DATA PROVIDER                 |       AGGREGATED VALUE PROCESS                  |                TO DATA VSILO
                                                        |                                                 |
        SERVICE         TYPE                ATTRIBUTES  |    TYPE                ATTRIBUTES               |     SERVICE         TYPE            ATTRIBUTES
        ''              'Sensor'            'libres'    |    'Sensor'           only 'freeParkingSpaces'  |    '' --> Always   'parkingsite'   'totalFreeParkingSpaces'
        'test'          'SensorTest'        'libres'    |    'SensorTest'       only 'freeParkingSpaces'  |

    */

    
    smartParkingStandardDM_Service: [''],

    "parkingsite_id": ["Aparcamiento:101","Aparcamiento:102","Aparcamiento:103","Aparcamiento:104","Aparcamiento:105"],
    "parkingsite_disSpacePCCapacity": [14,20,7,0,0],
    "parkingsite_maxHeight": [2.3,2.3,1.9,1.9,2.0],
    "parkingsite_carWash": [true,true,false,false,false],
    "parkingsite_valet": [false,false,false,false,false],
    "parkingsite_phoneNumber": [
                                   [ 
                                       {
                                           "phoneType": "Work Phone",
                                           "countryCode": "34",
                                           "areaCode": "968",
                                           "contactNumber": "281344"
                                       }
                                   ],
                                   [ 
                                       {
                                           "phoneType": "Work Phone",
                                           "countryCode": "34",
                                           "areaCode": "968",
                                           "contactNumber": "200522"
                                       }
                                   ],
                                   [ 
                                       {
                                           "phoneType": "Work Phone",
                                           "countryCode": "34",
                                           "areaCode": "968",
                                           "contactNumber": "234733"
                                       }
                                   ],
                                   [ 
                                       {
                                           "phoneType": "Work Phone",
                                           "countryCode": "34",
                                           "areaCode": "968",
                                           "contactNumber": "235265"
                                       }
                                   ],
                                   [ 
                                       {
                                           "phoneType": "Work Phone",
                                           "countryCode": "34",
                                           "areaCode": "968",
                                           "contactNumber": "204387"
                                       }
                                   ]
                               ],
    "parkingsite_webSite": ["https://aparcamientosnewcapital.es/pf/avenida-libertad-murcia/#info",
                           "https://aparcamientosnewcapital.es/pf/la-vega-murcia/",
                           "https://www.interparking.es/es-ES/find-parking/AlfonsoX/",
                           "https://aparcamientosnewcapital.es/pf/centrofama-murcia/",
                           "https://aparcamientosnewcapital.es/pf/hospital-morales-meseguer-murcia/"],
    "parkingsite_mail": ["info@newcapital2000.es","info@newcapital2000.es","5759@interparking.com","info@newcapital2000.es","info@newcapital2000.es"],
    "parkingsite_address": [
                           {   "country": "Spain",
                               "state": "Murcia",
                               "city": "Murcia",
                               "citySection": "San Miguel", //
                               "streetType": "Avenida",
                               "streetDirection": "Libertad",
                               "streetNumber": "S/N",
                               "postalCode": "30008"
                           },
                           {   "country": "Spain",
                               "state": "Murcia",
                               "city": "Murcia",
                               "citySection": "Santa Maria de Gracia",
                               "streetType": "Avenida",
                               "streetDirection": "Cronista Carlos Valcarcel",
                               "streetNumber": "S/N",
                               "postalCode": "30008"
                           },
                           {   "country": "Spain",
                               "state": "Murcia",
                               "city": "Murcia",
                               "citySection": "La Fama",
                               "streetType": "Avenida",
                               "streetDirection": "Gran Vía Alfonso X",
                               "streetNumber": "S/N",
                               "postalCode": "30008"
                           },
                           {   "country": "Spain",
                               "state": "Murcia",
                               "city": "Murcia",
                               "citySection": "La Fama",
                               "streetType": "Avenida",
                               "streetDirection": "Guitierrez Mellado",
                               "streetNumber": "S/N",
                               "postalCode": "30008"
                           },
                           {   "country": "Spain",
                               "state": "Murcia",
                               "city": "Murcia",
                               "citySection": "Vista Alegre",
                               "streetType": "Avenida",
                               "streetDirection": "Marques de los Vélez",
                               "streetNumber": "S/N",
                               "postalCode": "30008"
                           }
                           ],

    frecuency_mseg: 10000
}