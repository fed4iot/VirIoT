/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

'use strict'

const app = require('./app')

const config = require('./config')

var orion = require("./orion");

const axios = require('axios');

var util = require("./util")

var libfromNGSILD = require("./fromNGSILD")

var mqtt = require('mqtt')

var vThingList = []

//var MQTTbrokerIP
//var MQTTbrokerPort

var MQTTDataBrokerIP
var MQTTDataBrokerPort
var MQTTControlBrokerIP
var MQTTControlBrokerPort

var tenantID
var flavourParams
var vSiloID

var MQTTbrokerApiKeyvThing
var MQTTbrokerApiKeySilo
var MQTTbrokerTopic_c_in_Control
var MQTTbrokerTopic_c_out_Control
var MQTTbrokerTopicData
var MQTTbrokerTopicDataOut
var MQTTbrokerTopicDataIn

var protocolCB
var hostCB
var portCB
var serviceCB
var servicePathCB

var portNotification
var pathNotification

var MQTTbrokerUsername
var MQTTbrokerPassword

var commandDestroyVSilo
var commandDestroyVSiloAck
var commandAddVThing
var commandDeleteVThing
var commandGetContextRequest
var commandGetContextResponse

//var mqttSubscriptionList = []
var mqttSubscriptionListData = []
var mqttSubscriptionListControl = []

//var options
var optionsData
var optionsControl

//var clientMosquittoMqtt
var clientMosquittoMqttData
var clientMosquittoMqttControl

var subscriptionIdOCBCommandAttributeList = []

var urlCB
var urlConsumerServerNotification

console.log("")
console.log("")
console.log("**********" + util.unixTime(Date.now()) + " ***************")

//Processing environment variables...
try {

    //MQTTbrokerIP = config.MQTTbrokerIP
    //MQTTbrokerPort = config.MQTTbrokerPort 

    MQTTDataBrokerIP = config.MQTTDataBrokerIP,
    MQTTDataBrokerPort = config.MQTTDataBrokerPort,
    MQTTControlBrokerIP = config.MQTTControlBrokerIP,
    MQTTControlBrokerPort = config.MQTTControlBrokerPort,

    tenantID = config.tenantID
    flavourParams = config.flavourParams
    vSiloID = config.vSiloID
    MQTTbrokerApiKeyvThing = config.MQTTbrokerApiKeyvThing
    MQTTbrokerApiKeySilo = config.MQTTbrokerApiKeySilo
    MQTTbrokerTopic_c_in_Control = config.MQTTbrokerTopic_c_in_Control
    MQTTbrokerTopic_c_out_Control = config.MQTTbrokerTopic_c_out_Control
    MQTTbrokerTopicData = config.MQTTbrokerTopicData
    MQTTbrokerTopicDataOut = config.MQTTbrokerTopicDataOut
    MQTTbrokerTopicDataIn = config.MQTTbrokerTopicDataIn

    protocolCB = config.protocolCB
    hostCB = config.hostCB
    portCB = config.portCB
    serviceCB = config.serviceCB
    servicePathCB = config.servicePathCB

    portNotification = config.portNotification
    pathNotification = config.pathNotification

    urlCB = protocolCB + '://' + hostCB + ':' + portCB
    urlConsumerServerNotification = protocolCB + '://' + hostCB + ':' + portNotification + pathNotification

    MQTTbrokerUsername = config.MQTTbrokerUsername || ''
    MQTTbrokerPassword = config.MQTTbrokerPassword || ''
    
    commandDestroyVSilo = config.commandDestroyVSilo
    commandDestroyVSiloAck = config.commandDestroyVSiloAck
    commandAddVThing = config.commandAddVThing
    commandDeleteVThing = config.commandDeleteVThing
    commandGetContextRequest = config.commandGetContextRequest
    commandGetContextResponse = config.commandGetContextResponse

    if (MQTTDataBrokerIP == '' || typeof MQTTDataBrokerIP === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'MQTTDataBrokerIP' param not found.")
        return
    }

    if (MQTTDataBrokerPort == '' || typeof MQTTDataBrokerPort === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'MQTTDataBrokerPort' param not found.")
        return
    }

    if (MQTTControlBrokerIP == '' || typeof MQTTControlBrokerIP === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'MQTTControlBrokerIP' param not found.")
        return
    }

    if (MQTTControlBrokerPort == '' || typeof MQTTControlBrokerPort === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'MQTTControlBrokerPort' param not found.")
        return
    }


    //Options MQTT connection
    optionsControl = {
        clean: false,
        clientId: 'mqttjs_' + Math.random().toString(16).substr(2, 8), // Aleatory
        username: MQTTbrokerUsername, //optional
        password: MQTTbrokerPassword, //optional
    };

    optionsData = {
        clean: false,
        clientId: 'mqttjs_' + Math.random().toString(16).substr(2, 8), // Aleatory
        username: MQTTbrokerUsername, //optional
        password: MQTTbrokerPassword, //optional
    };

} catch(e) {
    console.error("Error - processing Silos's environment variables: " + e)
    return
}

//Connecting to MQTT-server...

try {
    
    clientMosquittoMqttControl = mqtt.connect("mqtt://" + MQTTControlBrokerIP + ":" + MQTTControlBrokerPort,optionsControl);

    clientMosquittoMqttData = mqtt.connect("mqtt://" + MQTTDataBrokerIP + ":" + MQTTDataBrokerPort,optionsData);

} catch(e) {
    console.error("Error - connecting MQTT-server...: " + e)
    return 
}

//Mapping connect function
clientMosquittoMqttControl.on("connect", async function() {
    try {
        console.log("")
        console.log(util.unixTime(Date.now()) + " - MQTT Control Broker connected")
        //Establishing topic's subscriptions

        var topicArray = []
        var topicElement = MQTTbrokerApiKeySilo + "/" + vSiloID + "/" + MQTTbrokerTopic_c_in_Control
        
        //"/vSilo/tenantID_vSiloID/c_in" topic
        topicArray.push(topicElement)

        const response_subscribeMQTT = await subscribeMQTT(topicArray,'0',vSiloID,"control")

        if (response_subscribeMQTT == false) {
            console.error("Error - connecting MQTT-server: Can't subscribe topics.")
            return
        } else {

            //Push into mqttSubscriptionListControl array new topic subscriptions array
            if (findArrayElement(mqttSubscriptionListControl,topicElement) == false) {
                mqttSubscriptionListControl = mqttSubscriptionListControl.concat(topicArray)    
            }
            //mqttSubscriptionListControl = mqttSubscriptionListControl.concat(topicArray)

            console.log("")
            console.log("MQTT Control Subscription Topic List: ")
            console.log(mqttSubscriptionListControl)
        }
    } catch (error) {
      console.error(error.toString());
      return;
    }
})

//Mapping error function
clientMosquittoMqttControl.on("error", function(error) {
    try {
        clientMosquittoMqttControl.reconnect()
    } catch (error) {
      console.error(error.toString());
      return;
    }
})

//Mapping reconnect function
clientMosquittoMqttControl.on("reconnect", function() {
    try {
        console.log(util.unixTime(Date.now()) + " - Reconnect clientMosquittoMqttControl")
    } catch (error) {
      console.error(error.toString());
      return;
    }
})

