'use strict'


const app = require('./app')

const axios = require('axios');

const config = require('./config')

var orion = require("./orion");

var util = require("./util")

var libWrapperUtils = require("./wrapperUtils")
var libfromNGSIv2 = require("./fromNGSIv2")

var mqtt = require('mqtt')

var isGreedy
var isAggregated
var isGroupingByType

//Only from "noGreedy" Thing visors.
var vThingListInternalTV = []

var vThingList = []
var vThingListAggValueContext = []

//var MQTTbrokerIP
//var MQTTbrokerPort

var MQTTDataBrokerIP
var MQTTDataBrokerPort
var MQTTControlBrokerIP
var MQTTControlBrokerPort

var systemDatabaseIP
var systemDatabasePort

var thingVisorID
var MQTTbrokerApiKeyvThing
var MQTTbrokerApiKeySilo
var MQTTbrokerApiKeyThingVisor
var MQTTbrokerTopicData
var MQTTbrokerTopicDataOut
var MQTTbrokerTopicDataIn

var MQTTbrokerTopic_c_in_Control
var MQTTbrokerTopic_c_out_Control

var ocb_type
var ocb_attrList
var dest_ocb_type
var dest_ocb_attrList

var valuevThingTypeLD

var params

var ocb_ip
var ocb_port
var ocb_service
var ocb_servicePath

var globalTotalFreeParkingSpaces = 0
var globalMaxObservedAt = ""


var notificacion_protocol = ""
var notify_ip = ""
var notificacion_port_container = ""
var notify_service = ""


var entitiesPerVThingID = 0


var MQTTbrokerUsername
var MQTTbrokerPassword

var commandDestroyTV
var commandDestroyTVAck
var commandDeleteVThing
var commandCreateVThing
var commandGetContextRequest
var commandGetContextResponse

var commandMappedPort


var mapped_port
var urlNotify
var subscriptionIdOCBList = []

var mqttSubscriptionList = []

var typeServiceList = []

//var options
var optionsData
var optionsControl

//var clientMosquittoMqtt
var clientMosquittoMqttData
var clientMosquittoMqttControl

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
    
    systemDatabaseIP=config.systemDatabaseIP
    systemDatabasePort = config.systemDatabasePort

    thingVisorID = config.thingVisorID
    MQTTbrokerApiKeyvThing = config.MQTTbrokerApiKeyvThing
    MQTTbrokerApiKeySilo = config.MQTTbrokerApiKeySilo
    MQTTbrokerApiKeyThingVisor = config.MQTTbrokerApiKeyThingVisor
    MQTTbrokerTopicData = config.MQTTbrokerTopicData
    MQTTbrokerTopicDataOut = config.MQTTbrokerTopicDataOut
    MQTTbrokerTopicDataIn = config.MQTTbrokerTopicDataIn

    MQTTbrokerTopic_c_in_Control = config.MQTTbrokerTopic_c_in_Control
    MQTTbrokerTopic_c_out_Control = config.MQTTbrokerTopic_c_out_Control

    commandDestroyTV = config.commandDestroyTV
    commandDestroyTVAck = config.commandDestroyTVAck
    commandMappedPort = config.commandMappedPort
    commandDeleteVThing = config.commandDeleteVThing
    commandCreateVThing = config.commandCreateVThing
    commandGetContextRequest = config.commandGetContextRequest
    commandGetContextResponse = config.commandGetContextResponse

    params = JSON.parse(config.providerParams)

    isGreedy = config.isGreedy
    if (typeof isGreedy === "undefined") {
        isGreedy = true
    }

    isAggregated = config.isAggregated
    if (typeof isAggregated === "undefined") {
        isAggregated = false
    }

    isGroupingByType = config.isGroupingByType
    if (typeof isGroupingByType === "undefined" && isGreedy) {
        isGroupingByType = true
    }

    /* ****************************************************************************************************** */
    
    //PDTE_JUAN:TODO todo este bloque afecta a la potencia que quedamos darle a nogreedy
    //hay que analizar las consecuencias de esta potencia que dejamos abierta....
    

    ocb_type = config.ocb_type
    ocb_attrList = config.ocb_attrList

    dest_ocb_type = config.dest_ocb_type
    dest_ocb_attrList = config.dest_ocb_attrList

    valuevThingTypeLD = ocb_type

    //To fix NGSI-LD entity type in no Greedy ThingVisor and obtain a new NGSI-LD id
    if (isGreedy == false && typeof dest_ocb_type !== "undefined") {
        valuevThingTypeLD = dest_ocb_type
    }

    /* ****************************************************************************************************** */


    if (params == '' || typeof params === 'undefined' || 
        params.ocb_ip == '' || typeof params.ocb_ip === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'ocb_ip' param not found.")
        return
    }

    if (params == '' || typeof params === 'undefined' || 
        params.ocb_port == '' || typeof params.ocb_port === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'ocb_port' param not found.")
        return
    }

/*    
    if (MQTTbrokerIP == '' || typeof MQTTbrokerIP === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'MQTTbrokerIP' param not found.")
        return
    }

    if (MQTTbrokerPort == '' || typeof MQTTbrokerPort === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'MQTTbrokerPort' param not found.")
        return
    }
*/

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

    if (systemDatabaseIP == '' || typeof systemDatabaseIP === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'systemDatabaseIP' param not found.")
        return
    }

    if (systemDatabasePort == '' || typeof systemDatabasePort === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'systemDatabasePort' param not found.")
        return
    }

    ocb_ip = params.ocb_ip
    ocb_port = params.ocb_port
    if (isGreedy) {
        ocb_service = params.ocb_service || [""]
        ocb_servicePath = '/#'
    } else {
        //PDTE_JUAN:TODO aqui se quitará esta forma de hacerlo, se cargarán los arrays directamente del fichero de configuración
        ocb_service = params.ocb_service || [""]
        ocb_servicePath = params.ocb_servicePath || '/#'    
    }
    notificacion_protocol = params.notificacion_protocol || 'http'
    notify_ip = params.notify_ip || ''
    notificacion_port_container = config.notificacion_port_container || ''
    notify_service = config.pathNotification
   
    if (notify_ip=="") {
        console.error("Error - processing ThingVisor's environment variables: 'notify_ip' param not found.")
        return
    }

    entitiesPerVThingID = parseInt(params.entitiesPerVThingID || '0')

    if (entitiesPerVThingID < 0){
        entitiesPerVThingID = 0
    }

    MQTTbrokerUsername = params.MQTTbrokerUsername || ''
    MQTTbrokerPassword = params.MQTTbrokerPassword || ''

    //PDTE_JUAN: Quit, only for development environment...
    if (MQTTDataBrokerIP == "155.54.99.118" && MQTTDataBrokerPort == "1884") {
        MQTTbrokerUsername = 'IoTPlatformMQTTUser'
        MQTTbrokerPassword = '1234MQTT'
    }

    //Options MQTT connection
    optionsControl = {
        clean: false,
        clientId: 'mqttjs_' + Math.random().toString(16).substr(2, 8), // Aleatorio
        username: MQTTbrokerUsername, // Optional
        password: MQTTbrokerPassword, // Optional
    };

    optionsData = {
        clean: false,
        clientId: 'mqttjs_' + Math.random().toString(16).substr(2, 8), // Aleatorio
        username: MQTTbrokerUsername, // Optional
        password: MQTTbrokerPassword, // Optional
    };

} catch(e) {
    console.error("Error - processing ThingVisor's environment variables: " + e.toString())
    return
}

