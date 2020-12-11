/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

module.exports = {
    MQTTDataBrokerIP: process.env.MQTTDataBrokerIP,
    MQTTDataBrokerPort: process.env.MQTTDataBrokerPort,
    MQTTControlBrokerIP: process.env.MQTTControlBrokerIP,
    MQTTControlBrokerPort: process.env.MQTTControlBrokerPort,

    tenantID: process.env.tenantID,
    flavourParams: process.env.flavourParams,
    vSiloID: process.env.vSiloID,

    MQTTbrokerUsername: process.env.MQTTbrokerUsername || 'IoTPlatformMQTTUser', 
    MQTTbrokerPassword: process.env.MQTTbrokerPassword || '1234MQTT',
    

    commandDestroyVSilo: 'destroyVSilo',
    commandDestroyVSiloAck: 'destroyVSiloAck',
    commandAddVThing: 'addVThing',
    commandDeleteVThing: 'deleteVThing',
    commandGetContextRequest: 'getContextRequest',
    commandGetContextResponse: 'getContextResponse',


    MQTTbrokerApiKeyvThing: 'vThing',
    MQTTbrokerApiKeySilo: 'vSilo',
    
    MQTTbrokerTopic_c_in_Control: 'c_in',
    MQTTbrokerTopic_c_out_Control: 'c_out',

    MQTTbrokerTopicData: 'data',
    MQTTbrokerTopicDataOut: 'data_out',
    MQTTbrokerTopicDataIn: 'data_in',

    protocolCB: 'http',
    hostCB: 'localhost', 
    portCB: 1026, 
    serviceCB: '',
    servicePathCB: '/',

    portNotification: 1030,
    pathNotification: '/notification',
   
    frecuency_mseg: 10000
}


