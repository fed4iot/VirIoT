/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

module.exports = {
    notificacion_port_container: '1030',

    pathNotification: '/notification',

    MQTTDataBrokerIP: process.env.MQTTDataBrokerIP,
    MQTTDataBrokerPort: process.env.MQTTDataBrokerPort,
    MQTTControlBrokerIP: process.env.MQTTControlBrokerIP,
    MQTTControlBrokerPort: process.env.MQTTControlBrokerPort,

    systemDatabaseIP: process.env.systemDatabaseIP,
    systemDatabasePort: process.env.systemDatabasePort,
    
    thingVisorID: process.env.thingVisorID,

    isGreedy: false,
    isAggregated: false,
    //isGroupingByType: true,
    isActuator: false, //This param will be considered only if isGreedy and isAggregated have false value.
    vThingLocalIDAggregated: 'parkingsite', //To define the topic to aggregatedValue use case. 

    providerParams: process.env.params,

    commandDestroyTV: 'destroyTV',
    commandDestroyTVAck: 'destroyTVAck',
    commandDeleteVThing: 'deleteVThing',
    commandCreateVThing: 'createVThing',
    commandGetContextRequest: 'getContextRequest',
    commandGetContextResponse: 'getContextResponse',

    MQTTbrokerApiKeyvThing: 'vThing',
    MQTTbrokerApiKeySilo: 'vSilo',
    MQTTbrokerApiKeyThingVisor: 'TV',
    
    MQTTbrokerTopicData: 'data',
    MQTTbrokerTopicDataOut: 'data_out',
    MQTTbrokerTopicDataIn: 'data_in',
    
    MQTTbrokerTopic_c_in_Control: 'c_in',
    MQTTbrokerTopic_c_out_Control: 'c_out',
    
    //Greedy Flexible configuration... define data provider service
    //[] and regular expresions is NO SUPPORTED.
    //noGreedyListService: ['aparcamiento','bicis'],
    //noGreedyListService: ['aparcamiento','ora'],
    noGreedyListService: ['ora'],

    //Greedy Flexible configuration... define data provider servicePath in service
    //Wildcard : '/#' (to recover all servicePath into the service), no use '/#' in actuator TV.
    //noGreedyListServicePath: ['/#'],
    //TODO:
    //Improvement in consideration (NO SUPPORTED):
    //Considerer specific servicepaths in each service : noGreedyListServicePath: [['/murcia','madrid','barcelona'],['/murcia']],

    //Greedy Flexible configuration... define data provider types in service/servicepath
    //[], [''], or regular expresions is NO SUPPORTED.
    //noGreedyListTypes: [['Sensor'],['Sensor']],
    //noGreedyListTypes: [['Sensor','SensorBici'],['SensorTest','SensorBiciTest']],
    noGreedyListTypes: [['Punto','policy','Sector']],
    //noGreedyListTypes: [['Sensor'],['Sensor']],
    //TODO:
    //Improvement in consideration (NO SUPPORTED):
    //Considerer wildcard (all types into the service/servicepath.): noGreedyListTypes: [['.*'],['.*']],

    //Greedy Flexible configuration... define provider attributes list in service/servicepath/type
    //Wildcard : [] (to recover all attributes into the specific service/servicepath/type)
    //noGreedyListTypesAttributes: [[['libres','totales','geoposicion']],[['libres','geoposicion']]],
    //noGreedyListTypesAttributes: [[[],['libres','geoposicion']],[[],['libres','geoposicion']]],
    noGreedyListTypesAttributes: [[
                                    ['nombre','parkingProbability','sector','geoposicion'],  //Punto attributes to map
                                    ['appliesDuring','currency','exclPHolidays','gracePeriod','maxDuration'],  //policy attributes to map
                                    ['name','libres','capacidad','policy','policyPHolidays','area'] //sector attributes to map
                                ]],
    //noGreedyListTypesAttributes: [[['nombre','libres','totales','geoposicion']],[[]]],

    //Greedy Flexible configuration... define destiny type for each data provider type
    //[], [''], or regular expresions is NO SUPPORTED.
    //noGreedyListDestTypes: [['parkingsite'],['bikeparkingsite']],
    //noGreedyListDestTypes: [['Sensor','SensorBici'],['parkingsite','parkingsitebike']],
    noGreedyListDestTypes: [['parkingmeter','policy','sector']],
    //noGreedyListDestTypes: [['parkingsite'],['Point']],

    //Greedy Flexible configuration... define destiny attribute name for each data provider attributes list in service/servicepath/type
    //[], [''] or regular expresions is NO SUPPORTED.
    //noGreedyListDestAttributesTypes: [[['freeParkingSpaces','totalParkingSpaces','location']],[['freeParkingSpaces','location']]],
    //noGreedyListDestAttributesTypes: [[[],['freeParkingSpaces','location']],[[],['freeParkingSpaces2','location2']]],
    noGreedyListDestAttributesTypes: [[
                                        ['name','parkingProbability','sector','location'], //parkingmeter attributes mapped
                                        ['appliesDuring','currency','exclPHolidays','gracePeriod','maxDuration'], //policy attributes mapped
                                        ['name','numSpace','numSpaceCapacity','policy','policyPHolidays','location'] //sector attributes to mapped
                                    ]],
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

    frecuency_mseg: 10000
}