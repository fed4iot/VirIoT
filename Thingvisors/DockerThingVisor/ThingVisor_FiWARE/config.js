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

    isGreedy: true,
    isAggregated: false,
    isGroupingByType: true, //This param will be considered only if isGreedy has true value.

    providerParams: process.env.params,

    commandDestroyTV: 'destroyTV',
    commandDestroyTVAck: 'destroyTVAck',
    commandDeleteVThing: 'deleteVThing',
    commandCreateVThing: 'createVThing',
    commandGetContextRequest: 'getContextRequest',
    commandGetContextResponse: 'getContextResponse',


    commandMappedPort: 'mapped_port', //Code not used, I will remove it when I confirm it's not necessary.

    MQTTbrokerApiKeyvThing: 'vThing',
    MQTTbrokerApiKeySilo: 'vSilo',
    MQTTbrokerApiKeyThingVisor: 'TV',
    
    MQTTbrokerTopicData: 'data',
    MQTTbrokerTopicDataOut: 'data_out',
    MQTTbrokerTopicDataIn: 'data_in',
    
    MQTTbrokerTopic_c_in_Control: 'c_in',
    MQTTbrokerTopic_c_out_Control: 'c_out',
    
    ocb_type: 'parkingsite',
    ocb_attrList: ['numSpacePC','totSpacePCCapacity'],

    dest_ocb_type: 'parkingsite',
    dest_ocb_attrList: ['freeParkingSpaces','totalParkingSpaces','@context','dateCreated','dateModified','timestamp','location'],

    //Greedy Flexible configuration... define 
    greedyListService: ["","prueba"],

    // "/#" --> to recover all servicePath into the service.
    greedyListServicePath: ["/#","/#"],

    // ".*" --> to recover all types into the service/servicepath.
    greedyListTypes: [".*",".*"],

    // ".*" --> to keep the same entity type in Silos.
    greedyListDestTypes: [[".*"],[".*"]],

    // ".*" --> to recover all attributes into the service/servicepath/type.
    greedyListTypesAttributes: [[".*"],[".*"]],

    // ".*" --> to recover all attributes into the service/servicepath/type.
    greedyListDestAttributesTypes: [[".*"],[".*"]],

    frecuency_mseg: 10000
}