//Connecting to MQTT-server...
try {
    
    clientMosquittoMqttControl = mqtt.connect("mqtt://" + MQTTControlBrokerIP + ":" + MQTTControlBrokerPort,optionsControl);

    clientMosquittoMqttData = mqtt.connect("mqtt://" + MQTTDataBrokerIP + ":" + MQTTDataBrokerPort,optionsData);
    
} catch(e) {
    console.error("Error - connecting MQTT-server...: " + e.toString())
    return 
}

//Mapping connect function
clientMosquittoMqttControl.on("connect", function() {
    try {

        console.log("")
        console.log(util.unixTime(Date.now()) + " - MQTT Broker connected")
        //Establishing topic's subscriptions
        var topicArray = []
        var topicElement = MQTTbrokerApiKeyThingVisor + "/" + thingVisorID + "/" + MQTTbrokerTopic_c_in_Control

        //"/TV/thingVisorID/c_in" topic
        //topicArray.push(MQTTbrokerApiKeyThingVisor + "/" + thingVisorID + "/" + MQTTbrokerTopic_c_in_Control)
        topicArray.push(topicElement)

        if (subscribeMQTT(topicArray,'0',thingVisorID) == false) {
            console.error("Error - connecting MQTT-server: Can't subscribe topics.")
            return
        } else {

            //Push into mqttSubscriptionList array new topic subscriptions array
            if (findArrayElement(mqttSubscriptionList,topicElement) == false) {
                mqttSubscriptionList = mqttSubscriptionList.concat(topicArray)    
            }
            //mqttSubscriptionList = mqttSubscriptionList.concat(topicArray)

            console.log("")
            console.log("MQTT Subscription Topic List: ")
            console.log(mqttSubscriptionList)
            
        }
        return
    } catch(e) {
      //log.error(error.toString());
      console.error(e.toString());
      return;
    }
})

//Mapping error function
clientMosquittoMqttControl.on("error", function(error) {
    try {
        clientMosquittoMqttControl.reconnect()
        return;
    } catch(e) {
      //log.error(error.toString());
      console.error(e.toString());
      return;
    }
})

//Mapping reconnect function
clientMosquittoMqttControl.on("reconnect", function(a) {
    try {
        console.log(util.unixTime(Date.now()) + " - Reconnecting clientMosquittoMqttControl...")
        return;
    } catch(e) {
      //log.error(error.toString());
      console.error(e.toString());
      return;
    }
})