//Mapping topic's subscriptions function
clientMosquittoMqttControl.on("message", async function(topic, payload) {
    try {

        //Processing topic's message
        var topicLevelLength = topic.split("/").length
        var topicLevelElement = []

        for(var k = 0; k < topicLevelLength;k++) {
            topicLevelElement[k]=topic.split("/")[k]
        }
        
        var centralElement = ""
        
        for(var k = 1; k < topicLevelLength-1;k++) {

            if (centralElement.length==0) {
                centralElement = topic.split("/")[k]    
            } else {
                centralElement = centralElement + "/" + topic.split("/")[k]    
            }
        }
        
        console.log("");
        console.log(util.unixTime(Date.now()) + " - Received topic: " + topic + " ; payload: " + payload.toString());

        //console.log("")
        //console.log("")
        //console.log("******* " + util.unixTime(Date.now()) + " ********")
        //console.log("topic: " + topic)
        //console.log("payload: " + payload)
        //console.log("typeof payload: " + typeof payload)
                    
        //Processing topic's message
        if (topicLevelElement[0]==MQTTbrokerApiKeySilo && centralElement==vSiloID && topicLevelElement[topicLevelLength-1]==MQTTbrokerTopic_c_in_Control) {
            //Handling "/vSilo/tenantID_vSiloID/c_in" message
            //console.log("Handling c_in message")

            //const payLoadObject = JSON.parse(payload.toString());
            const payLoadObject = JSON.parse(payload.toString().replace(/'/g, '"'));

            if (payLoadObject.command==commandDestroyVSilo) {
                //destroyVSilo command example  {"command": "destroyVSilo", "vSiloID": vSiloID}
                //console.log("Handling destroyVSilo command")
                
                const responseShutdown = await shutdown(0)

            } else if (payLoadObject.command==commandAddVThing) {
                //addVThing payload example: {"command": "addVThing", "vSiloID": v_silo_id, "vThingID": v_thing_id}
                //console.log("Handling addVThing command")
                
                //Obtain vThingID from payload
                const vThingID = payLoadObject.vThingID

                try {
                    //Establishing topic's subscriptions
                    var topicArray = []
                    var topicElement = MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopicDataOut

                    //"/vThing/vThingID/data_out" topic
                    //topicArray.push(MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopicData)
                    //topicArray.push(MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopicDataOut)
                    topicArray.push(topicElement)
                    
                    const response_subscribeMQTTData = await subscribeMQTT(topicArray,'1',vThingID,"data")

                    if (response_subscribeMQTTData) {
                        
                        //Push into mqttSubscriptionListData array new topic subscriptions array
                        if (findArrayElement(mqttSubscriptionListData,topicElement) == false) {
                            mqttSubscriptionListData = mqttSubscriptionListData.concat(topicArray)    
                        }
                        //mqttSubscriptionListData = mqttSubscriptionListData.concat(topicArray)

                        //console.log('Operation has been completed successfully');
                        
                        var topicArray = []
                        var topicElement = MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopic_c_out_Control

                        //"/vThing/vThingID/out_control" topic
                        //topicArray.push(MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopic_c_out_Control)
                        topicArray.push(topicElement)

                        const response_subscribeMQTTControl = await subscribeMQTT(topicArray,'1',vThingID,"control")

                        if (response_subscribeMQTTControl) {

                            //Push into mqttSubscriptionListControl array new topic subscriptions array
                            if (findArrayElement(mqttSubscriptionListControl,topicElement) == false) {
                                mqttSubscriptionListControl = mqttSubscriptionListControl.concat(topicArray)    
                            }
                            //mqttSubscriptionListControl = mqttSubscriptionListControl.concat(topicArray)

                            console.log("MQTT Data Subscription Topic List: ")
                            console.log(mqttSubscriptionListData)
                            console.log("MQTT Control Subscription Topic List: ")
                            console.log(mqttSubscriptionListControl)

                            //Send sendGetContextRequest
                            const sendGetContextRequestResponse = await sendGetContextRequest(vThingID)

                            if (sendGetContextRequestResponse) {
                                //console.log('Operation has been completed successfully');
                            } else {
                                console.error("Creation fails.")
                            }
                            
                            //console.log('Operation has been completed successfully');

                        } else {
                            console.error("Creation fails.")
                        }


                    } else {
                        console.error("Creation fails.")
                    }

                } catch(e) {
                    console.error("Creation fails: " + e.toString());
                }

            } else if (payLoadObject.command==commandDeleteVThing) {
                //deleteVThing payload format example:  {"command": "deleteVThing", "vSiloID": v_silo_id, "vThingID": v_thing_id}
                //console.log("Handling deleteVThing command (Silos : VThing)")

                //Obtain vThingID from payload
                const vThingID = payLoadObject.vThingID

                try {

                    const delete_vThingResponse = await delete_vThing(vThingID,urlCB)

                    if (delete_vThingResponse) {
                        //console.log('Operation has been completed successfully');
                    } else {
                        console.error("Delete fails.")
                    }

                } catch(e) {
                    console.error("Delete fails: " + e.toString());
                }

            } else if (payLoadObject.command==commandGetContextResponse) {
                //getContextResponse command example {"command": "getContextResponse", "data": [OCB_entities], "meta": {"vThingID": vThingID}}
                //console.log("Handling commandGetContextResponse")

                //Processing entities... Create/Update Orion Context Broker entity & store track vThingID - vThingLD.
                
                /*console.log("payLoadObject.data")
                console.log(payLoadObject.data)
                console.log("payLoadObject.data.length")
                console.log(payLoadObject.data.length)*/

                for(var j = 0; j < payLoadObject.data.length;j++) {
                    try {
                        //const append_vThingResponse = await appendCBEntity(libfromNGSILD.fromNGSILDtoNGSI(payLoadObject.data[j],"v2",""),urlCB,payLoadObject.meta.vThingID)

                        var payLoadObjectNGSIv2 = {}

                        var payLoadObjectNGSIv2 = libfromNGSILD.fromNGSILDtoNGSI(payLoadObject.data[j],"v2","")

                        console.log(payLoadObjectNGSIv2)

                        const processedEntities = await processNGSIv2Payload(payLoadObjectNGSIv2)

                        //console.log(processedEntities)

                        const append_vThingResponse = await appendCBEntity(processedEntities,urlCB,payLoadObject.meta.vThingID)
        
                        if (append_vThingResponse) {
                            //console.log('Operation has been completed successfully');
                        } else {
                            console.error("Create/Update fails.")
                        }
        
                    } catch(e) {
                        console.error("Create/Update: " + e.toString());
                    }
                }

                console.log("vThing List after 'GetContextResponse': ")
                console.log(vThingList)

            } else {
                console.error("invalid command (" + payLoadObject.command + ") in topic '" + topic + "'");
            }
        } else if (topicLevelElement[0]==MQTTbrokerApiKeyvThing && topicLevelElement[topicLevelLength-1]==MQTTbrokerTopic_c_out_Control) {   
            //Handling /vThing/vThingID/c_out
            //console.log("Handling out_control message")

            //const payLoadObject = JSON.parse(payload.toString());
            const payLoadObject = JSON.parse(payload.toString().replace(/'/g, '"'));
            

            if (payLoadObject.command==commandDeleteVThing) {
                //delete payload format example:  {"command": "deleteVThing", "vThingID": v_thing_id "vSiloID": "ALL"}
                //console.log("Handling deleteVThing command (TV : VThing)")

                //Obtain vThingID from payload
                const vThingID = payLoadObject.vThingID

                try {

                    const delete_vThingResponse = await delete_vThing(vThingID,urlCB)

                    if (delete_vThingResponse) {
                        //console.log('Operation has been completed successfully');
                    } else {
                        console.error("Delete fails.")
                    }

                } catch(e) {
                    console.error("Delete fails: " + e.toString());
                }

            } else {
                console.error("invalid command (" + payLoadObject.command + ") in topic '" + topic + "'");            
            }

        } else {
            console.error("invalid topic: '" + topic + "'");            
        }
        return;
    } catch(e) {
        console.error(e.toString());
        return;
    }
})


//Mapping connect function
clientMosquittoMqttData.on("connect", async function() {
    try {
        console.log("")
        console.log(util.unixTime(Date.now()) + " - MQTT Data Broker connected")
        //Establishing topic's subscriptions

        var topicArray = []
        var topicElement = MQTTbrokerApiKeySilo + "/" + vSiloID + "/" + MQTTbrokerTopicDataIn
        
        //"/vSilo/tenantID_vSiloID/data_in" topic
        topicArray.push(topicElement)

        const response_subscribeMQTT = await subscribeMQTT(topicArray,'0',vSiloID,"data")

        if (response_subscribeMQTT == false) {
            console.error("Error - connecting MQTT-server: Can't subscribe topics.")
            return
        } else {

            //Push into mqttSubscriptionListData array new topic subscriptions array
            if (findArrayElement(mqttSubscriptionListData,topicElement) == false) {
                mqttSubscriptionListData = mqttSubscriptionListData.concat(topicArray)    
            }
            //mqttSubscriptionListData = mqttSubscriptionListData.concat(topicArray)

            console.log("")
            console.log("MQTT Data Subscription Topic List: ")
            console.log(mqttSubscriptionListData)
        }

    } catch (error) {
      console.error(error.toString());
      return;
    }
})

//Mapping error function
clientMosquittoMqttData.on("error", function(error) {
    try {
        clientMosquittoMqttData.reconnect()
    } catch (error) {
      console.error(error.toString());
      return;
    }
})

//Mapping reconnect function
clientMosquittoMqttData.on("reconnect", function() {
    try {
        console.log(util.unixTime(Date.now()) + " - Reconnect clientMosquittoMqttData")
    } catch (error) {
      console.error(error.toString());
      return;
    }
})


//Mapping topic's subscriptions function
clientMosquittoMqttData.on("message", async function(topic, payload) {
    try {

        //Processing topic's message
        var topicLevelLength = topic.split("/").length
        var topicLevelElement = []

        for(var k = 0; k < topicLevelLength;k++) {
            topicLevelElement[k]=topic.split("/")[k]
        }
       
        var centralElement = ""
        
        for(var k = 1; k < topicLevelLength-1;k++) {

            if (centralElement.length==0) {
                centralElement = topic.split("/")[k]    
            } else {
                centralElement = centralElement + "/" + topic.split("/")[k]    
            }
        }


        console.log("");
        console.log(util.unixTime(Date.now()) + " - Received topic: " + topic + " ; payload: " + payload.toString());

        //console.log("")
        //console.log("")
        //console.log("******* " + util.unixTime(Date.now()) + " ********")
        //console.log("topic: " + topic)
        //console.log("payload: " + payload)
        //console.log("typeof payload: " + typeof payload)
                    
        //Processing topic's message
    
        //if (topicLevel0==MQTTbrokerApiKeyvThing && topicLevel2==MQTTbrokerTopicData) {   
        if (topicLevelElement[0]==MQTTbrokerApiKeyvThing && topicLevelElement[topicLevelLength-1]==MQTTbrokerTopicDataOut) {               
            //Handling "/MQTTbrokerApiKeyvThing/vThingID/data_out" message
            //console.log("Handling data_out message")

            //const payLoadObject = JSON.parse(payload.toString());
            const payLoadObject = JSON.parse(payload.toString().replace(/'/g, '"'));
            //const payLoadObject = JSON.parse(payload)

            /*console.log("payLoadObject.data")
            console.log(payLoadObject.data)
            console.log("payLoadObject.data.length")
            console.log(payLoadObject.data.length)
            */

            ////Obtain vThingID from topic's string
            const vThingID = payLoadObject.meta.vThingID

            try {

                for(var j = 0; j < payLoadObject.data.length;j++) {

                    //const append_vThingResponse = await appendCBEntity(libfromNGSILD.fromNGSILDtoNGSI(payLoadObject.data[j],"v2",""),urlCB,vThingID)

                    var payLoadObjectNGSIv2 = {}

                    var payLoadObjectNGSIv2 = libfromNGSILD.fromNGSILDtoNGSI(payLoadObject.data[j],"v2","")

                    const processedEntities = await processNGSIv2Payload(payLoadObjectNGSIv2)

                    const append_vThingResponse = await appendCBEntity(processedEntities,urlCB,vThingID)

                    if (append_vThingResponse) {
                        //console.log('Operation has been completed successfully');
                    } else {
                        console.error("Create/Update fails.")
                    }
                }

            } catch(e) {
                console.error("Create/Update: " + e.toString());
            }

        } else if (topicLevelElement[0]==MQTTbrokerApiKeySilo && centralElement==vSiloID && topicLevelElement[topicLevelLength-1]==MQTTbrokerTopicDataIn) {
            //Handling /vSilo/vSiloID/data_in
            /*
                {
                    "data":[
                            {
                                "id":"urn:ngsi-ld:Device:001",
                                "type":"Device",
                                "start-result":{
                                                "type":"Property",
                                                "value":{
                                                            "cmd-value":"",
                                                            "cmd-qos":"0",
                                                            "cmd-id":"001",
                                                            "cmd-nuri":["viriot://vSilo/tenantID_orionv2/data_in"],
                                                            "cmd-result":"OK"
                                                }
                                },
                                "start-status":{
                                                "type":"Property",
                                                "value":{
                                                            "cmd-value":"",
                                                            "cmd-qos":"0",
                                                            "cmd-id":"001",
                                                            "cmd-nuri":["viriot://vSilo/tenantID_orionv2/data_in"],
                                                            "cmd-status":"OK"
                                                }
                                }
                            }
                    ],
                    "meta":{
                            "vThingID":"thingVisorID_Actuator/Device"
                    }
                }
            */


            const payLoadObject = JSON.parse(payload.toString().replace(/'/g, '"'));

            for(var j = 0; j < payLoadObject.data.length;j++) {
                try {
                    //const append_vThingResponse = await appendCBEntity(libfromNGSILD.fromNGSILDtoNGSI(payLoadObject.data[j],"v2",""),urlCB,payLoadObject.meta.vThingID)

                    var payLoadObjectNGSIv2 = {}

                    var payLoadObjectNGSIv2 = libfromNGSILD.fromNGSILDtoNGSI(payLoadObject.data[j],"v2","")

                    const processedEntities = await processNGSIv2PayloadDataIn(payLoadObjectNGSIv2)

                    //console.log("processedEntities")
                    //console.log(processedEntities)
                    
                    const append_vThingResponse = await appendCBEntity(processedEntities,urlCB,payLoadObject.meta.vThingID)
        
                    if (append_vThingResponse) {
                        //console.log('Operation has been completed successfully');
                    } else {
                        console.error("Create/Update fails.")
                    }
        
                } catch(e) {
                    console.error("Create/Update: " + e.toString());
                }
            }
        } else {
            console.error("invalid topic: '" + topic + "'");            
        }
        return;
    } catch(e) {
        console.error(e.toString());
        return;
    }
})

function addCommandToSubcriptionList(serviceArg, servicePathArg, typeArg, keyArg) {
    try {

        //["service","servicePath", "type", "command", ""subscriptionID"]
        
        if (subscriptionIdOCBCommandAttributeList.length == 0) {
            subscriptionIdOCBCommandAttributeList.push({IdOCB: "", Service: serviceArg, ServicePath: servicePathArg, Type: typeArg, Command: keyArg, delete: false})
            console.log("Add new subscription to create(1): " + typeArg)
        } else {
            var addCommand = true
            for(var i = 0; i < subscriptionIdOCBCommandAttributeList.length;i++) {
                if ( serviceArg == subscriptionIdOCBCommandAttributeList[i].Service && servicePathArg == subscriptionIdOCBCommandAttributeList[i].ServicePath && 
                    typeArg == subscriptionIdOCBCommandAttributeList[i].Type && keyArg == subscriptionIdOCBCommandAttributeList[i].Command) {
                    if (subscriptionIdOCBCommandAttributeList[i].IdOCB == "" && subscriptionIdOCBCommandAttributeList[i].delete) {
                        subscriptionIdOCBCommandAttributeList[i].delete = false
                    }
                    addCommand = false
                    break;
                }
            }  
            if (addCommand)  {
                subscriptionIdOCBCommandAttributeList.push({IdOCB: "", Service: serviceArg, ServicePath: servicePathArg, Type: typeArg, Command: keyArg, delete: false})
                console.log("Add new subscription to create(2): " + typeArg) 
            }
        }

        return true

    } catch(e) {
        console.error("addCommandToSubcriptionList: " + e.toString())
        return false
    }

}

//Create Orion Context Broker subscriptions.
async function orionSubscriptionByTypeCommands() {
    try {

        //console.log("orionSubscriptionByTypeCommands")

        for(var h = 0; h < subscriptionIdOCBCommandAttributeList.length;h++) {

            if(subscriptionIdOCBCommandAttributeList[h].IdOCB == "") {


                //Obtain all Orion Context Broker Subscriptions, the request are limited by a register fixed number (100).
                var obtainMore = true
                var offset = 100
                var actualOffset = 0
                var limit = 100

                //console.log("urlConsumerServerNotification: " + urlConsumerServerNotification)

                while (obtainMore) {

                    var responseCBSubscriptions

                    try {
                        //Obtain actual subscriptions in Context Broker
                        responseCBSubscriptions = await orion.obtainCBSubscriptions(actualOffset, limit, hostCB, portCB, 
                                                                                    subscriptionIdOCBCommandAttributeList[h].Service, 
                                                                                    subscriptionIdOCBCommandAttributeList[h].ServicePath)
                    } catch(e){
                        console.error(e)
                        if(e.message.indexOf("statusCode=404") <= -1) {
                            obtainMore=false
                            return false
                        }
                    }
                    
                    if (obtainMore && responseCBSubscriptions.length>0) {
                        //Processing response
                        var foundSubscritionID = false
                        for(var i = 0; i < responseCBSubscriptions.length;i++) {
                            //Compare notification URL subscription and urlConsumerServerNotification variable value.

                            if (responseCBSubscriptions[i].notification.http.url == urlConsumerServerNotification && 
                                    responseCBSubscriptions[i].description.startsWith("vSilo:"+ subscriptionIdOCBCommandAttributeList[h].Command +":") &&
                                    responseCBSubscriptions[i].subject.entities[0].type == subscriptionIdOCBCommandAttributeList[h].Type) {
                                
                                subscriptionIdOCBCommandAttributeList[h].IdOCB = responseCBSubscriptions[i].id
                                foundSubscritionID = true
                                break;
                            }
                        }

                        // responseCBSubscriptions.length<limit --> No more subscriptions in Orion Context Broker
                        // arrayObjectServiceTypes.length --> All virtual things types was found
                        if (responseCBSubscriptions.length<limit || foundSubscritionID == false) {
                            obtainMore=false
                        } else {
                            actualOffset = actualOffset + offset
                        }
                    } else {
                        obtainMore=false
                    }
                }
            }
        }

        var counter = 0
        for(var h = 0; h < subscriptionIdOCBCommandAttributeList.length;h++) {

            if(subscriptionIdOCBCommandAttributeList[h].IdOCB == "") {
                counter = counter + 1
            }
        }

        if(counter>0){
            console.log("")
            console.log("Command Subscriptions number to create in Orion Context Broker: " + counter)
    
            for(var h = 0; h < subscriptionIdOCBCommandAttributeList.length;h++) {

                if(subscriptionIdOCBCommandAttributeList[h].IdOCB == "") {


                    //Defining subscription body
                    var subscriptionOCB = {}
                    subscriptionOCB.description = "vSilo:" + subscriptionIdOCBCommandAttributeList[h].Command + ": subscription."
                    subscriptionOCB.subject = {
                                                entities: [
                                                            {
                                                                idPattern: ".*", 
                                                                type: subscriptionIdOCBCommandAttributeList[h].Type
                                                            }
                                                ],
                                                condition: {
                                                    attrs: [ 
                                                                subscriptionIdOCBCommandAttributeList[h].Command
                                                    ]
                                                }
                                            };  
                    subscriptionOCB.notification = {}
                    subscriptionOCB.notification.http = {url: urlConsumerServerNotification}
                    subscriptionOCB.notification.attrs = [ 
                                                            subscriptionIdOCBCommandAttributeList[h].Command
                                                        ]
                    //Preparing subscription command.
                    const instance = axios.create({
                        baseURL: urlCB
                    })

                    var headersPost = {}

                    headersPost["Content-Type"] = 'application/json';

                    if (subscriptionIdOCBCommandAttributeList[h].Service.length != 0) {
                        headersPost["fiware-service"] = subscriptionIdOCBCommandAttributeList[h].Service;
                    }
            
                    if (subscriptionIdOCBCommandAttributeList[h].ServicePath.length != 0) {
                        headersPost["fiware-servicepath"] = subscriptionIdOCBCommandAttributeList[h].ServicePath;
                    }

                    const optionsAxios = {
                        headers: headersPost
                        //,params: { options : 'skipInitialNotification' }
                    }
            
                    var responsePost

                    //console.log(JSON.stringify(subscriptionOCB))
            
                    try {
                        //Creamos la suscripción en OCB
                        responsePost = await instance.post(`/v2/subscriptions`, subscriptionOCB, optionsAxios)

                        const location=responsePost.headers['location']
                        const subscriptionIdOCB = location.split('/')[3]

                        if (typeof subscriptionIdOCB === 'undefined' || subscriptionIdOCB.length == 0 ) {
                            console.error("Error - connecting Orion Context Broker: Can't obtain information - subscriptionId.")
                            return false
                        } else {

                            subscriptionIdOCBCommandAttributeList[h].IdOCB = subscriptionIdOCB
                        }

                    } catch(e) {
                        console.error("Error - connecting Orion Context Broker: Can't subscribe '" + subscriptionOCB.description + "': " + e.toString())
                        return false
                    }
                }
            }
        }
        
        //Only to logs when new subscriptions are created
        if(counter>0){
            console.log("")
            console.log("All Command Subscriptions list created in Orion Context Broker: ")
            console.log(subscriptionIdOCBCommandAttributeList)
        }

        return true

    } catch(e) {
        console.error("orionSubscriptionByTypeCommands: " + e.toString())
        return false
    }
}

//Delete Orion Context Broker subscriptions.
async function orionUnsubscription() {
    try {

        //console.log("orionUnsubscription")

        var test = true

        //Define baseURL --> URL of OCB source.
        const instance = axios.create({
                baseURL: urlCB
        })

        for(var i = 0; i < subscriptionIdOCBCommandAttributeList.length;i++) {

            if (subscriptionIdOCBCommandAttributeList[i].IdOCB != "" && subscriptionIdOCBCommandAttributeList[i].delete) {

                var headersDelete = {}
                headersDelete["Accept"] = 'application/json';

                if (subscriptionIdOCBCommandAttributeList[i].Service.length != 0) {
                    headersDelete["fiware-service"] = subscriptionIdOCBCommandAttributeList[i].Service;
                }

                if (subscriptionIdOCBCommandAttributeList[i].ServicePath.length != 0) {
                    headersDelete["fiware-servicepath"] = subscriptionIdOCBCommandAttributeList[i].ServicePath;
                }

                try {
                    console.log("Deleting: " + subscriptionIdOCBCommandAttributeList[i].IdOCB)
                    const responseDel = await instance.delete(`/v2/subscriptions/${subscriptionIdOCBCommandAttributeList[i].IdOCB}`, 
                            { headers: headersDelete })
                    console.log("Deleted: " + subscriptionIdOCBCommandAttributeList[i].IdOCB)

                    subscriptionIdOCBCommandAttributeList[i].IdOCB = ""
                } catch(e) {
                    console.error("Error - connecting Orion Context Broker: Can't unsubscribe: " + e.toString())
                    test = false
                } 
            }
        }

        for(var i = 0; i < subscriptionIdOCBCommandAttributeList.length;i++) {
            if (subscriptionIdOCBCommandAttributeList[i].IdOCB == "" && subscriptionIdOCBCommandAttributeList[i].delete) {
                subscriptionIdOCBCommandAttributeList.splice(i, 1); 
                i--;
            }
        }

        return test

    } catch(e) {
        console.error("orionUnsubscription: " + e.toString())
        return false

    }
}

//Delete Orion Context Broker entity.
//async function deleteCBEntity (service,servicePath,subscriptionIdOCB) {
async function orionObtainTypes () {
    try {
        //Definimos baseURL de axios según la URl de OCB source.
        const instance = axios.create({
                baseURL: urlCB
        })

        var headersGet = {}
        headersGet["Accept"] = 'application/json';

        /* Non-operative
        if (typeof service !== 'undefined') {
            headersDelete["fiware-service"] = service;
        }
            
        if (typeof servicePath !== 'undefined') {
            headersDelete["fiware-servicepath"] = servicePath;
        }
        */

        var responseGet

        try {

            const responseGet = await instance.get(`/v2/types?limit=100&options=count`, { headers: headersGet })

            console.log(responseGet)

        } catch(e) {
            console.error("Get type fails (1) - error deleting Context Broker entity: " + e.toString());            
            return {  status: 500, data: [] }
        }
        return responseGet

    } catch(e) {
        console.error("Get type fails (2) - error deleting Context Broker entity: " + e.toString());            
        return { status: 500, data: [] }
    }
}



//Create mqtt subscriptions.
async function subscribeMQTT(topicArray,elem,identify,param) {
    try {
        //console.log("Subscribe topics: ")             
        if (param=="data") {
            await clientMosquittoMqttData.subscribe(topicArray, {qos: 0}, function (err, granted) {
                if (!err) {
                    /*
                    if (elem == '0') {
                        console.log("Successfully tenantID_vSiloID topic subscription: " + identify + "'") 
                    } if (elem == '1') {
                        console.log("Successfully vThing topic subscription: '" + identify + "'") 
                    } else {
                        console.log("Successfully topic's subscription")    
                    }
                    */
                    //console.log("Successfully topic's subscription '" + identify + "'.")
                    //console.log(granted)
                } else {
                    /*if (elem == '0') {
                        console.error("Error tenantID_vSiloID topic subscription: '" + identify + "' - : " + err) 
                    } if (elem == '1') {
                        console.error("Error vThing topic subscription: '" + identify + "' - : " + err) 
                    } else {
                        console.error("Error topic's subscription: " + err)    
                    }*/
                    //clientMosquittoMqttData.end()
                    console.error("Error topic's subscription '" + identify + "': " + err)

                    return false
                }
            })
        } else {
            await clientMosquittoMqttControl.subscribe(topicArray, {qos: 0}, function (err, granted) {
                if (!err) {
                    /*if (elem == '0') {
                        console.log("Successfully tenantID_vSiloID topic subscription: " + identify + "'") 
                    } if (elem == '1') {
                        console.log("Successfully vThing topic subscription: '" + identify + "'") 
                    } else {
                        console.log("Successfully topic's subscription")    
                    }
                    */
                    //console.log("Successfully topic's subscription '" + identify + "'.")
                    //console.log(granted)
                } else {
                    /*if (elem == '0') {
                        console.error("Error tenantID_vSiloID topic subscription: '" + identify + "' - : " + err) 
                    } if (elem == '1') {
                        console.error("Error vThing topic subscription: '" + identify + "' - : " + err) 
                    } else {
                        console.error("Error topic's subscription: " + err)  
                    }*/
                    //clientMosquittoMqttControl.end()
                    console.error("Error topic's subscription '" + identify + "': " + err)
                    return false
                }
            })
        }
        
        //clientMosquittoMqtt.end()
        return true

    } catch(e) {
        console.error(e.toString());
        return false
    }
}


//Unsubscribe mqtt.
async function unsubscribeMQTT(topicArray,param) {
    try {

        console.log("Unsubscribe topics: ")
        console.log(topicArray)

        if (param=="data") {
            await clientMosquittoMqttData.unsubscribe(topicArray, function (err) {

                if (!err) {
                    //console.log("Successfully topic's unsubscription")    
                } else {

                    console.error("Error topic's unsubscription: " + err)    
                    return false
                }
            })

        } else {
            await clientMosquittoMqttControl.unsubscribe(topicArray, function (err) {

                if (!err) {
                    //console.log("Successfully topic's unsubscription")    
                } else {

                    console.error("Error topic's unsubscription: " + err)    
                    return false
                }
            })
        }
        return true

    } catch(e) {
        console.error(e.toString());
        return false
    }
}


function findArrayElement(array,element) {
    try {
        if (array.indexOf(element)==-1) {
            return false
        }
        return true
    }
     catch(e) {
        console.error(e.toString());
        return false
    }
}



//Delete vThing from Silo.
async function delete_vThing(vThingID,urlCB) {
    try {

        //Deleting topic's subscriptions
        var topicArray = []
        var topicElement = MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopicDataOut

        //"/vThing/vThingID/data_out" topic
        //topicArray.push(MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopicData)
        //topicArray.push(MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopicDataOut)
        topicArray.push(topicElement)

        //TODO: handle ¿unsubscribe not done --> delete context broker entity error?

        const response_unsubscribeMQTTData = await unsubscribeMQTT(topicArray,"data")

        if (response_unsubscribeMQTTData) {

            //POP from mqttSubscriptionListData array vThing topic unsubscriptions
            //for(var i = 0; i < topicArray.length;i++) {
            //    mqttSubscriptionListData.splice(mqttSubscriptionListData.indexOf(topicArray[i]), 1 );    
            //}
            mqttSubscriptionListData.splice(mqttSubscriptionListData.indexOf(topicElement), 1 );

            var topicArray = []
            var topicElement = MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopic_c_out_Control
                
            //"/vThing/vThingID/out_control" topic
            //topicArray.push(MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopic_c_out_Control)
            topicArray.push(topicElement)

            //TODO: handle ¿unsubscribe not done --> delete context broker entity error?

            const response_unsubscribeMQTTControl = await unsubscribeMQTT(topicArray,"control")

            if (response_unsubscribeMQTTControl) {

                //POP from mqttSubscriptionListControl array vThing topic unsubscriptions
                //for(var i = 0; i < topicArray.length;i++) {
                //    mqttSubscriptionListControl.splice(mqttSubscriptionListControl.indexOf(topicArray[i]), 1 );    
                //}
                mqttSubscriptionListControl.splice(mqttSubscriptionListControl.indexOf(topicElement), 1 );    

                console.log("MQTT Data Subscription Topic List: ")
                console.log(mqttSubscriptionListData)
                console.log("MQTT Control Subscription Topic List: ")
                console.log(mqttSubscriptionListControl)

                const delete_vThingResponse = await deleteCBEntity(vThingID,urlCB)

                if (delete_vThingResponse) {
                    return true
                } else  {
                    return false
                }
            } else {
                return false
            }
        } else {
            return false
        }
    } catch(e) {
        console.error(e.toString());
        return false
    }
}

//Create/Update Orion Context Broker entity.
//async function appendCBEntity (service,servicePath,subscriptionIdOCB) {
async function appendCBEntity(payLoadObject,urlCB,vThingID) {
    try {
        const instance = axios.create({
            baseURL: urlCB
        })

        //Defining headers.
        var headersPost = {}

        headersPost["Content-Type"] = 'application/json';

        //const dOCBService = subscriptionFound.destinyOCB_service || ""
        //const dOCBServicePath = subscriptionFound.destinyOCB_servicePath || ""

        //if (dOCBService != "") {
        //    headersPost["fiware-service"] = dOCBService;
        //}
        
        //if (dOCBServicePath != "") {
        //    headersPost["fiware-servicepath"] = dOCBServicePath
        //}

        const options = {
            headers: headersPost
        }
        
        //payLoadObject.id = subscriptionFound.destinyOCB_id
        //payLoadObject.type = subscriptionFound.destinyOCB_type

        //Definimos el body de la actualización.
        var entities = []
        entities.push(payLoadObject)

        //console.log(payLoadObject)

        var updatebody = {
            actionType: "APPEND",
            entities
            }

        //console.log("updatebody")
        //console.log(updatebody)
        //console.log(updatebody.entities)
        //console.log(typeof updatebody)

        //Update/create entity - CONTEXT BROKER
        try {
            const responsePost = await instance.post(`/v2/op/update`, updatebody, options)

            //Store in vThingList track vThingID & vThingLDID/vThingLDType
            //when receives a deleteVThing command, Silos-Controller will need this information to identify
            //specifics NGSI-LD entities.
            for(var i = 0; i < entities.length;i++) {
                var testBoolean = false

                for(var k = 0; k < vThingList.length;k++) {
                    if (entities[i].type==vThingList[k].vThingLDType && entities[i].id==vThingList[k].vThingLDID && vThingID==vThingList[k].vThingID) {
                        testBoolean = true
                        break;
                    }
                }

                if(testBoolean == false) {
                    vThingList.push({
                        vThingLDID: entities[i].id,
                        vThingLDType: entities[i].type,
                        vThingID: vThingID
                    })
                }
            }

        } catch(e) {
            console.error("Create/Update fails - error Create/Update Context Broker entity: " + e.toString());            
            return false
        }
        return true
    } catch(e) {
        console.error("Create/Update fails - error Create/Update Context Broker entity: " + e.toString());            
        return false
    }
}

//Send vThingID getContextRequest message.
async function sendGetContextRequest(vThingID) {
    try {

        //Silos Controller sends the response to Master-Controller ( vSilo/<ID>/c_out destroyVSilo).

        //"/vSilo/<ID>/c_out" topic
        const topic = MQTTbrokerApiKeyvThing + "/" + vThingID + "/" + MQTTbrokerTopic_c_in_Control;

        const body = {"command": commandGetContextRequest, "vSiloID": vSiloID, "vThingID": vThingID}

        console.log("Sending message... " + topic + " " + JSON.stringify(body));
            
        await clientMosquittoMqttControl.publish(topic, JSON.stringify(body), {qos: 0}, function (err) {
            if (!err) {
                //console.log("Message has been sent correctly.")
            } else {
                console.error("ERROR: Sending MQTT message (publish): ",err)
            }
        })

        return true

    } catch(e) {
        console.error(e.toString());
        return false
    }
}



//Delete Orion Context Broker entity.
//async function deleteCBEntity (service,servicePath,subscriptionIdOCB) {
async function deleteCBEntity (vThingID,urlCB) {
    try {
        //Definimos baseURL de axios según la URl de OCB source.
        const instance = axios.create({
                baseURL: urlCB
        })

        var headersDelete = {}
        headersDelete["Accept"] = 'application/json';

        /* Non-operative
        if (typeof service !== 'undefined') {
            headersDelete["fiware-service"] = service;
        }
            
        if (typeof servicePath !== 'undefined') {
            headersDelete["fiware-servicepath"] = servicePath;
        }
        */

        try {

            var vThingListRemove = []

            for(var k = 0; k < vThingList.length;k++) {
                if (vThingID==vThingList[k].vThingID) {
                    const responseDel = await instance.delete(`/v2/entities/${vThingList[k].vThingLDID}?type=${vThingList[k].vThingLDType}`, { headers: headersDelete })
                    
                    vThingListRemove.push(vThingList[k])
                }
            }
            //Remove from vThingList.
            for(var i = 0; i < vThingListRemove.length;i++) {
                vThingList.splice(vThingList.indexOf(vThingListRemove[i]), 1 );    
            }

            console.log("The Context Broker entities, relate with vThingID: " + vThingID + "', are deleted.") 
            console.log("vThing List after 'deleteVThing': ")
            console.log(vThingList)

        } catch(e) {
            console.error("Delete fails - error deleting Context Broker entity: " + e.toString());            
            return false
        }
        return true

    } catch(e) {
        console.error("Delete fails - error deleting Context Broker entity: " + e.toString());            
        return false
    }
}


//Process NGSI payload to create, if it corresponds, the commands attributes.
//Affected topics:
// - vThing/<vThingID>/data_out
// - vSilo/<vSiloID>/c_in {"command":"getContextResponse","data":[...], ,"meta":{"vThingID":"<vThingID>"}}

async function processNGSIv2Payload(entityArg) {
    try {

        var entity = {}

        entity = JSON.parse(JSON.stringify(entityArg))

        
        if (typeof entity.commands !== "undefined") {

            for(var j = 0; j < entity.commands.value.length;j++) {

                var testAddAttributes = false
                try {
                    var response = await orion.obtainCBAttributeEntity (entity.id, entity.commands.value[j], hostCB, portCB, serviceCB, servicePathCB)

                    if(response.status == 404) {
                        testAddAttributes = true
                    }   
                } catch(e) {
                    if(e.message.indexOf("statusCode=404") >= 0) {
                        testAddAttributes = true
                    } else {
                        console.error(e);
                    }

                }

                if(testAddAttributes) {
                    entity[entity.commands.value[j]] = {type: "command", value: ""}
                    entity[entity.commands.value[j] + "-result"] = {type: "commandResult", value: ""}
                    entity[entity.commands.value[j] + "-status"] = {type: "commandStatus", value: ""}
                }
                   
            }
            delete entity.commands

            //console.log(entity)
        }

        return entity

    } catch(e) {
        console.error(e.toString());
        return {}
    }
}

//Process NGSI payload to create, if it corresponds, the commands attributes.
//Affected topics:
// - vSilo/<vSiloID>/data_in {"data":[...], ,"meta":{"vThingID":"<vThingID>"}}

async function processNGSIv2PayloadDataIn(entityArg) {
    try {

        var entity = {}

        entity = JSON.parse(JSON.stringify(entityArg))

        for(var key in entity) {

            if(findArrayElement(["id","type","@context"],key) == false) {

                //console.log(key)

                try {
                    //console.log(key.substring(key.length-7,key.length))

                    if(key.substring(key.length-7,key.length) == "-result") {

                        var cmdResultValue = entity[key].value["cmd-result"]

                        entity[key].type = "commandResult"
                        entity[key].value = cmdResultValue
                        //delete entity[key].metadata


                    } else if(key.substring(key.length-7,key.length) == "-status") {

                            var cmdStatusValue = entity[key].value["cmd-status"]

                            entity[key].type = "commandStatus"
                            entity[key].value = cmdStatusValue
                            //delete entity[key].metadata

                    } else {
                        console.log("Delete key: " + key )
                        delete entity[key]
                    }

                } catch(e) {
                    console.error(e.toString());
                    var a

                }

            }

        }

        return entity

    } catch(e) {
        console.error(e.toString());
        return {}
    }
}





//Send delete messages in topics.
async function sendDeleteMessages() {
    try {

        //Silos Controller sends the response to Master-Controller ( vSilo/<ID>/c_out destroyVSilo).

        //"/vSilo/<ID>/c_out" topic
        const topic = MQTTbrokerApiKeySilo + "/" + vSiloID + "/" + MQTTbrokerTopic_c_out_Control;

        const body = {"command": commandDestroyVSiloAck, "vSiloID": vSiloID}

        console.log("Sending message... " + topic + " " + JSON.stringify(body));
            
        await clientMosquittoMqttControl.publish(topic, JSON.stringify(body), {qos: 0}, function (err) {
            if (!err) {
                //console.log("Message has been sent correctly.")
            } else {
                console.error("ERROR: Sending MQTT message (publish): ",err)
            }
        })

        return true

    } catch(e) {
        console.error(e.toString());
        return false
    }
}


//Sending commands....
async function sendCommandMessage(commandBodyLD,entityType,entiyID) {
    try {

        /*
            {
                "meta":{
                        "vSiloID":"tenantID_orionv2_vSiloName_orionv2"
                },
                "data":[
                        {
                            "id":"urn:ngsi-ld:Device:001",
                            "type":"Device",
                            "start":{
                                        "type":"Property",
                                        "value":{
                                                    "cmd-value": "",
                                                    "cmd-qos":"0",
                                                    "cmd-id":"001",
                                                    "cmd-nuri":["viriot://vSilo/tenantID_orionv2_vSiloName_orionv2/data_in"]
                                        }
                            }
                        }
                ]
            }
        */

        var vThingIDValue = ""

        for(var k = 0; k < vThingList.length;k++) {
            if (vThingList[k].vThingLDType == entityType && vThingList[k].vThingLDID == entiyID) {
                vThingIDValue = vThingList[k].vThingID
                break;
            }
        }

        if(vThingIDValue != "") {

            const topic = MQTTbrokerApiKeyvThing + "/" + vThingIDValue + "/" + MQTTbrokerTopicDataIn;
                    
            const topicMessage = {"data": [commandBodyLD], "meta": {"vSiloID": vSiloID}}

            console.log("Sending message... " + topic + " " + JSON.stringify(topicMessage));

            await clientMosquittoMqttData.publish(topic, JSON.stringify(topicMessage), {qos: 0}, function (err) {
                if (!err) {
                    //console.log("Message has been sent correctly.")
                } else {
                    console.error("ERROR: Sending MQTT message (publish): ",err)
                }
            })

        } else {
            console.error("sendCommandMessage: Can't send command - vThingID to (type: " + entityType + ", id: " + entiyID + ") not found.")
        }

                    
        return true

    } catch(e) {
        console.error("sendCommandMessage: " + e.toString())
        return false
    }  
}



async function shutdown(param) {

    try {

        //STEP 1: The vSilo controller cancels the topic subscriptions.
        if (mqttSubscriptionListData.length>0) {
            const response_unsubscribeMQTTData = await unsubscribeMQTT(mqttSubscriptionListData,"data")

            if (response_unsubscribeMQTTData) {
                //Emptly mqttSubscriptionList
                mqttSubscriptionListData = []
            }
        }

        if (mqttSubscriptionListControl.length>0) {
            const response_unsubscribeMQTTControl = await unsubscribeMQTT(mqttSubscriptionListControl,"control")

            if (response_unsubscribeMQTTControl) {
                //Emptly mqttSubscriptionList
                mqttSubscriptionListControl = []
            }
        }
        
        //TODO: process response_unsubscribeMQTT value (true or false) send topic message¿?¿?
        console.log('MQTT Subscriptions Deleted.');

        //STEP 2: //Silos Controller sends the response to Master-Controller ( vSilo/<ID>/c_out destroyVSilo).  
        //Master-Controller receives the information. It cancels DB information and topic subscriptions and kills the TV container. 

        const response_sendDeleteMessages = await sendDeleteMessages()

        if (response_sendDeleteMessages) {
            //Emptly
        }


        clientMosquittoMqttControl.end()
        clientMosquittoMqttData.end()
        console.log('MQTT disconnected.');

        console.log('Silos stopped, exiting now');
        if (param=="1") { // Only when capture signals.
            process.exit();            
        } else {
            return true
        }

    } catch(e){
        console.error("shutdown: " + e.toString())
        if (param=="1") { // Only when capture signals.
            process.exit();            
        } else {
            return false
        }
    }
}


/* References to capture signals
//--> Show System Docker Events 
//https://docs.docker.com/engine/reference/commandline/events/

//--> Docker List Events
//https://nodejs.org/api/process.html#process_signal_events

//--> Docker kill Event - info
//https://docs.docker.com/engine/reference/commandline/kill/
//https://docker-py.readthedocs.io/en/stable/containers.html

//--> Signals values
https://stackoverflow.com/questions/16338884/what-does-exited-abnormally-with-signal-9-killed-9-mean/27989874
*/

//TODO: remove or update?
// To capture signals.
const capt_signals = ['SIGHUP', 'SIGINT', 'SIGTERM'];

//TODO: remove or update?
// processing exit condition signals
capt_signals.forEach(signal => {
	var sd_gen = (s) => {
		return () => {
		    console.log(`Signal ${s} received, starting shutdown`)
    		shutdown(1)
		}
	}
	process.on(signal, sd_gen(signal))
	}
);

//Consume Orion Context Broker notifications..
app.post(config.pathNotification, async function(req,res) {
    try {
        console.log("")
        console.log(util.unixTime(Date.now()) + " - POST /notification - " + req.body.subscriptionId)
    
        const dataBody = req.body.data


        for(var i = 0; i < dataBody.length; i++) {

            var mqttPayLoad = {}

            var attributes = {}

            var testSendCommand = false

            //Obtain command from payload
            for(var key in dataBody[i]) {
                if(key != "id" && key != "type") {

                    var auxValue  = ""
                    if (typeof dataBody[i][key].value === "object") {
                        auxValue = JSON.parse(JSON.stringify(dataBody[i][key].value))
                    } else {
                        auxValue = dataBody[i][key].value
                    }

                    //Send command only if command.value is defined.
                    if(auxValue != "") {

                        var cmdID = parseInt(Date.now())

                        attributes[key] = {
                            "type":"Property",
                            "value":{
                                    "cmd-value": auxValue,
                                    "cmd-qos":"2",
                                    "cmd-id": cmdID,
                                    "cmd-nuri":"viriot://" + MQTTbrokerApiKeySilo + "/" + vSiloID + "/" + MQTTbrokerTopicDataIn
                            }
                        }

                        testSendCommand = true
                    //} else {
                    //    console.log("Don't send : " + key)
                    //    console.log(dataBody[i])
                    }

                    
                }
            }

            if(testSendCommand){

                /*
                {
                    "id":"urn:ngsi-ld:Device:001",
                    "type":"Device",
                    "start":{
                                "type":"Property",
                                "value":{
                                            "cmd-value": "",
                                            "cmd-qos":"0",
                                            "cmd-id":"001",
                                            "cmd-nuri":["viriot://vSilo/tenantID_orionv2_vSiloName_orionv2/data_in"]
                                }
                    }
                }

                */
                var dataPayload = {}

                dataPayload = JSON.parse(JSON.stringify(attributes))

                dataPayload["id"] = dataBody[i].id
                dataPayload["type"] = dataBody[i].type

                const responseSendCommandMessage = await sendCommandMessage(dataPayload,dataBody[i].type,dataBody[i].id)

            }

        }



        //var service =req.headers['fiware-service'] || ""
        
        res.status(200).send({description: 'Operation has been completed successfully'})
    } catch(e) {
        console.error(e)
        res.status(500).send({ error: e })
    }
})

// Launch service.
app.listen(portNotification,() => {        

    setTimeout(async function() {
        console.log(util.unixTime(Date.now()) + ` - Listener running, port: ${portNotification}`)

    }, 10000); //Wait 10 seconds

})


// PERIODIC PROCESS
setInterval(async  function() {

    try  {
        
        //Obtain all representation schema by type and compare with subscriptionIdOCBCommandAttributeList to add or remove subscritions.
        var responseOrionSchemaByType

        var error = false

        try {

            responseOrionSchemaByType = await orion.obtainALLCBSchemaByType (1000, hostCB, portCB, serviceCB, servicePathCB)

        } catch(e){
            console.error(e)

            error = true
        }

        //console.log(responseOrionSchemaByType[0].attrs)

        if (error == false) {

            //console.log("Marking subscriptions to delete....")
            //Obtain subscriptions should be deleted.
            for(var i = 0; i < subscriptionIdOCBCommandAttributeList.length;i++) {

                if (responseOrionSchemaByType.length == 0) { //Mark all subscriptions to delete them.
                    subscriptionIdOCBCommandAttributeList[i].delete = true
                    console.log("Mark to remove subscription(1): " + subscriptionIdOCBCommandAttributeList[i].IdOCB)
                } else {

                    var testFound = false

                    for(var j = 0; j < responseOrionSchemaByType.length;j++) {

                        if(responseOrionSchemaByType[j].type == subscriptionIdOCBCommandAttributeList[i].Type && 
                            typeof responseOrionSchemaByType[j].attrs[subscriptionIdOCBCommandAttributeList[i].Command+"-result"] !== "undefined") {
                            testFound = true
                            break
                        }

                    }

                    if (testFound == false) {
                        subscriptionIdOCBCommandAttributeList[i].delete = true
                        console.log("Mark to remove subscription(2): " + subscriptionIdOCBCommandAttributeList[i].IdOCB)
                    }

                }
            }

            //console.log("Detecting new subscriptions to create....")
            //Detect if new subscriptions are needed.
            for(var i = 0; i < responseOrionSchemaByType.length;i++) {

                for(var key in responseOrionSchemaByType[i].attrs) {

                    if(findArrayElement(["@context"],key) == false) {

                        if (typeof responseOrionSchemaByType[i].attrs[key].types !== "undefined") {

                            if (findArrayElement(responseOrionSchemaByType[i].attrs[key].types, "commandResult")) {

                                var addCommandResult = addCommandToSubcriptionList(
                                                            serviceCB, //Service
                                                            servicePathCB, //Service_path
                                                            responseOrionSchemaByType[i].type, //type
                                                            key.substring(0,key.length-7) //command
                                                            )
                            } 
                        }
                    }
                }
            }

            //Delete unnecessary subscriptions.
            var responseOrionUnsubscription = await orionUnsubscription()

            //Call orionSubscriptionByTypeCommands and create new subcriptions.
            var responseOrionSubscription = await orionSubscriptionByTypeCommands()

        }

    } catch(e) {
        console.error(e.toString());
    }
}, config.frecuency_mseg);  