//Mapping topic's subscriptions function
clientMosquittoMqttControl.on("message", async function(topic, payload) {
    
    try {
        console.log("");
        console.log(util.unixTime(Date.now()) + " - Received topic: " + topic + " ; payload: " + payload.toString());
        
        //var payLoadObject;

        //payLoadObject = JSON.parse(payload.toString());


        //Processing topic's message
        var topicLevelLength = topic.split("/").length
        var topicLevelElement = []

        var centralElement = ""

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

        if (topicLevelElement[0]==MQTTbrokerApiKeyThingVisor && centralElement==thingVisorID && topicLevelElement[topicLevelLength-1]==MQTTbrokerTopic_c_in_Control) {
            //Handling "TV/thingVisorID/c_in" message
            //console.log("Handling TV/thingVisorID/c_in message")
            
            //const payLoadObject = JSON.parse(payload.toString());
            const payLoadObject = JSON.parse(payload.toString().replace(/'/g, '"'));

            if (payLoadObject.command==commandDestroyTV) {
                //destroyTV command example {"command": "destroyTV", "thingVisorID": thingVisorID}
                //console.log("Destroying TV")

                const responseShutdown = await shutdown(0)
            
            } else if (payLoadObject.command==commandMappedPort) {
                //mapped_port command example {"command": "mapped_port", "port": {"1030/tcp": "32779"}}
                //PDTE_JUAN: ¿Standby? without decission about this... vs Query to Database System

                var responseStartThingVisor

                responseStartThingVisor = await startThingVisor(payLoadObject.port[notificacion_port_container+'/tcp'])

//                console.log("responseStartThingVisor")
//                console.log(responseStartThingVisor)

                //PDTE_JUAN: TODO process responseStartThingVisor value (true or false) send topic message¿?¿?

            } else {
                console.error("invalid command (" + payLoadObject.command + ") in topic '" + topic + "'");                      
            }

        } else if (topicLevelElement[0]==MQTTbrokerApiKeyvThing && topicLevelElement[topicLevelLength-1]==MQTTbrokerTopic_c_in_Control) {
            //Handling "vThing/vThingID/c_in" message
            //console.log("Handling vThing/vThingID/c_in")

            //const payLoadObject = JSON.parse(payload.toString());
            const payLoadObject = JSON.parse(payload.toString().replace(/'/g, '"'));
            
            if (payLoadObject.command==commandGetContextRequest) {
                //getContextRequest command example {"command": "getContextRequest", "vSiloID": vSiloID, "vThingID": vThingID}
                //console.log("Handling getContextRequest.")

                const entities = get_context(payLoadObject.vThingID)
                
                //Send sendGetContextResponse
                const sendGetContextResponseResponse = await sendGetContextResponse(payLoadObject.vThingID,payLoadObject.vSiloID,entities)

                if (sendGetContextResponseResponse) {
                    //console.log('Operation has been completed successfully');
                } else {
                    console.error("Handling getContextRequest fails.")
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

//Mapping error function
clientMosquittoMqttData.on("error", function(error) {
    try {
        clientMosquittoMqttData.reconnect()
        return;
    } catch(e) {
      //log.error(error.toString());
      console.error(e.toString());
      return;
    }
})

//Mapping reconnect function
clientMosquittoMqttData.on("reconnect", function(a) {
    try {
        console.log(util.unixTime(Date.now()) + " - Reconnecting clientMosquittoMqttData...")
        return;
    } catch(e) {
      //log.error(error.toString());
      console.error(e.toString());
      return;
    }
})

/*
//Launch ThingVisor...
if (handleCBSubscriptions==false) {
    // ********** Periodic process.
    setInterval(async function() {
        try {
            var vThingDataProvider
            var resultSendMQTT

            console.log("")
            console.log("")
            console.log("**********" + util.unixTime(Date.now()) + " ***************")

            vThingDataProvider = await obtainDataProvider(vThingList,ocb_ip,ocb_port,ocb_service,ocb_servicePath)

            if (vThingDataProvider.length>0) {
        
                resultSendMQTT = await processDataProvider(vThingDataProvider, MQTTbrokerIP, MQTTbrokerPort, thingVisorID, MQTTbrokerUsername, MQTTbrokerPassword,
                                                    MQTTbrokerApiKeyvThing, MQTTbrokerTopicData)    
            }
        } catch(e) {
            console.error("setInterval: " + e.toString())
            return false
        }
    }, 10000); //default 5 seconds.
}
*/

//const app = require('./app')
    
//Consume Orion Context Broker notifications..
app.post(config.pathNotification, async function(req,res) {
    try {
        console.log("")
        console.log(util.unixTime(Date.now()) + " - POST /notification")
    
        const dataBody = req.body.data

        if (isGreedy) {
        
            for(var i = 0; i < dataBody.length; i++) {
            
                const dataBodyLD = libfromNGSIv2.fromNGSIv2toNGSILD(dataBody[i],"")

                const responseSendDataMQTT = await sendDataMQTT(dataBody[i], dataBodyLD)
                   
            }
        } else {

            //console.log(req.body.data)
            //PDTE_JUAN:TODO ver el tratamiento con el enfoque nuevo, si afecta en algo...

            for(var i = 0; i < dataBody.length; i++) {

                var entityv2TV = {}

                entityv2TV.id = dataBody[i].id
                //Changing entity type.
                entityv2TV.type = valuevThingTypeLD

                for(let attr in dataBody[i]){
                    if ( attr != "id" && attr != "type"){
                        if ( ocb_attrList.length == 0 ) {
                            entityv2TV[attr] = dataBody[i][attr]
                        } else {
                            for(var k = 0; k < ocb_attrList.length; k++) {
                                if (ocb_attrList[k] == attr) {
                                    try {
                                        entityv2TV[dest_ocb_attrList[k]] = dataBody[i][attr]
                                    } catch(e) {
                                        console.log("Mapping NGSI-LD attribute - not found for '" + attr + "'")
                                    }
                                    break;
                                }
                            }
                        } 

                    }
                }

                //Obtain "@context"
                if (typeof dataBody[i]["@context"] !== 'undefined' && typeof entityv2TV["@context"] === "undefined") {
                    entityv2TV["@context"] = dataBody[i]["@context"]
                }

                 //Obtain "dateCreated"
                if (typeof dataBody[i].dateCreated !== 'undefined' && typeof entityv2TV.dateCreated === 'undefined') {
                    entityv2TV.dateCreated = dataBody[i].dateCreated
                }
                
                //Obtain "dateModified"
                if (typeof dataBody[i].dateModified !== 'undefined' && typeof entityv2TV.dateModified === 'undefined') {
                    entityv2TV.dateModified = dataBody[i].dateModified
                }                
                //Obtain timestamp
                if (typeof dataBody[i].timestamp !== 'undefined' && typeof entityv2TV.timestamp === 'undefined') {
                    entityv2TV.timestamp = dataBody[i].timestamp
                }

                //Obtain "location"
                if (typeof dataBody[i].location !== 'undefined' && typeof entityv2TV.location === 'undefined') {
                    entityv2TV.location = dataBody[i].location
                }

                const dataBodyLD = libfromNGSIv2.fromNGSIv2toNGSILD(entityv2TV,"")

                if (isAggregated) {
                    const responseStoreData = await storeData(dataBody[i], dataBodyLD)
                } else {
                    const responseSendDataMQTT = await sendDataMQTT(dataBody[i], dataBodyLD)
                }
            }
        }
        res.status(200).send({description: 'Operation has been completed successfully'})
    } catch(e) {
        res.status(500).send({ error: e })
    }
})

// Launch service.
app.listen(notificacion_port_container,() => {        
    console.log(util.unixTime(Date.now()) + ` - API running, port: ${notificacion_port_container}`)

    //var obtainMappedTVPort = false
    //while (obtainMappedTVPort == false) {

        //console.log("(1)Try to obtain mapped TV port: " + util.unixTime(Date.now()))

        setTimeout(function() {  //PDTE_JUAN: TODO to obtain mapped port??? --> without decission about send a topic message or Query to Database System.

            console.log("")
            console.log(util.unixTime(Date.now()) + " - Try to obtain mapped TV port...")
                
            var MongoClient = require('mongodb').MongoClient;
            //var url = "mongodb://155.54.99.118:27018/viriotDB";
            var url = "mongodb://"+systemDatabaseIP+":"+systemDatabasePort;
            //"mongodb://155.54.99.118:27018";
            const dbName = 'viriotDB';

            console.info('Mongoose openning connection...'+url);

            MongoClient.connect(url, { useNewUrlParser: true }, async function(err, client) {

                const db = client.db(dbName);
            
                var query = {"thingVisorID": thingVisorID};

                await db.collection("thingVisorC").findOne(query, async function(err, result) {
                    if (err) throw err;
                    
                    //console.log(typeof result)
                    //console.log(result)
                    //console.log(result.port[notificacion_port_container+'/tcp'])

                    mapped_port = result.port[notificacion_port_container+'/tcp']

                    console.log("Mapped port to Thingvisor: " + mapped_port)
                    
                    var responseStartThingVisor = await startThingVisor()

    //                console.log("responseStartThingVisor")
    //                console.log(responseStartThingVisor)

                    //PDTE_JUAN: TODO process responseStartThingVisor value (true or false) send topic message¿?¿?

    //                obtainMappedTVPort = true
                });

                client.close();
            }); 
        }, 5000); //Wait 5 seconds before access database system.
    //}

})

async function startThingVisor() {
    try {
        //console.log("startThingVisor")

        var responseInitProces = await initProcess()

        //if (isGreedy) {
        //    responseInitProces = await greedyProcess()
        //} else {
        //    responseInitProces = await noGreedyProcess()
        //}

//        console.log("responseInitProces")
//        console.log(responseInitProces)

        //PDTE_JUAN: TODO process responseInitProces value (true or false) send topic message¿?¿?

        console.log("")
        console.log("******* ThingVisor is completly configured!!! *******")

        return responseInitProces

    } catch(e) {
        console.error("startThingVisor: " + e.toString())
        return false
    }  
}


async function initProcess() {
    try {
        console.log("")
        console.log("******* Start ThingVisor - INIT PROCESS *******")
        
        //STEP 1: Obtain all Orion Context Broker entities, the request are limited by a register fixed number (100). This process store the
        //traceability between NGSI-v2 id and NGSI-LD id.

        for(var h = 0; h < ocb_service.length;h++) {
            var obtainMore = true
            var offset = 100
            var actualOffset = 0
            var limit = 100
            var numEntities = 0

            var keyVThingID = 0
            var entityGroupCounter = 0

            while (obtainMore) {

                var responseCBEntities

                try {
                    //Obtain actual entities in Context Broker
                    if (isGreedy) {
                        responseCBEntities = await orion.obtainALLCBEntities(actualOffset, limit, ocb_ip, ocb_port, ocb_service[h], ocb_servicePath)
                    } else {
                        //PDTE_JUAN:TODO aqui afectará en algo seguro porque la forma de seleccionar 
                        //ya no es por service/servicepath/type sino que depende de los array configurados...
                        //y de la potencia que estos ofrezcan...
                        responseCBEntities = await orion.obtainALLCBEntitiesPerType(actualOffset, limit, ocb_ip, ocb_port, ocb_service[h], ocb_servicePath, ocb_type)    
                    }
                    
                } catch(e){
                    console.error(e)
                    if(e.message.indexOf("statusCode=404") <= -1) {
                        obtainMore=false
                        return false
                    }
                }
                
                if (obtainMore && responseCBEntities.length>0) {
                    //Processing response, 
                    for(var i = 0; i < responseCBEntities.length;i++) {

                        //const valuevThingLocalID = Date.now() + "-" + i
                        var valuevThingLocalID

                        if (isGroupingByType) {
                            //Find if entity service/servicepath/type is in the array to obtain the corresponding keyVThingID value.

                            var element = ocb_service[h] + "_" + ocb_servicePath + "_" + responseCBEntities[i].type
                            var valueIndex = obtainArrayIndex(typeServiceList,element)

                            if (valueIndex!=-1) { //Found.
                                keyVThingID = valueIndex
                            } else { //Not Found.
                                typeServiceList.push(element)
                                keyVThingID = obtainArrayIndex(typeServiceList,element)
                            }

                        } else {
                            if (entitiesPerVThingID != 0 && entityGroupCounter >= entitiesPerVThingID && isGreedy) {
                                //New vThingID
                                entityGroupCounter = 0
                                keyVThingID = keyVThingID + 1
                            }
                        }

                        valuevThingLocalID = keyVThingID //+ "-" + entityGroupCounter

                        if (isGreedy) {
                            vThingList.push({
                                rThingID: responseCBEntities[i].id, //Used by "orionSubscription" function.
                                rThingType: responseCBEntities[i].type, //Used by "orionSubscription" function.
                                rThingService: ocb_service[h], //Used by "orionSubscription" function.
                                vThingLD: libWrapperUtils.format_uri(responseCBEntities[i].type,responseCBEntities[i].id),
                                vThingLocalID: valuevThingLocalID,
                                vThingID: thingVisorID + "/" + valuevThingLocalID,
                                data: libfromNGSIv2.fromNGSIv2toNGSILD(responseCBEntities[i],"") //Establishing data_context 
                            })
                        } else {
                            
                            //NGSI-LD type entity, changing to calculate vThingLD and data
                            responseCBEntities[i].type = valuevThingTypeLD //NGSI-LD type entity, 

                            vThingListInternalTV.push({
                                rThingID: responseCBEntities[i].id,
                                rThingType: responseCBEntities[i].type,   //Real type entity
                                //rThingType: ocb_type,                   //Real type entity
                                rThingService: ocb_service[h], //Used by "orionSubscription" function.
                                vThingLD: libWrapperUtils.format_uri(responseCBEntities[i].type,responseCBEntities[i].id),
                                data: libfromNGSIv2.fromNGSIv2toNGSILD(responseCBEntities[i],"")
                            })
                        }

                        numEntities = numEntities + 1

                        //if (entitiesPerVThingID != 0 && isGreedy) {
                        entityGroupCounter = entityGroupCounter + 1
                        //}

                    }

                    // responseCBEntities.length<limit --> No more entities in Orion Context Broker
                    if (responseCBEntities.length<limit) {
                        obtainMore=false
                    } else {
                        actualOffset = actualOffset + offset
                    }
                } else {
                    obtainMore=false
                }
            }

            console.log("Orion Context Broker entities number: " + numEntities)
            
            //Defining vThings for noGreedy Thingvisor
            if (isGreedy == false) {

                //PDTE_JUAN TODO...  Create a function to do it...
                for(var i = 0; i < vThingListInternalTV.length;i++) {
                    vThingList.push({
                        rThingID: vThingListInternalTV[i].rThingID,         //Used by "orionSubscription" function.
                        rThingType: vThingListInternalTV[i].rThingType,     //Used by "orionSubscription" function.
                        rThingService: vThingListInternalTV[i].rThingService, //Used by "orionSubscription" function.
                        vThingLD: vThingListInternalTV[i].vThingLD,
                        vThingLocalID: valuevThingTypeLD,                  //In this case, valuevThingTypeLD is used to define vThingLocalID & vThingID
                        vThingID: thingVisorID + "/" + valuevThingTypeLD,
                        data: vThingListInternalTV[i].data                  //Establishing data_context 
                    })
                }
            }
        }

//        console.log("vThing List after init process: ")
//        console.log(vThingList)

        //STEP 2: Establishing topic's subscriptions using vThingID of vThingList array.
        //STEP 3: Subscribe to Orion Context Broker.
        //STEP 4: Send createVThings topic message to Master-Controller.
        const responseInitProcessAux = await initProcessAux()

//        console.log("responseInitProcessAux")
//        console.log(responseInitProcessAux)

        //PDTE_JUAN: TODO process responseInitProcessAux value (true or false) send topic message¿?¿?

        return true

    } catch(e) {
        console.error("initProcess: " + e.toString())
        return false
    }
}

/*
//To subscribe to all Orion Context Broker entities NO Greedy TV.
async function noGreedyProcess() {
    try{
        //console.log("noGreedyProcess")

        //STEP 1: Obtain all Orion Context Broker entities, the request are limited by a register fixed number (100). This process store the
        //traceability between NGSI-v2 id and NGSI-LD id.

        //PDTE_JUAN: TODO --> podria necesitarse para esto la función "obtainDataProvider" ya que en este punto tenemos que saber id y type
        //de la entidad ya que tenemos que crear vThingList como se hace en "greedyProcess", si tenemos el id y type por params entonces no necesitamos
        //este paso porque podremos crear el array directamente. Si va por params, habría que poner la validación al arrancar el proceso.
        
        //STEP 2: Establishing topic's subscriptions using vThingID of vThingList array.
        //STEP 3: Subscribe to Orion Context Broker.
        //STEP 4: Send createVThings topic message to Master-Controller.
        const responseInitProcessAux = await initProcessAux()

//        console.log("responseInitProcessAux")
//        console.log(responseInitProcessAux)

        //PDTE_JUAN: TODO process responseInitProcessAux value (true or false) send topic message¿?¿?

        return true
        
    } catch(e) {
        console.error("noGreedyProcess: " + e.toString())
        return false
    }
}
*/

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

function obtainArrayIndex(array,element) {
    try {
        return array.indexOf(element)
    }
     catch(e) {
        console.error(e.toString());
        return -1
    }
}


//Auxiliar init process TV.
async function initProcessAux() {
    try {

        //STEP 2: Establishing topic's subscriptions using vThingID of vThingList array.
        var counter = 0
        var topicArray = []
                       
        for(var i = 0; i < vThingList.length;i++) {
            //"/vThing/vThingID/c_in" topic

            const topicElement = MQTTbrokerApiKeyvThing + "/" + vThingList[i].vThingID + "/" + MQTTbrokerTopic_c_in_Control
            //topicArray.push(MQTTbrokerApiKeyvThing + "/" + vThingList[i].vThingID + "/" + MQTTbrokerTopic_c_in_Control)

            //To avoid two equals subscriptions.
            if (findArrayElement(mqttSubscriptionList,topicElement) == false && findArrayElement(topicArray,topicElement) == false ) {
                topicArray.push(topicElement)
       
                counter = counter + 1    
            }

            if (counter==10 || i == vThingList.length-1 ) {
                        
                if (subscribeMQTT(topicArray,'0',thingVisorID) == false) {
                    console.error("Error - connecting MQTT-server: Can't subscribe topics.")
                    return false
                } else {

                    //Push into mqttSubscriptionList array new topic subscriptions array
                    mqttSubscriptionList = mqttSubscriptionList.concat(topicArray)
                }
       
                counter = 0
                topicArray = []
            }
        }
       
        console.log("")
        console.log("MQTT Subscription Topic List: ")
        console.log(mqttSubscriptionList)
              
        //STEP 3: Subscribe to Orion Context Broker.
        var responseOrionSubscription

        if (isGroupingByType) {
            responseOrionSubscription = await orionSubscriptionByType()    
        } else {
            responseOrionSubscription = await orionSubscription()    
        }
//        console.log("responseOrionSubscription")
//        console.log(responseOrionSubscription)
       
        //PDTE_JUAN: TODO process responseOrionSubscription value (true or false) send topic message¿?¿?

        //console.log("ThingVisor subscribed to all Orion Context Broker entities.")

        //STEP 4: Send createVThings topic message to Master-Controller.
        var responseSendCreateVThingMessages
        responseSendCreateVThingMessages = await sendCreateVThingMessages()
               
//        console.log("responseSendCreateVThingMessages")
//        console.log(responseSendCreateVThingMessages)
               
        //PDTE_JUAN: TODO process responseSendCreateVThingMessages value (true or false) send topic message¿?¿?

        //console.log("ThingVisor sent createVThings topic message to Master-Controller.")

        return true

    } catch(e) {
        console.error("initProcessAux: " + e.toString())
        return false
    }

}

//Send vThingID data_context Aggregated Value
async function sendDataMQTT_AggregatedValue(){

    try {

        var vThingIDValue = ""

        var totalFreeParkingSpaces = 0
        var maxObservedAt = ""
        var dateObserved

        var date = new Date();

        dateObserved = util.ISODateString(date)

        for(var i = 0; i < vThingList.length;i++) {

            if (vThingIDValue == "") {
                vThingIDValue = vThingList[i].vThingID
            }

            if (typeof vThingList[i].data.freeParkingSpaces.value !== 'undefined') {
                totalFreeParkingSpaces = totalFreeParkingSpaces + vThingList[i].data.freeParkingSpaces.value
            }

            if (typeof vThingList[i].data.observedAt.value['@value'] !== 'undefined' && 
                vThingList[i].data.observedAt.value['@value'] > maxObservedAt) {
                
                maxObservedAt = vThingList[i].data.observedAt.value['@value']
            }
        }

        if (maxObservedAt == "") {
            maxObservedAt = dateObserved
        }

        if (vThingListAggValueContext.length == 0) {
            vThingListAggValueContext.push(
                {   
                    type: 'parkingsite',
                    totalFreeParkingSpaces: { type: 'Property', value: totalFreeParkingSpaces },
                    '@context': 
                        [ 'http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld',
                          'https://odins.org/smartParkingOntology/parkingsite-context.jsonld' ],
                    observedAt: 
                        { type: 'Property',
                        value: { '@type': 'DateTime', '@value': maxObservedAt } },
                    id: 'urn:ngsi-ld:parkingsite:vThingParkingSite' 
                } 
            )
        } else {
            vThingListAggValueContext[0].totalFreeParkingSpaces.value = totalFreeParkingSpaces
            vThingListAggValueContext[0].observedAt.value['@value'] = maxObservedAt

        }
       
        //It sent to MQTT data broker when change.
        if (globalTotalFreeParkingSpaces != totalFreeParkingSpaces || globalMaxObservedAt != maxObservedAt) {

            globalTotalFreeParkingSpaces = totalFreeParkingSpaces 
            globalMaxObservedAt = maxObservedAt

            if (vThingIDValue != "") {

                //const vThingIDValue = libWrapperUtils.format_uri(dataBody.type,dataBody.id)
                //const topic = MQTTbrokerApiKeyvThing + "/" + vThingIDValue + "/" + MQTTbrokerTopicData;

                const topic = MQTTbrokerApiKeyvThing + "/" + vThingIDValue + "/" + MQTTbrokerTopicDataOut;
                    
                //const topicMessage = {"data": [dataBodyLD], "meta": {"vThingID": vThingIDValue}}
                const topicMessage = {"data": vThingListAggValueContext, "meta": {"vThingID": vThingIDValue}}

                console.log("Sending message... " + topic + " " + JSON.stringify(topicMessage));

                //await clientMosquittoMqttData.publish(topic, JSON.stringify(dataBodyLD), {qos: 0}, function (err) {
                await clientMosquittoMqttData.publish(topic, JSON.stringify(topicMessage), {qos: 0}, function (err) {
                    if (!err) {
                        //console.log("Message has been sent correctly.")
                    } else {
                        console.error("ERROR: Sending MQTT message (publish): ",err)
                    }
                })
            }
        }

        return true

    } catch(e) {
        console.error("sendDataMQTT_AggregatedValue: " + e.toString())
        return false
    }
}


//Obtain vThingID data_context
function get_context(vThingID){
    try {

        var dataContext = []

        if (isGreedy || isAggregated == false) {
            for(var i = 0; i < vThingList.length;i++) {
                if (vThingList[i].vThingID == vThingID) {
                    dataContext.push(vThingList[i].data)    
                }
            }
        } else {
            for(var i = 0; i < vThingListAggValueContext.length;i++) {
                if (vThingListAggValueContext[i].vThingID == vThingID) {
                    dataContext.push(vThingListAggValueContext[i].data)    
                }
            }
        }

        return dataContext

    } catch(e) {
        console.error("get_context: " + e.toString())
        return []
    }
}

//Send vThingID getContextResponse message.
async function sendGetContextResponse(vThingID,vSiloID,entities) {
    try {

        //Silos Controller sends the response to Master-Controller ( vSilo/<ID>/c_out destroyVSilo).

        //"/vSilo/<ID>/c_out" topic
        const topic = MQTTbrokerApiKeySilo + "/" + vSiloID + "/" + MQTTbrokerTopic_c_in_Control;

        const body = {"command": commandGetContextResponse, "data": entities, "meta": {"vThingID": vThingID}}

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

//Create mqtt subscriptions.
async function subscribeMQTT(topicArray,param,identify) {
    try {
                     
        //console.log("Subscribe topics: ")
        //console.log(topicArray)
        await clientMosquittoMqttControl.subscribe(topicArray, {qos: 0}, function (err, granted) {
            if (!err) {
                /*if (param == '0') {
                    console.log("Successfully thingVisor topic subscription: '" + identify + "'") 
                } else {
                    console.log("Successfully topic's subscription")    
                }*/
                //console.log(granted)
                //console.log("Successfully topic's subscription '" + identify + "': " + granted)
                //console.log("Successfully topic's subscription '" + identify + "'.")
                //console.log(granted)
            } else {
                /*if (param == '0') {
                    console.error("Error thingVisor topic subscription: '" + identify + "' - : " + err) 
                } else {
                    console.error("Error topic's subscription: " + err)    
                }*/
                //clientMosquittoMqttControl.end()
                console.error("Error topic's subscription '" + identify + "': " + err)
                return false
            }
        })
        //clientMosquittoMqttControl.end()
        return true

    } catch(e) {
        console.error(e.toString());
        return false
    }
}

//Unsubscribe mqtt.
async function unsubscribeMQTT(topicArray) {
    try {

        //console.log("Unsubscribe topics: ")
        //console.log(topicArray)
        await clientMosquittoMqttControl.unsubscribe(topicArray, function (err) {

            if (!err) {
                //console.log("Successfully topic's unsubscription")    
            } else {

                console.error("Error topic's unsubscription: " + err)    
                return false
            }
        })

        return true

    } catch(e) {
        console.error(e.toString());
        return false
    }
}

//Create Orion Context Broker subscriptions.
async function orionSubscription() {
    try {
        
        console.log("orionSubscription")
        var vThingListCopy

        if (isGreedy) {
            vThingListCopy = vThingList
        } else {
            vThingListCopy = vThingListInternalTV
        }

        for(var h = 0; h < ocb_service.length;h++) {

            console.log("ocb_service[h]: " + ocb_service[h])

            //Obtain all Orion Context Broker Subscriptions, the request are limited by a register fixed number (100).
            var obtainMore = true
            var offset = 100
            var actualOffset = 0
            var limit = 100

            urlNotify = notificacion_protocol + '://' + notify_ip + ':' + mapped_port + notify_service

            //console.log("urlNotify: " + urlNotify)

            while (obtainMore) {

                var responseCBSubscriptions

                try {
                    //Obtain actual subscriptions in Context Broker
                    responseCBSubscriptions = await orion.obtainCBSubscriptions(actualOffset, limit, ocb_ip, ocb_port, ocb_service[h], ocb_servicePath)
                } catch(e){
                    console.error(e)
                    if(e.message.indexOf("statusCode=404") <= -1) {
                        obtainMore=false
                        return false
                    }
                }
                
                if (obtainMore && responseCBSubscriptions.length>0) {
                    //Processing response
                    for(var i = 0; i < responseCBSubscriptions.length;i++) {
                        //Compare notification URL subscription and urlNotify variable value.

                        if (responseCBSubscriptions[i].notification.http.url==urlNotify) {
                            
                            //Find in the vThingListCopy array an element with the same service, type and id 
                            //as the subscriptions ones.
                            //ocb_service[h]
                            //responseCBSubscriptions.subject.entities[0].type
                            //responseCBSubscriptions.subject.entities[0].id

                            var elementIndex = -1

                            for(var k = 0; k < vThingListCopy.length;k++) {
                                if (ocb_service[h]==vThingListCopy[k].rThingService && 
                                    responseCBSubscriptions[i].subject.entities[0].type==vThingListCopy[k].rThingType && 
                                    responseCBSubscriptions[i].subject.entities[0].id==vThingListCopy[k].rThingID) {
                                    elementIndex = k
                                    break;
                                }
                            }

                            //If we find the id in the vThingListCopy, we remove the item (found)
                            if (elementIndex!=-1) {
                                vThingListCopy.splice(elementIndex, 1);    
                            }
                        }
                    }

                    // responseCBSubscriptions.length<limit --> No more subscriptions in Orion Context Broker
                    // vThingListCopy.length --> All virtual things was found
                    if (responseCBSubscriptions.length<limit || vThingListCopy.length==0) {
                        obtainMore=false
                    } else {
                        actualOffset = actualOffset + offset
                    }
                } else {
                    obtainMore=false
                }
            }
        }

        console.log("")
        console.log("Subscriptions number to create in Orion Context Broker: " + vThingListCopy.length)

        //There are entities without Orion Context Broker subscription, we need create it.
        if (vThingListCopy.length>0) {

            //console.log("Creating Orion Context Broker subscriptions...")

            for(var i = 0; i < vThingListCopy.length;i++) {

                //Defining subscription body
                var subscriptionOCB = {}
                subscriptionOCB.description = "TV: " + thingVisorID + " subscription."
                subscriptionOCB.subject = {entities: [{id: vThingListCopy[i].rThingID, type: vThingListCopy[i].rThingType}]};  
                subscriptionOCB.notification = {}
                subscriptionOCB.notification.http = {url: urlNotify}

                //Preparing subscription request.
                const instance = axios.create({
                    baseURL: 'http://' + ocb_ip + ':' + ocb_port
                })

                var headersPost = {}

                headersPost["Content-Type"] = 'application/json';

                if (vThingListCopy[i].rThingService.length != 0) {
                    headersPost["fiware-service"] = vThingListCopy[i].rThingService;
                }
        
                if (ocb_servicePath.length != 0) {
                    headersPost["fiware-servicepath"] = ocb_servicePath;
                }

                const optionsAxios = {
                    headers: headersPost
                    //,params: { options : 'skipInitialNotification' }
                }
        
                var responsePost
        
                try {
                    //Creamos la suscripción en OCB
                    responsePost = await instance.post(`/v2/subscriptions`, subscriptionOCB, optionsAxios)

                    const location=responsePost.headers['location']
                    const subscriptionIdOCB = location.split('/')[3]

                    if (typeof subscriptionIdOCB === 'undefined' || subscriptionIdOCB.length == 0 ) {
                        console.error("Error - connecting Orion Context Broker: Can't obtain information - subscriptionId.")
                        return false
                    } else {


                        var foundID = false
                        for(var k = 0; k < subscriptionIdOCBList.length;k++) {
                            if (subscriptionIdOCBList[k].IdOCB == subscriptionIdOCB && 
                                subscriptionIdOCBList[k].Service == vThingListCopy[i].rThingService) {
                                foundID = true
                                break;
                            }
                        }

                        if (foundID == false) {
                            //console.log("registra subscriptionIdOCBList: " + JSON.stringify({IdOCB: subscriptionIdOCB, Service: vThingListCopy[i].rThingService}))
                            subscriptionIdOCBList.push({IdOCB: subscriptionIdOCB, Service: vThingListCopy[i].rThingService})
                        }

                        //if (findArrayElement(subscriptionIdOCBList,subscriptionIdOCB) == false) {
                        //    subscriptionIdOCBList.push(subscriptionIdOCB)
                        //}

                        //subscriptionIdOCBList.push(subscriptionIdOCB)
                        //console.log(subscriptionOCB.description + " --> Created subscription: " + subscriptionIdOCB)
                    }
                } catch(e) {
                    console.error("Error - connecting Orion Context Broker: Can't subscribe '" + subscriptionOCB.description + "': " + e.toString())
                    return false
                }
            }    
        }

        console.log("")
        console.log("Subscriptions list created in Orion Context Broker: ")
        console.log(subscriptionIdOCBList)

        return true

    } catch(e) {
        console.error("orionSubscription: " + e.toString())
        return false
    }
}

//Create Orion Context Broker subscriptions.
async function orionSubscriptionByType() {
    try {

        console.log("orionSubscriptionByType")
        var vThingListCopy

        if (isGreedy) {
            vThingListCopy = vThingList
        } else {
            vThingListCopy = vThingListInternalTV
        }

        var arrayTextServiceTypes = []
        var arrayObjectServiceTypes = []
        //Obtain all service/type pairs from real entities.
        for(var h = 0; h < vThingListCopy.length;h++) {

            var element = vThingListCopy[h].rThingService + "_" + vThingListCopy[h].rThingType

            if (obtainArrayIndex(arrayTextServiceTypes,element) == -1) {
                arrayTextServiceTypes.push(element)    
                arrayObjectServiceTypes.push({
                    rThingType: vThingListCopy[h].rThingType,
                    rThingService: vThingListCopy[h].rThingService
                })
            }
        }

        for(var h = 0; h < ocb_service.length;h++) {

            //Obtain all Orion Context Broker Subscriptions, the request are limited by a register fixed number (100).
            var obtainMore = true
            var offset = 100
            var actualOffset = 0
            var limit = 100

            urlNotify = notificacion_protocol + '://' + notify_ip + ':' + mapped_port + notify_service

            //console.log("urlNotify: " + urlNotify)

            while (obtainMore) {

                var responseCBSubscriptions

                try {
                    //Obtain actual subscriptions in Context Broker
                    responseCBSubscriptions = await orion.obtainCBSubscriptions(actualOffset, limit, ocb_ip, ocb_port, ocb_service[h], ocb_servicePath)
                } catch(e){
                    console.error(e)
                    if(e.message.indexOf("statusCode=404") <= -1) {
                        obtainMore=false
                        return false
                    }
                }
                
                if (obtainMore && responseCBSubscriptions.length>0) {
                    //Processing response
                    for(var i = 0; i < responseCBSubscriptions.length;i++) {
                        //Compare notification URL subscription and urlNotify variable value.

                        if (responseCBSubscriptions[i].notification.http.url==urlNotify) {
                            
                            //Find in the arrayServiceTypes array an element with the same service and type 
                            //as the subscriptions ones.
                            //ocb_service[h]
                            //responseCBSubscriptions.subject.entities[0].type
                            //responseCBSubscriptions.subject.entities[0].id

                            var element = ocb_service[h] + "_" + responseCBSubscriptions[i].subject.entities[0].type

                            var elementIndex = obtainArrayIndex(arrayTextServiceTypes,element)

                            if (elementIndex != -1 && 
                                responseCBSubscriptions[i].subject.entities[0].idPattern==".*") {
                                
                                    arrayTextServiceTypes.splice(elementIndex, 1);  
                                    arrayObjectServiceTypes.splice(elementIndex, 1);  
                            }
                        }
                    }

                    // responseCBSubscriptions.length<limit --> No more subscriptions in Orion Context Broker
                    // arrayObjectServiceTypes.length --> All virtual things types was found
                    if (responseCBSubscriptions.length<limit || arrayObjectServiceTypes.length==0) {
                        obtainMore=false
                    } else {
                        actualOffset = actualOffset + offset
                    }
                } else {
                    obtainMore=false
                }
            }
        }

        console.log("")
        console.log("Subscriptions number to create in Orion Context Broker: " + arrayObjectServiceTypes.length)

        //There are entities without Orion Context Broker subscription, we need create it.
        if (arrayObjectServiceTypes.length>0) {

            //console.log("Creating Orion Context Broker subscriptions...")

            for(var i = 0; i < arrayObjectServiceTypes.length;i++) {

                //Defining subscription body
                var subscriptionOCB = {}
                subscriptionOCB.description = "TV: " + thingVisorID + " subscription."
                subscriptionOCB.subject = {entities: [{idPattern: ".*", type: arrayObjectServiceTypes[i].rThingType}]};  
                subscriptionOCB.notification = {}
                subscriptionOCB.notification.http = {url: urlNotify}

                //Preparing subscription request.
                const instance = axios.create({
                    baseURL: 'http://' + ocb_ip + ':' + ocb_port
                })

                var headersPost = {}

                headersPost["Content-Type"] = 'application/json';

                if (arrayObjectServiceTypes[i].rThingService.length != 0) {
                    headersPost["fiware-service"] = arrayObjectServiceTypes[i].rThingService;
                }
        
                if (ocb_servicePath.length != 0) {
                    headersPost["fiware-servicepath"] = ocb_servicePath;
                }

                const optionsAxios = {
                    headers: headersPost
                    //,params: { options : 'skipInitialNotification' }
                }
        
                var responsePost
        
                try {
                    //Creamos la suscripción en OCB
                    responsePost = await instance.post(`/v2/subscriptions`, subscriptionOCB, optionsAxios)

                    const location=responsePost.headers['location']
                    const subscriptionIdOCB = location.split('/')[3]

                    if (typeof subscriptionIdOCB === 'undefined' || subscriptionIdOCB.length == 0 ) {
                        console.error("Error - connecting Orion Context Broker: Can't obtain information - subscriptionId.")
                        return false
                    } else {


                        var foundID = false
                        for(var k = 0; k < subscriptionIdOCBList.length;k++) {
                            if (subscriptionIdOCBList[k].IdOCB == subscriptionIdOCB && 
                                subscriptionIdOCBList[k].Service == arrayObjectServiceTypes[i].rThingService &&
                                subscriptionIdOCBList[k].Type == arrayObjectServiceTypes[i].rThingType) {
                                foundID = true
                                break;
                            }
                        }

                        if (foundID == false) {
                            //console.log("registra subscriptionIdOCBList: " + JSON.stringify({IdOCB: subscriptionIdOCB, 
                            //            Service: arrayObjectServiceTypes[i].rThingService, Type: arrayObjectServiceTypes[i].rThingType}))

                            subscriptionIdOCBList.push({IdOCB: subscriptionIdOCB, 
                                                        Service: arrayObjectServiceTypes[i].rThingService,
                                                        Type: arrayObjectServiceTypes[i].rThingType
                                                    })
                        }

                        //if (findArrayElement(subscriptionIdOCBList,subscriptionIdOCB) == false) {
                        //    subscriptionIdOCBList.push(subscriptionIdOCB)
                        //}

                        //subscriptionIdOCBList.push(subscriptionIdOCB)
                        //console.log(subscriptionOCB.description + " --> Created subscription: " + subscriptionIdOCB)
                    }
                } catch(e) {
                    console.error("Error - connecting Orion Context Broker: Can't subscribe '" + subscriptionOCB.description + "': " + e.toString())
                    return false
                }
            }    
        }

        console.log("")
        console.log("Subscriptions list created in Orion Context Broker: ")
        console.log(subscriptionIdOCBList)

        return true

    } catch(e) {
        console.error("orionSubscription: " + e.toString())
        return false
    }
}


//Send VThings createVThing message in topics.
async function sendCreateVThingMessages() {
    try {

        console.log("")

        var vThingIDArray = []

        //The TV sends a "TV/<ID>/c_out createVThing" message per vThing.
        for(var i = 0; i < vThingList.length;i++) {
            //"/vThing/vThingID/c_out" topic

            const topic = MQTTbrokerApiKeyThingVisor + "/" + thingVisorID + "/" + MQTTbrokerTopic_c_out_Control;

            if (findArrayElement(vThingIDArray,vThingList[i].vThingID) == false) {

                vThingIDArray.push(vThingList[i].vThingID)

                var body

                if (isGreedy) {
                    if (isGroupingByType) {
                        body = {"command": commandCreateVThing, "thingVisorID": thingVisorID, 
                        "vThing": {label: "Type:" + vThingList[i].rThingType + " # Service:" + vThingList[i].rThingService + " # ServicePath:" + ocb_servicePath, 
                                id: vThingList[i].vThingID, 
                                description: ""}}
                    } else if (entitiesPerVThingID == 1) {
                        body = {"command": commandCreateVThing, "thingVisorID": thingVisorID, 
                        "vThing": {label: "id:" + vThingList[i].rThingID + " # Type:" + vThingList[i].rThingType + " # Service:" + vThingList[i].rThingService + " # ServicePath:" + ocb_servicePath, 
                                id: vThingList[i].vThingID, 
                                description: ""}}
                    } else {
                        body = {"command": commandCreateVThing, "thingVisorID": thingVisorID, 
                        "vThing": {label: "Service:" + vThingList[i].rThingService + " # ServicePath:" + ocb_servicePath, 
                                id: vThingList[i].vThingID, 
                                description: ""}}
                    }
                } else {
                    body = {"command": commandCreateVThing, "thingVisorID": thingVisorID, 
                        "vThing": {label: "Service:" + vThingList[i].rThingService + " # ServicePath:" + ocb_servicePath, 
                                id: vThingList[i].vThingID, 
                                description: ""}}
                }
                

                console.log("Sending message... " + topic + " " + JSON.stringify(body));
                    
                await clientMosquittoMqttControl.publish(topic, JSON.stringify(body), {qos: 0}, function (err) {
                    if (!err) {
                        //console.log("Message has been sent correctly.")
                    } else {
                        console.error("ERROR: Sending MQTT message (publish): ",err)
                    }
                })
            }
           
        }

        return true

    } catch(e) {
        console.error(e.toString());
        return false
    }
}



async function sendDataMQTT(dataBody, dataBodyLD) {
    try {
        //Obtain vThingID
        //Find in the vThingList array an element with the same type and id as notification entity ones.
        //dataBody.type
        //dataBody.id

        var vThingIDValue = await storeData(dataBody, dataBodyLD)

        //for(var k = 0; k < vThingList.length;k++) {
        //    if (dataBody.type==vThingList[k].rThingType && dataBody.id==vThingList[k].rThingID) {
        //        vThingIDValue = vThingList[k].vThingID
        //        vThingList[k].data = dataBodyLD //Updating data_context
        //        break;
        //    }
        //}

        //If we find it
        if (vThingIDValue!="") {
            //const vThingIDValue = libWrapperUtils.format_uri(dataBody.type,dataBody.id)
            //const topic = MQTTbrokerApiKeyvThing + "/" + vThingIDValue + "/" + MQTTbrokerTopicData;

            const topic = MQTTbrokerApiKeyvThing + "/" + vThingIDValue + "/" + MQTTbrokerTopicDataOut;
                
            const topicMessage = {"data": [dataBodyLD], "meta": {"vThingID": vThingIDValue}}

            console.log("Sending message... " + topic + " " + JSON.stringify(topicMessage));

            //await clientMosquittoMqttData.publish(topic, JSON.stringify(dataBodyLD), {qos: 0}, function (err) {
            await clientMosquittoMqttData.publish(topic, JSON.stringify(topicMessage), {qos: 0}, function (err) {
                if (!err) {
                    //console.log("Message has been sent correctly.")
                } else {
                    console.error("ERROR: Sending MQTT message (publish): ",err)
                }
            })
                    
        } else {
            //PDTE_JUAN: TODO Handle error situation.
        }

        return true

    } catch(e) {
        console.error("sendDataMQTT: " + e.toString())
        return false
    }  
}


async function storeData(dataBody, dataBodyLD) {
    try {
        //Obtain vThingID
        //Find in the vThingList array an element with the same type and id as notification entity ones.
        //dataBody.type
        //dataBody.id

        var vThingIDValue = ""

        for(var k = 0; k < vThingList.length;k++) {
            if (dataBody.type==vThingList[k].rThingType && dataBody.id==vThingList[k].rThingID) {
                vThingIDValue = vThingList[k].vThingID
                vThingList[k].data = dataBodyLD //Updating data_context
                break;
            }
        }
        return vThingIDValue

    } catch(e) {
        console.error("storeData: " + e.toString())
        return ""
    }  
}


//Delete Orion Context Broker subscriptions.
async function orionUnsubscription(subscriptionCBArray) {
    try {

        //console.log("orionUnsubscription")

        var test = true

        //Definimos baseURL de axios según la URl de OCB source.
        const instance = axios.create({
                baseURL: 'http://' + ocb_ip + ':' + ocb_port
        })

        for(var i = 0; i < subscriptionCBArray.length;i++) {

            var headersDelete = {}
            headersDelete["Accept"] = 'application/json';

            if (subscriptionCBArray[i].Service.length != 0) {
                headersDelete["fiware-service"] = subscriptionCBArray[i].Service;
            }
                
            if (ocb_servicePath.length != 0) {
                headersDelete["fiware-servicepath"] = ocb_servicePath;
            }

            try {
                console.log("Deleting: " + subscriptionCBArray[i].IdOCB)
                const responseDel = await instance.delete(`/v2/subscriptions/${subscriptionCBArray[i].IdOCB}`, 
                        { headers: headersDelete })
                console.log("Deleted: " + subscriptionCBArray[i].IdOCB)
            } catch(e) {
                console.error("Error - connecting Orion Context Broker: Can't unsubscribe: " + e.toString())
                test = false
            }
        }

        return test

    } catch(e) {
        console.error("orionUnsubscription: " + e.toString())
        return false

    }
}


//Send delete messages in topics.
async function sendDeleteMessages() {
    try {
                  
        var vThingIDArray = []

        //The TV sends a "vThing/vThingID/c_out deleteVThing" message per vThing.
        for(var i = 0; i < vThingList.length;i++) {
            //"/vThing/vThingID/c_out" topic

            const topic = MQTTbrokerApiKeyvThing + "/" + vThingList[i].vThingID + "/" + MQTTbrokerTopic_c_out_Control;

            if (findArrayElement(vThingIDArray,topic) == false) {
                
                vThingIDArray.push(topic)

                const body = {"command": commandDeleteVThing, "vThingID": vThingList[i].vThingID}
                console.log("Sending message... " + topic + " " + JSON.stringify(body));
                    
                await clientMosquittoMqttControl.publish(topic, JSON.stringify(body), {qos: 0}, function (err) {
                    if (!err) {
                        //console.log("Message has been sent correctly.")
                    } else {
                        console.error("ERROR: Sending MQTT message (publish): ",err)
                    }
                })
            }
        }

        //The TV sends the response to Master-Controller ( TV/<ID>/c_out destroyTV). 

        //"TV/<ID>/c_out" topic
        const topic = MQTTbrokerApiKeyThingVisor + "/" + thingVisorID + "/" + MQTTbrokerTopic_c_out_Control;

        const body = {"command": commandDestroyTVAck, "thingVisorID": thingVisorID}

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

/*
//Obtain entities from Orion Context Broker.
async function obtainDataProvider(vThingArray,ocb_ip,ocb_port,ocb_service,ocb_servicePath) {
    try {
        var entitiesOCB = []

        for(var i = 0; i < vThingArray.length;i++) {

            var responseOCB
            try {
                //Launch Orion Context Broker request
                responseOCB = await orion.obtainCBEntity(vThingArray[i],ocb_service, ocb_servicePath, ocb_ip, ocb_port);    

                if (responseOCB.id == vThingArray[i]) {
                    entitiesOCB.push(responseOCB)
                }

            } catch(e) {
                if(e.message.indexOf("statusCode=404") <= -1) {
                    console.error("Error Entity: " + vThingArray[i] + " : " + e.toString())
                }
            }
        }
        return entitiesOCB

    } catch(e) {
        console.error("obtainDataProvider: " + e.toString())
        return []
    }
}
*/

/*
//Publish mqtt.
async function processDataProvider(vThingDataProvider, MQTTbrokerIP, MQTTbrokerPort, thingVisorID, MQTTbrokerUsername, MQTTbrokerPassword,
                            MQTTbrokerApiKeyvThing, MQTTbrokerTopicData) {

    try {
        for(var i = 0; i < vThingDataProvider.length; i++) {

            //Obtain entity data body
            const dataBody = vThingDataProvider[i] 

            const topic = MQTTbrokerApiKeyvThing + "/" + dataBody.id + "/" + MQTTbrokerTopicData;
        
            console.log("Sending message... " + topic + " " + JSON.stringify(dataBody));
        
            await clientMosquittoMqttControl.publish(topic, JSON.stringify(dataBody), {qos: 0}, async function (err) {
                if (!err) {
                    console.log("Message has been sent correctly.")
                    } else {
                    console.error("ERROR: Sending MQTT message (publish): ",err)
                }
            })
        }

        return true

    } catch(e) {
        console.error("processDataProvider: " + e.toString())
        return false
    }
}
*/

async function shutdown(param) {

    try {

        //STEP 1: The TV unsubscribes from all active subscription.
        var responseOrionUnsubscription

        console.log('Orion Context Broker subscriptions deleting...');

        //Subscribe to Orion Context Broker.

        responseOrionUnsubscription = await orionUnsubscription(subscriptionIdOCBList)

        if (responseOrionUnsubscription) {
            subscriptionIdOCBList = []
        }

        //PDTE_JUAN: TODO process responseOrionUnsubscription value (true or false) send topic message¿?¿?

        console.log('All Orion Context Broker subscriptions deleted.');
        console.log('MQTT Subscriptions deleting...');

        const response_unsubscribeMQTT = await unsubscribeMQTT(mqttSubscriptionList)

        if (response_unsubscribeMQTT) {
            //Emptly mqttSubscriptionList
            mqttSubscriptionList = []
        }

        //PDTE_JUAN: TODO process response_unsubscribeMQTT value (true or false) send topic message¿?¿?
        console.log('MQTT Subscriptionsd deleted.');
        console.log('MQTT Delete messages sending...');

        //STEP 2: The TV sends a "vThing/vThingID/c_out deleteVThing" message per vThing. 
        //When Silos receives then "vThing/vThingID/c_out" with "deleteVThing", it will do 
        //the same as when handle "vSilo/vSiloID/c_in deleteVThing".

        //TV also sends the response to Master-Controller ( TV/<ID>/c_out destroyTV).  
        //Master-Controller receives the information. It cancels DB information and topic subscriptions and kills the TV container. 

        const response_sendDeleteMessages = await sendDeleteMessages()

        if (response_sendDeleteMessages) {
            //Emptly vThingList
            vThingListInternalTV = []
            vThingList = []
            vThingListAggValueContext = []
        }

        //PDTE_JUAN: TODO process response_sendDeleteMessages value (true or false) send topic message¿?¿?
        console.log('MQTT Delete Messages sent.');

        clientMosquittoMqttControl.end()
        clientMosquittoMqttData.end()
        //console.log('MQTT disconnected.');

        console.log('ThingVisor stopped, exiting now');
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

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
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

//PDTE_JUAN: TODO remove or update?
// To capture signals.
const capt_signals = ['SIGHUP', 'SIGINT', 'SIGTERM'];

//PDTE_JUAN: TODO remove or update?
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



// PERIODIC PROCESS - NO GREEDY.
setInterval(async  function() {
    if (isAggregated) {
        sendDataMQTT_AggregatedValue()
    }
}, config.frecuency_mseg);  
