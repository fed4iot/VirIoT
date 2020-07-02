/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

'use strict'

const app = require('./app')

const axios = require('axios');

const config = require('./config')

var orion = require("./orion");

var util = require("./util")

const entitiesDM = require('./DataModels/entities')

var libWrapperUtils = require("./wrapperUtils")
var libfromNGSIv2 = require("./fromNGSIv2")

var mqtt = require('mqtt')

var guid = require('guid')

var isGreedy
var isAggregated
// DEPRECATED isGroupingByType
//var isGroupingByType
var isActuator
var vThingLocalIDAggregated

var vThingList = []
var vThingListAggValueContext = []

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

var noGreedyListService
//var noGreedyListServicePath
var noGreedyListTypes
var noGreedyListTypesAttributes
var noGreedyListDestTypes
var noGreedyListDestAttributesTypes

var smartParkingStandardDM_use
var smartParkingStandardDM_Service
var smartParkingStandardDM_ListTypes
var smartParkingStandardDM_Attributes

/* DEPRECATED
var parkingsite_id
var parkingsite_disSpacePCCapacity
var parkingsite_maxHeight
var parkingsite_carWash
var parkingsite_valet
var parkingsite_phoneNumber
var parkingsite_webSite
var parkingsite_mail
var parkingsite_address
*/

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

// DEPRECATED isGroupingByType
//var entitiesPerVThingID = 0


var MQTTbrokerUsername
var MQTTbrokerPassword

var commandDestroyTV
var commandDestroyTVAck
var commandDeleteVThing
var commandCreateVThing
var commandGetContextRequest
var commandGetContextResponse

var mapped_port
var urlNotify
var subscriptionIdOCBList = []

//var mqttSubscriptionList = []
var mqttSubscriptionListData = []
var mqttSubscriptionListControl = []

var typeServiceList = []

var subscriptionIdOCBCommandAttributeList = []
var subscriptionIdOCBCommandAttributeListAux = []

var vSiloCommandRequestHistory = []


//var options
var optionsData
var optionsControl

//var clientMosquittoMqtt
var clientMosquittoMqttData
var clientMosquittoMqttControl

console.log("")
console.log("")
console.log("**********" + util.unixTime(Date.now()) + " ***************")


try {

    systemDatabaseIP=config.systemDatabaseIP
    if (systemDatabaseIP == '' || typeof systemDatabaseIP === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'systemDatabaseIP' param not found.")
        return
    }

    systemDatabasePort = config.systemDatabasePort
    if (systemDatabasePort == '' || typeof systemDatabasePort === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'systemDatabasePort' param not found.")
        return
    }

    thingVisorID = config.thingVisorID
    if (thingVisorID == '' || typeof thingVisorID === 'undefined') {
        console.error("Error - processing ThingVisor's environment variables: 'thingVisorID' param not found.")
        return
    }

    notificacion_port_container = config.notificacion_port_container || ''

} catch(e) {
    console.error("Processing environment's variables - Error: " + e.toString())
    return
}

function settingConfiguration(notify_ipArg, paramsArg,MQTTDataBrokerIPArg, MQTTDataBrokerPortArg, MQTTControlBrokerIPArg, MQTTControlBrokerPortArg) {

    try {

        ocb_service = []
        ocb_servicePath = []

        notificacion_protocol = ""
        notify_service = ""

        // DEPRECATED isGroupingByType
        //entitiesPerVThingID = 0

        MQTTDataBrokerIP = MQTTDataBrokerIPArg
        MQTTDataBrokerPort = MQTTDataBrokerPortArg
        
        MQTTControlBrokerIP = MQTTControlBrokerIPArg
        MQTTControlBrokerPort = MQTTControlBrokerPortArg
        
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
        commandDeleteVThing = config.commandDeleteVThing
        commandCreateVThing = config.commandCreateVThing
        commandGetContextRequest = config.commandGetContextRequest
        commandGetContextResponse = config.commandGetContextResponse

        //params = obtainParams(paramsArg)
        params = paramsArg

        isGreedy = config.isGreedy
        if (typeof isGreedy === "undefined") {
            //isGreedy = true
            console.error("Error - processing ThingVisor's configuration: 'isGreedy' is undefined.")
            return false
        }

        isAggregated = config.isAggregated
        if (typeof isAggregated === "undefined") {
            //isAggregated = false
            console.error("Error - processing ThingVisor's configuration: 'isAggregated' is undefined.")
            return false
        }

        isActuator = config.isActuator
        if (typeof isActuator === "undefined") {
            //isAggregated = false
            console.error("Error - processing ThingVisor's configuration: 'isActuator' is undefined.")
            return false
        }
        if ( (isActuator && (isGreedy || isAggregated)) || (isGreedy && isAggregated) ) {
            //isActuator == false
            console.error("Error - processing ThingVisor's configuration: 'isGreedy', 'isAggregated', 'isActuator' only one can be true.")
            return false
        }

        // DEPRECATED isGroupingByType
        //isGroupingByType = config.isGroupingByType || true
        //if (typeof isGroupingByType === "undefined" && isGreedy) {
        //    isGroupingByType = true
        //}


        vThingLocalIDAggregated = config.vThingLocalIDAggregated

        if (params == '' || typeof params === 'undefined' || 
            params.ocb_ip == '' || typeof params.ocb_ip === 'undefined') {
            console.error("Error - processing ThingVisor's environment variables: 'ocb_ip' param not found.")
            return false
        }

        if (params == '' || typeof params === 'undefined' || 
            params.ocb_port == '' || typeof params.ocb_port === 'undefined') {
            console.error("Error - processing ThingVisor's environment variables: 'ocb_port' param not found.")
            return false
        }

        if (MQTTDataBrokerIP == '' || typeof MQTTDataBrokerIP === 'undefined') {
            console.error("Error - processing ThingVisor's environment variables: 'MQTTDataBrokerIP' param not found.")
            return false
        }

        if (MQTTDataBrokerPort == '' || typeof MQTTDataBrokerPort === 'undefined') {
            console.error("Error - processing ThingVisor's environment variables: 'MQTTDataBrokerPort' param not found.")
            return false
        }

        if (MQTTControlBrokerIP == '' || typeof MQTTControlBrokerIP === 'undefined') {
            console.error("Error - processing ThingVisor's environment variables: 'MQTTControlBrokerIP' param not found.")
            return false
        }

        if (MQTTControlBrokerPort == '' || typeof MQTTControlBrokerPort === 'undefined') {
            console.error("Error - processing ThingVisor's environment variables: 'MQTTControlBrokerPort' param not found.")
            return false
        }

        ocb_ip = params.ocb_ip
        ocb_port = params.ocb_port

        //Obtaining mapping attributes/type configuration from config.js file (by default)
        noGreedyListService = config.noGreedyListService || [""]
        //noGreedyListServicePath = config.noGreedyListServicePath || '/#'
        noGreedyListTypes = config.noGreedyListTypes
        noGreedyListTypesAttributes = config.noGreedyListTypesAttributes
        noGreedyListDestTypes = config.noGreedyListDestTypes
        noGreedyListDestAttributesTypes = config.noGreedyListDestAttributesTypes

        smartParkingStandardDM_use = params.StdDataModel || false
        smartParkingStandardDM_Service = config.smartParkingStandardDM_Service || [""]
        
        //In case it doesn't use mapping attributes/type configuration from config.js file, and OCB has the same configuration use require Mapping to smartparking standard Data Model.
        if (isGreedy == false && isAggregated == false && isActuator == false && smartParkingStandardDM_use) {

            noGreedyListService = smartParkingStandardDM_Service

            smartParkingStandardDM_ListTypes = []
            smartParkingStandardDM_Attributes = []

            //Obtains ListTypes and their attributes from entitiesDM, and includes it on smartParkingStandardDM_ListTypes and smartParkingStandardDM_Attributes
            var typeList = []
            var attributesTypeList = []

            for (var typeKey in entitiesDM) {

                    if (Object.keys(entitiesDM[typeKey]).length > 0) {

                        typeList.push(typeKey)

                        var attributesList = []

                        for (var attrKey in entitiesDM[typeKey]) {

                            if (findArrayElement(["id","type","@context"],attrKey) == false) {
                                attributesList.push(attrKey)
                            }

                        }

                        attributesTypeList.push(attributesList)
                    }
            }

            smartParkingStandardDM_ListTypes.push(typeList)
            smartParkingStandardDM_Attributes.push(attributesTypeList)

            console.log("Standard DataModel mapping - Supported Types.")
            console.log(JSON.stringify(smartParkingStandardDM_ListTypes))
            console.log("Standard DataModel mapping - Supported Attributes by type.")
            console.log(JSON.stringify(smartParkingStandardDM_Attributes))

            noGreedyListTypes = smartParkingStandardDM_ListTypes
            noGreedyListTypesAttributes = smartParkingStandardDM_Attributes
            noGreedyListDestTypes = noGreedyListTypes
            noGreedyListDestAttributesTypes = noGreedyListTypesAttributes
        }

        if (isGreedy) {
            ocb_service = params.ocb_service || [""]

            //ocb_servicePath = '/#'
            if (ocb_service.length == 0) {
                ocb_servicePath.push('/#')
            } else {
                for(var i = 0; i < ocb_service.length;i++){
                    ocb_servicePath.push('/#')
                }    
            }
        } else {
            //ocb_service = noGreedyListService || [""]
            if (typeof params.ocb_service === 'undefined') {
                ocb_service = noGreedyListService || [""]
            } else {
                ocb_service = params.ocb_service
            }
            
            //ocb_servicePath = noGreedyListServicePath
            //TODO: ocb_servicePath = config.noGreedyListServicePath || [['/#']]

            if (typeof params.ocb_servicePath === 'undefined') {
                if (ocb_service.length == 0) {
                    if (isActuator) {
                        ocb_servicePath.push('/')
                    } else {
                        ocb_servicePath.push('/#')    
                    }
                } else {
                    for(var i = 0; i < ocb_service.length;i++){
                        if (isActuator) {
                            ocb_servicePath.push('/')
                        } else {
                            ocb_servicePath.push('/#')    
                        }
                    }    
                }
            } else {
                ocb_servicePath = params.ocb_servicePath

            }
        }

        if (isGreedy || isActuator) {  //For compatibility with initProcess only (nested "for" statements)
            ocb_type = []

            for(var i = 0; i < ocb_service.length;i++){
                ocb_type.push([i])
            }
        } else {
            ocb_type = noGreedyListTypes
        }

        ocb_attrList = noGreedyListTypesAttributes

        dest_ocb_type = noGreedyListDestTypes

        dest_ocb_attrList = noGreedyListDestAttributesTypes

        /* DEPRECATED
        parkingsite_id = config.parkingsite_id
        parkingsite_disSpacePCCapacity = config.parkingsite_disSpacePCCapacity
        parkingsite_maxHeight = config.parkingsite_maxHeight
        parkingsite_carWash = config.parkingsite_carWash
        parkingsite_valet = config.parkingsite_valet
        parkingsite_phoneNumber = config.parkingsite_phoneNumber
        parkingsite_webSite = config.parkingsite_webSite
        parkingsite_mail = config.parkingsite_mail
        parkingsite_address = config.parkingsite_address
        */

        //Configuration controls...
        if (isGreedy == false && isActuator == false) {

            //noGreedyListService.length>0
            if (noGreedyListService.length <= 0 || typeof noGreedyListService === 'undefined') {
                console.error("Error - processing ThingVisor's configuration params: invalid length (noGreedyListService).")
                return false
            }

            //noGreedyListTypes.length>0
            if (noGreedyListTypes.length <= 0 || typeof noGreedyListTypes === 'undefined') {
                console.error("Error - processing ThingVisor's configuration params: invalid length (noGreedyListTypes).")
                return false
            }

            //noGreedyListTypesAttributes.length>0
            if (noGreedyListTypesAttributes.length <= 0 || typeof noGreedyListTypesAttributes === 'undefined') {
                console.error("Error - processing ThingVisor's configuration params: invalid length (noGreedyListTypesAttributes).")
                return false
            }

            //noGreedyListDestTypes.length>0
            if (noGreedyListDestTypes.length <= 0 || typeof noGreedyListDestTypes === 'undefined') {
                console.error("Error - processing ThingVisor's configuration params: invalid length (noGreedyListDestTypes).")
                return false
            }

            //noGreedyListDestAttributesTypes.length>0
            if (noGreedyListDestAttributesTypes.length <= 0 || typeof noGreedyListDestAttributesTypes === 'undefined') {
                console.error("Error - processing ThingVisor's configuration params: invalid length (noGreedyListDestAttributesTypes).")
                return false
            }

            //noGreedyListService.length == noGreedyListTypes.length
            if (noGreedyListService.length != noGreedyListTypes.length) {
                console.error("Error - processing ThingVisor's configuration params: (noGreedyListService/noGreedyListTypes) have different first level length.")
                return false
            }

            //noGreedyListTypes.length == noGreedyListTypesAttributes.length
            if (noGreedyListTypes.length != noGreedyListTypesAttributes.length) {
                console.error("Error - processing ThingVisor's configuration params: (noGreedyListTypes/noGreedyListTypesAttributes) have different first level length.")
                return false
            }

            //noGreedyListTypes.length == noGreedyListDestTypes.length
            if (noGreedyListTypes.length != noGreedyListDestTypes.length) {
                console.error("Error - processing ThingVisor's configuration params: (noGreedyListTypes/noGreedyListDestTypes) have different first level length.")
                return false
            }

            //noGreedyListDestTypes.length == noGreedyListDestAttributesTypes.length
            if (noGreedyListDestTypes.length != noGreedyListDestAttributesTypes.length) {
                console.error("Error - processing ThingVisor's configuration params: (noGreedyListDestTypes/noGreedyListDestAttributesTypes) have different first level length.")
                return false
            }

            for(var i = 0; i < noGreedyListService.length;i++){

                //noGreedyListTypes[i].length != 0
                if (noGreedyListTypes[i].length == 0) {
                    console.error("Error - processing ThingVisor's configuration params: invalid length (noGreedyListTypes second level).")
                    return false
                }

                //noGreedyListDestTypes[i].length != 0
                if (noGreedyListDestTypes[i].length == 0) {
                    console.error("Error - processing ThingVisor's configuration params: invalid length (noGreedyListDestTypes second level).")
                    return false
                }

                //noGreedyListTypes[i].length == noGreedyListTypesAttributes[i].length
                if (noGreedyListTypes[i].length != noGreedyListTypesAttributes[i].length) {
                    console.error("Error - processing ThingVisor's configuration params: (noGreedyListTypes/noGreedyListTypesAttributes) have different second level length.")
                    return false
                }

                //noGreedyListTypes[i].length == noGreedyListDestTypes[i].length
                if (noGreedyListTypes[i].length != noGreedyListDestTypes[i].length) {
                    console.error("Error - processing ThingVisor's configuration params: (noGreedyListTypes/noGreedyListDestTypes) have different second level length.")
                    return false
                }

                for(var k = 0; k < noGreedyListTypes[i].length;k++){
                    //noGreedyListTypes[i][k] != '' NO SUPPORTED
                    if (noGreedyListTypes[i][k] == "") {
                        console.error("Error - processing ThingVisor's configuration params: invalid value '' (noGreedyListTypes second level).")
                        return false
                    }

                    //noGreedyListDestTypes[i][k] != '' NO SUPPORTED
                    if (noGreedyListDestTypes[i][k] == "") {
                        console.error("Error - processing ThingVisor's configuration params: invalid value '' (noGreedyListDestTypes second level).")
                        return false
                    }
                }

                //noGreedyListTypesAttributes[i].length == noGreedyListDestAttributesTypes[i].length
                if (noGreedyListTypesAttributes[i].length != 0 && noGreedyListTypesAttributes[i].length != noGreedyListDestAttributesTypes[i].length) {
                    console.error("Error - processing ThingVisor's configuration params: (noGreedyListTypesAttributes/noGreedyListDestAttributesTypes) have different second level length.")
                    return false
                }

                for(var k = 0; k < noGreedyListTypesAttributes[i].length;k++){
                    //noGreedyListTypesAttributes[i][k].length == noGreedyListDestAttributesTypes[i][k].length
                    if (noGreedyListTypesAttributes[i][k].length != 0 && noGreedyListTypesAttributes[i][k].length != noGreedyListDestAttributesTypes[i][k].length) {
                        console.error("Error - processing ThingVisor's configuration params: (noGreedyListTypesAttributes/noGreedyListDestAttributesTypes) have different third level length.")
                        return false
                    }

                    for(var l = 0; l < noGreedyListTypesAttributes[i][k].length;l++){
                        //noGreedyListTypesAttributes[i][k][l] != '' NO SUPPORTED
                        if (noGreedyListTypesAttributes[i][k][l] == "") {
                            console.error("Error - processing ThingVisor's configuration params: invalid value '' (noGreedyListTypesAttributes third level).")
                            return false
                        }

                        //noGreedyListDestAttributesTypes[i][k][l] != '' NO SUPPORTED
                        if (noGreedyListDestAttributesTypes[i][k][l] == "") {
                            console.error("Error - processing ThingVisor's configuration params: invalid value '' (noGreedyListDestAttributesTypes third level).")
                            return false
                        }
                    }
                }
            }
        }

        /* ****************************************************************************************************** */

        notificacion_protocol = params.notificacion_protocol || 'http'
        notify_ip = notify_ipArg
        notify_service = config.pathNotification
       
        
        if (notify_ip=="") {
            console.error("Error - processing ThingVisor's environment variables: 'notify_ip' param not found.")
            return
        }
        
        // DEPRECATED isGroupingByType
        //entitiesPerVThingID = parseInt(params.entitiesPerVThingID || '0')
        //if (entitiesPerVThingID < 0){
        //    entitiesPerVThingID = 0
        //}

        MQTTbrokerUsername = params.MQTTbrokerUsername || ''
        MQTTbrokerPassword = params.MQTTbrokerPassword || ''

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

        return true
        
    } catch(e) {
        console.error("settingConfiguration - Error: " + e.toString())
        return false
    }

    // body...
}

setTimeout(async function() {

    console.log("")
    console.log(util.unixTime(Date.now()) + " - Try to obtain mapped TV port...")
                
    var MongoClient = require('mongodb').MongoClient;
    var url = "mongodb://"+systemDatabaseIP+":"+systemDatabasePort;
    const dbName = 'viriotDB';

    console.info('Mongoose openning connection...'+url);

    MongoClient.connect(url, { useNewUrlParser: true }, async function(err, client) {

        const db = client.db(dbName);
            
        var query = {"thingVisorID": thingVisorID};

        await db.collection("thingVisorC").findOne(query, async function(err, result) {
            if (err) throw err;
            
            var notify_ipTV        
            var paramsTV
            var MQTTDataBrokerIPTV
            var MQTTDataBrokerPortTV
            var MQTTControlBrokerIPTV
            var MQTTControlBrokerPortTV

            try {

                notify_ipTV = result.IP || params.notify_ip || ""
                console.log("Gateway to Thingvisor: " + notify_ipTV)

                mapped_port = result.port[notificacion_port_container+'/tcp'] || 0
                console.log("Mapped port to Thingvisor: " + mapped_port)

                //paramsTV = obtainParams(result.params) || obtainParams(config.providerParams) || {}
                paramsTV = obtainParams(result.params) || {}
                console.log("Params of Thingvisor: ")
                console.log(paramsTV)

                //MQTTDataBrokerIPTV = result.MQTTDataBroker.ip || config.MQTTDataBrokerIP || ""
                MQTTDataBrokerIPTV = result.MQTTDataBroker.ip ||  ""
                console.log("MQTT DataBroker IP: " + MQTTDataBrokerIPTV)

                //MQTTDataBrokerPortTV = result.MQTTDataBroker.port || config.MQTTDataBrokerPort || 0
                MQTTDataBrokerPortTV = result.MQTTDataBroker.port || 0
                console.log("MQTT DataBroker Port: " + MQTTDataBrokerPortTV)

                //MQTTControlBrokerIPTV = result.MQTTControlBroker.ip || config.MQTTControlBrokerIP || ""
                MQTTControlBrokerIPTV = result.MQTTControlBroker.ip || ""
                console.log("MQTT ControlBroker IP: " + MQTTControlBrokerIPTV)

                //MQTTControlBrokerPortTV = result.MQTTControlBroker.port || config.MQTTControlBrokerPort || 0
                MQTTControlBrokerPortTV = result.MQTTControlBroker.port || config.MQTTControlBrokerPort || 0
                console.log("MQTT ControlBroker Port: " + MQTTControlBrokerPortTV)
                    
            } catch(e) {
                console.error(e)
                notify_ipTV = ""
                mapped_port = 0
                paramsTV = {}
                MQTTDataBrokerIPTV = ""
                MTTDataBrokerPortTV = 0
                MQTTControlBrokerIPTV = ""
                MQTTControlBrokerPortTV = 0
            }

            if(notify_ipTV != "" && mapped_port != 0 && isEmpty(paramsTV) == false && MQTTDataBrokerIPTV != "" &&  MQTTDataBrokerPortTV != 0 &&
                MQTTControlBrokerIPTV != "" && MQTTControlBrokerPortTV != 0 ){

                if(settingConfiguration(notify_ipTV, paramsTV, MQTTDataBrokerIPTV, MQTTDataBrokerPortTV, MQTTControlBrokerIPTV, MQTTControlBrokerPortTV)) {
                    
                    console.log("settingConfiguration : true")
                
                } else {

                    console.log("settingConfiguration : false")

                }
            }

        });

        client.close();
    }); 

}, 5000); //Wait 5 seconds


setTimeout(async function() {
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
            console.log(util.unixTime(Date.now()) + " - MQTT Control Broker connected")
            //Establishing topic's subscriptions
            var topicArray = []
            var topicElement = MQTTbrokerApiKeyThingVisor + "/" + thingVisorID + "/" + MQTTbrokerTopic_c_in_Control

            //"/TV/thingVisorID/c_in" topic
            //topicArray.push(MQTTbrokerApiKeyThingVisor + "/" + thingVisorID + "/" + MQTTbrokerTopic_c_in_Control)
            topicArray.push(topicElement)

            if (subscribeMQTT(topicArray,'0',thingVisorID,"control") == false) {
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
          console.error(e.toString());
          return;
        }
    })

    //Mapping topic's subscriptions function
    clientMosquittoMqttControl.on("message", async function(topic, payload) {
        
        try {
            console.log("");
            console.log(util.unixTime(Date.now()) + " - Received topic: " + topic + " ; payload: " + payload.toString());
            
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

    //Mapping connect function
    clientMosquittoMqttData.on("connect", function() {
        try {

            console.log("")
            console.log(util.unixTime(Date.now()) + " - MQTT Data Broker connected")

            return
        } catch(e) {
          //log.error(error.toString());
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
          console.error(e.toString());
          return;
        }
    })

        //Mapping topic's subscriptions function
    clientMosquittoMqttData.on("message", async function(topic, payload) {
        
        try {
            console.log("");
            console.log(util.unixTime(Date.now()) + " - Received topic: " + topic + " ; payload: " + payload.toString());
            
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

            if (topicLevelElement[0]==MQTTbrokerApiKeyvThing && topicLevelElement[topicLevelLength-1]==MQTTbrokerTopicDataIn) {    

                if (isActuator) {

                    //Handling "vThing/vThingID/data_in" message
                    //console.log("Handling vThing/vThingID/data_in")

                    //const payLoadObject = JSON.parse(payload.toString());
                    const payLoadObject = JSON.parse(payload.toString().replace(/'/g, '"'));

                    var vThingAux = centralElement
                    //Format:
                    //{"meta":{"vSiloID":"vSiloID"},
                    // "data":[
                    //         {
                    //              "id":"NGSI-LD identifier"
                    //              "type":"NGSI-LD type"
                    //              "commandName":{
                    //                  "type": "Property",
                    //                  "value": {
                    //                       "cmd-value": ,
                    //                       "cmd-qos": , //optional, Default = 0
                    //                       "cmd-id": ,
                    //                       "cmd-nuri": ["viriot:/vSilo/<ID>/data_in"] //optional
                    //                  }
                    //              }
                    //          }
                    //   ]
                    //}

                    var vSiloIDValue = payLoadObject.meta.vSiloID

                    var vThingIDValue = centralElement

                    for(var i = 0; i < payLoadObject.data.length;i++){

                        var commandKey = ""

                        var rThingIDValue = ""
                        var rThingTypeValue = ""
                        var rThingServiceValue = ""
                        var rThingServicePathValue = ""

                        var testEntity = false
                        var testCommand = false

                        //Obtain command from payload
                        for(var key in payLoadObject.data[i]) {
                            if(key != "id" && key != "type") {
                                commandKey = key

                                //Obtain real data entity to send command and validate if command exist througth "NGSI-LD identifier"
                                for(var k = 0; k < vThingList.length;k++){
                                    if(vThingList[k].vThingLD == payLoadObject.data[i].id) {

                                        testEntity = true

                                        rThingIDValue = vThingList[k].rThingID
                                        rThingTypeValue = vThingList[k].rThingType
                                        rThingServiceValue = vThingList[k].rThingService
                                        rThingServicePathValue = vThingList[k].rThingServicePath

                                        if (findArrayElement(vThingList[k].data.commands.value,commandKey)) {
                                            testCommand = true
                                        }

                                        break
                                    }
                                }

                                if (testEntity == false) {
                                    //TODO:
                                } else if (testCommand == false) {
                                    //TODO:

                                } else {

                                    //1) Register vSilo Request (Historic):  [internalidentifier, cmd_id, command, cmd_nuri, cmd_value, cmd_qos]
                                    var guidObject = guid.create()
                                    var internalidentifier = guidObject.value


                                    var cmd_idValue = ""
                                    var cmd_nuriValue = ""
                                    var cmd_valueValue
                                    var cmd_qosValue = 0

                                    if(typeof payLoadObject.data[i][commandKey].value["cmd-id"] !== 'undefined') {
                                        cmd_idValue = payLoadObject.data[i][commandKey].value["cmd-id"].toString()
                                    }

                                    if(typeof payLoadObject.data[i][commandKey].value["cmd-nuri"] !== 'undefined') {
                                        cmd_nuriValue = payLoadObject.data[i][commandKey].value["cmd-nuri"]
                                    }

                                    if(typeof payLoadObject.data[i][commandKey].value["cmd-value"] !== 'undefined') {
                                        cmd_valueValue = payLoadObject.data[i][commandKey].value["cmd-value"]
                                    }

                                    if(typeof payLoadObject.data[i][commandKey].value["cmd-qos"] !== 'undefined') {
                                        cmd_qosValue = payLoadObject.data[i][commandKey].value["cmd-qos"]
                                    }

                                    vSiloCommandRequestHistory.push([internalidentifier,commandKey,payLoadObject,vThingAux])

                                    //Passing trazability identifier to device in "cmd-id", suppose device returns this identifier 
                                    //in the response.

                                    var cmdParams = {}
                                    cmdParams["value"] = cmd_valueValue
                                    cmdParams["cmd-id"] = internalidentifier.toString()

                                    //console.log("Request from vSilo:")
                                    //console.log(vSiloCommandRequestHistory)

                                    //2) Send command (updating broker)
                                    var responseSendCommandUpdatingBroker

                                    try {

                                        var bodyPayload = {
                                                            "id": rThingIDValue,   
                                                            "type": rThingTypeValue,   
                                                            "isPattern": "false",   
                                                            "attributes": [{       
                                                                "name": commandKey,       
                                                                "type": "command",       
                                                                "value": cmdParams       
                                                            }]    
                                                        }

                                        responseSendCommandUpdatingBroker = await orion.sendCommandUpdatingBroker(bodyPayload,ocb_ip, ocb_port, rThingServiceValue, rThingServicePathValue)

                                    } catch(e){
                                        console.error(e)
                                    }

                                    if (parseInt(cmd_qosValue) == 2) {

                                        var dataBodyLDmod = {}
                                        var obtainCommand = {}

                                        obtainCommand = JSON.parse(JSON.stringify(payLoadObject.data[i][commandKey].value))

                                        obtainCommand["cmd-status"] = "PENDING"

                                        var date = new Date();

                                        const timestampValue = util.ISODateString(date)

                                        dataBodyLDmod = {"id": payLoadObject.data[i].id, "type": payLoadObject.data[i].type}
                                        dataBodyLDmod[commandKey + "-status"] = {"type":"Property","value": obtainCommand, 
                                                                                 "TimeInstant": {"type":"Property","value": timestampValue}}

                                        //Obtaining vSilo topic to response.

                                        var listCMDNURI = processCMDNURI(obtainCommand["cmd-nuri"])

                                        if(listCMDNURI.length > 0) {
                                            const responseSendInfoStatusMQTT = await sendCommandInfoStatusMQTT(vSiloIDValue, vThingIDValue, dataBodyLDmod, listCMDNURI)
                                        } else  {
                                            console.log("Send using data_out topic (2).")
                                            const responseSendInfoStatusMQTT_data_out = await sendCommandInfoStatusMQTT_data_out(vThingIDValue, dataBodyLDmod)
                                        }
                                    }
                                }
                            }
                        }
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



}, 15000); //Wait 15 seconds


//Obtain the param value of an specific entity.
function obtainEntityDM(param) // min and max included
{

    return entitiesDM[param]

}

function isEmpty(obj) {
    for(var key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}

function obtainNGSILDPayload(service,dataBody){
    try  {

        var entityv2TV = {}

        entityv2TV.id = dataBody.id

        var date = new Date();

        const timestampValue = util.ISODateString(date)

        //Changing entity type.
        //1) Obtain service element index in ocb_service array
        var serviceIndex
        var typeIndex
        var typeResult

        serviceIndex = obtainArrayIndex(ocb_service,service)

        if (serviceIndex!=-1) { //Found.
            var typeIndex = obtainArrayIndex(ocb_type[serviceIndex],dataBody.type)
            //2) Obtain type element index in ocb_type
            if (typeIndex!=-1) {
                //3) Assing new type from dest_ocb_type
                entityv2TV.type = dest_ocb_type[serviceIndex][typeIndex]
                typeResult = dest_ocb_type[serviceIndex][typeIndex]
            }
        }

        if(typeof entityv2TV.type === 'undefined' || typeof typeResult === 'undefined'){
            console.error('Notification error: Building type... not found.')
            return {}
        } else {

            var entity_template

            var entityDataModel = {}

            var mappedAttr = []

            var isEntityDataModel = false

            //isAggregated == false condition is needed because, if we use a type defined in entities.js in dest_ocb_type array, 
            //it fails when aggregated data model entities are different than the entities.js one. 
            //If we won't this condition, we need to be careful. We must define types, in dest_ocb_type, 
            //are not included in entities.js file.
            if(isAggregated == false){
            //if((typeResult == 'parkingsite' || typeResult == 'parkingmeter') && isAggregated == false){
            //if(typeResult == 'parkingsite' || typeResult == 'parkingmeter'){
                if (typeof obtainEntityDM(typeResult) !== 'undefined'){

                    entity_template = obtainEntityDM(typeResult)
                    entityDataModel = JSON.parse(JSON.stringify(entity_template));

                    if(dataBody.id.startsWith("urn:ngsi-ld:")) {
                        entityDataModel.id = dataBody.id
                    } else {
                        entityDataModel.id = entityDataModel.id.replace("---",dataBody.id)
                    }
                    
                    isEntityDataModel = true                    
                }
            }

            for(let attr in dataBody){
                if ( attr != "id" && attr != "type"){
                    //Can recover all attributes
                    if (ocb_attrList[serviceIndex][typeIndex].length == 0 && isEntityDataModel == false) {
                        entityv2TV[attr] = dataBody[attr]
                    } else {

                        //Recover only attributes was defined.
                        for(var k = 0; k < ocb_attrList[serviceIndex][typeIndex].length; k++) {
                            if (ocb_attrList[serviceIndex][typeIndex][k] == attr) {
                                try {

                                    if (isEntityDataModel) {
                                        if ( dataBody[attr].type.toUpperCase() == "TEXT".toUpperCase() || 
                                            dataBody[attr].type.toUpperCase() == "STRING".toUpperCase() || 
                                            dataBody[attr].type.toUpperCase() == "NUMBER".toUpperCase() || 
                                            dataBody[attr].type.toUpperCase() == "STRUCTUREDVALUE".toUpperCase() ||
                                            dataBody[attr].type.toUpperCase() == "GEO:JSON".toUpperCase() ||
                                            dataBody[attr].type.toUpperCase() == "DATETIME".toUpperCase() ||
                                            dataBody[attr].type.toUpperCase() == "RELATIONSHIP".toUpperCase() ) {
                                                
                                            entityDataModel[dest_ocb_attrList[serviceIndex][typeIndex][k]].value = dataBody[attr].value
            
                                        } else if (dataBody[attr].type.toUpperCase() == "COORDS".toUpperCase() ||
                                                    dataBody[attr].type.toUpperCase() == "GEO:POINT".toUpperCase()) {
            
                                            entityDataModel[dest_ocb_attrList[serviceIndex][typeIndex][k]].value.coordinates = 
                                                [ parseFloat(dataBody[attr].value.split(",")[1]), parseFloat(dataBody[attr].value.split(",")[0]) ]
                                        } else if ( dataBody[attr].type.toUpperCase() == "GEO:POLYGON".toUpperCase()) {

                                            var aux = []
          
                                            for(var l=0; l< dataBody[attr].value.length; l++){

                                                aux.push([ parseFloat(dataBody[attr].value[l].split(",")[1]), parseFloat(dataBody[attr].value[l].split(",")[0]) ])
                                            }

           
                                            entityDataModel[dest_ocb_attrList[serviceIndex][typeIndex][k]].value.coordinates = [ aux ]

                                        }else if (dataBody[attr].type.toUpperCase() == "POINT".toUpperCase()) {
            
                                            entityDataModel[dest_ocb_attrList[serviceIndex][typeIndex][k]].value.coordinates = 
                                                //[ parseFloat(dataBody[attr].value.split(",")[1]), parseFloat(dataBody[attr].value.split(",")[0]) ]
                                                dataBody[attr].coordinates
                                        }
                                    }

                                    mappedAttr.push(attr)
        
                                    entityv2TV[dest_ocb_attrList[serviceIndex][typeIndex][k]] = dataBody[attr]

                                } catch(e) {

                                    console.log("Mapping NGSI-LD attribute - not found for '" + attr + "'")
                                }
                                break;
                            }
                        }
                    }
                }
            }

            var dataBodyLD

            if (isEntityDataModel == false) {
                //Obtain "@context"
                if (typeof dataBody["@context"] !== 'undefined' && typeof entityv2TV["@context"] === "undefined") {
                    entityv2TV["@context"] = dataBody["@context"]
                }

                //Obtain "dateCreated"
                if (typeof dataBody.dateCreated !== 'undefined' && typeof entityv2TV.dateCreated === 'undefined') {
                    entityv2TV.dateCreated = dataBody.dateCreated
                }

                //Obtain "dateModified"
                if (typeof dataBody.dateModified !== 'undefined' && typeof entityv2TV.dateModified === 'undefined') {
                    entityv2TV.dateModified = dataBody.dateModified
                }

                //Obtain timestamp
                if (typeof dataBody.timestamp !== 'undefined' && typeof entityv2TV.timestamp === 'undefined') {
                    entityv2TV.timestamp = dataBody.timestamp
                }

                //Obtain "location"
                if (typeof dataBody.location !== 'undefined' && typeof entityv2TV.location === 'undefined') {
                    entityv2TV.location = dataBody.location
                }

                dataBodyLD = libfromNGSIv2.fromNGSIv2toNGSILD(entityv2TV,"")

            } else {

                if(typeof entityDataModel.timestamp !== 'undefined'){
                    const timestampIndex = obtainArrayIndex(mappedAttr,"timestamp")
                    if (timestampIndex==-1) {
                        entityDataModel.timestamp.value = timestampValue
                    }
                }


                ////Additional information (config.js)
                //if (typeResult.toUpperCase() == "parkingsite".toUpperCase()) {
                //

                //    const timestampIndex = obtainArrayIndex(mappedAttr,"timestamp")
                //    if (timestampIndex==-1) {
                //        entityDataModel.timestamp.value = timestampValue
                //    }

                    /* DEPRECATED
                    //Find "id" in "parkingsite_id"
                    const idIndex = obtainArrayIndex(parkingsite_id,dataBody.id)

                    //If it exists, it obtains the additional information only when it wasn't mapped previously (mappedAttr).
                    if (idIndex!=-1) {

                        if(smartParkingStandardDM_use == false){


                            const disSpacePCCapacityIndex = obtainArrayIndex(mappedAttr,"disSpacePCCapacity")
                            if (disSpacePCCapacityIndex==-1) {
                                entityDataModel.disSpacePCCapacity.value = parkingsite_disSpacePCCapacity[idIndex]
                            }

                            const maxHeightIndex = obtainArrayIndex(mappedAttr,"maxHeight")
                            if (maxHeightIndex==-1) {
                                entityDataModel.maxHeight.value = parkingsite_maxHeight[idIndex]
                            }

                            const carWashIndex = obtainArrayIndex(mappedAttr,"carWash")
                            if (carWashIndex==-1) {
                                entityDataModel.carWash.value = parkingsite_carWash[idIndex]
                            }

                            const valetIndex = obtainArrayIndex(mappedAttr,"valet")
                            if (valetIndex==-1) {
                                entityDataModel.valet.value = parkingsite_valet[idIndex]
                            }

                            const phoneNumberIndex = obtainArrayIndex(mappedAttr,"phoneNumber")
                            if (phoneNumberIndex==-1) {
                                entityDataModel.phoneNumber.value = parkingsite_phoneNumber[idIndex]
                            }

                            const webSiteIndex = obtainArrayIndex(mappedAttr,"webSite")
                            if (webSiteIndex==-1) {
                                entityDataModel.webSite.value = parkingsite_webSite[idIndex]
                            }

                            const mailIndex = obtainArrayIndex(mappedAttr,"mail")
                            if (mailIndex==-1) {
                                entityDataModel.mail.value = parkingsite_mail[idIndex]
                            }
                                    
                            const addressIndex = obtainArrayIndex(mappedAttr,"address")
                            if (addressIndex==-1) {
                                entityDataModel.address.value = parkingsite_address[idIndex]
                            } 
                        }  

                    }
                    */
                //}

                dataBodyLD = libfromNGSIv2.fromNGSIv2toNGSILD(entityDataModel,"")

            }

            return dataBodyLD

        }

    } catch(e) {
            console.error("obtainNGSILDPayload: " + e.toString())
            return {}
    }        
}

//Consume Orion Context Broker notifications..
app.post(config.pathNotification, async function(req,res) {
    try {
        console.log("")
        console.log(util.unixTime(Date.now()) + " - POST /notification - " + req.body.subscriptionId)
    
        const dataBody = req.body.data

        //var service =req.headers['fiware-service'] || ""

        var service = ""
        var servicePath = ""
        var commandKey = ""

        var obtainSubscriptionInfo = false
        var isCommandNotification = false

        if (isActuator) {

            for(var k = 0; k < subscriptionIdOCBCommandAttributeList.length;k++) {
                if (subscriptionIdOCBCommandAttributeList[k].IdOCB == req.body.subscriptionId) {
                    service = subscriptionIdOCBCommandAttributeList[k].Service
                    servicePath = subscriptionIdOCBCommandAttributeList[k].ServicePath
                    commandKey = subscriptionIdOCBCommandAttributeList[k].Command
                    isCommandNotification = true
                    obtainSubscriptionInfo = true
                    break;
                }
            }

        } 

        if (obtainSubscriptionInfo == false)  {

            for(var k = 0; k < subscriptionIdOCBList.length;k++) {
                if (subscriptionIdOCBList[k].IdOCB == req.body.subscriptionId) {
                    service = subscriptionIdOCBList[k].Service
                    servicePath = subscriptionIdOCBList[k].ServicePath
                    obtainSubscriptionInfo = true
                    break;
                }
            }

        }



        if (obtainSubscriptionInfo) {
            
            if (isGreedy) {
        
                for(var i = 0; i < dataBody.length; i++) {
            
                    const dataBodyLD = libfromNGSIv2.fromNGSIv2toNGSILD(dataBody[i],"")

                    const responseSendDataMQTT = await sendDataMQTT(dataBody[i], dataBodyLD, service, servicePath)
                   
                }

            } else if (isActuator) {

                for(var i = 0; i < dataBody.length; i++) {

                    if (isCommandNotification == false) {

                        var deleteCommandKey = []
                        var commandList = []

                        for(var key in dataBody[i]) {

                            if(findArrayElement(["id","type","@context"],key) == false) {
                                if (typeof dataBody[i][key].type !== "undefined") {
                                    if (findArrayElement(["commandResult"],dataBody[i][key].type)) {
                                        deleteCommandKey.push(key)
                                        if (findArrayElement(commandList,key.substring(0,key.length-5)) == false) {
                                            commandList.push(key.substring(0,key.length-5))
                                        }
                                    } else if (findArrayElement(["commandStatus"],dataBody[i][key].type)) {
                                        deleteCommandKey.push(key)
                                        if (findArrayElement(commandList,key.substring(0,key.length-7)) == false) {
                                            commandList.push(key.substring(0,key.length-7))
                                        }
                                    } else if (findArrayElement(["command"],dataBody[i][key].type)) {
                                        deleteCommandKey.push(key)
                                        if (findArrayElement(commandList,key) == false) {
                                            commandList.push(key)
                                        }
                                    }
                                }
                            }

                        }  

                        //Delete unshared properties (commands) from payload.
                        for(var j = 0; j < deleteCommandKey.length; j++) {
                            delete dataBody[i][deleteCommandKey[j]]
                        }

                        //Add command key 
                        if (commandList.length > 0) {
                            dataBody[i].commands = {type: "StructuredValue", value: commandList}
                        }

                        //Verify if all commands of entity have subscription.

                        for(var j = 0; j < commandList.length; j++) {

                            var addCommandResult = addCommandToSubcriptionListAux(service, servicePath, dataBody[i].type, commandList[j])
                        }

                        const dataBodyLD = libfromNGSIv2.fromNGSIv2toNGSILD(dataBody[i],"")

                        const responseSendDataMQTT = await sendDataMQTT(dataBody[i], dataBodyLD, service, servicePath)    

                    } else {

                        //console.log("Command notification - " + req.body.subscriptionId)

                        const dataBodyLD = libfromNGSIv2.fromNGSIv2toNGSILD(dataBody[i],"")
                        
                        var obtainRequest = false

                        //console.log(vSiloCommandRequestHistory)
                        //console.log(dataBodyLD)

                        //vSiloCommandRequestHistory.push([internalidentifier,commandKey,payLoadObject,vThingAux)

                        for(var j = 0; j < vSiloCommandRequestHistory.length; j++) {

                            if (typeof dataBody[i][vSiloCommandRequestHistory[j][1]+"_info"] !== "undefined") {

                                if (vSiloCommandRequestHistory[j][0] ==  dataBody[i][vSiloCommandRequestHistory[j][1]+"_info"].value["cmd-id"]) {

                                    //console.log("vSilo Request FOUND!")

                                    obtainRequest = true
                                
                                    var dataBodyLDmod = {}

                                    var obtainCommand1 = {}

                                    var obtainCommand2 = {}

                                    obtainCommand1 = JSON.parse(JSON.stringify(vSiloCommandRequestHistory[j][2].data[0][vSiloCommandRequestHistory[j][1]].value))

                                    if (typeof obtainCommand1["cmd-qos"] !== "undefined") {

                                        if (parseInt(obtainCommand1["cmd-qos"]) > 0 ) {

                                            obtainCommand1["cmd-result"] = "OK"

                                            obtainCommand2 = JSON.parse(JSON.stringify(vSiloCommandRequestHistory[j][2].data[0][vSiloCommandRequestHistory[j][1]].value))

                                            obtainCommand2["cmd-status"] = "OK"

                                            dataBodyLDmod = {"id": dataBodyLD.id, "type": dataBodyLD.type}

                                            var commandResultKey = vSiloCommandRequestHistory[j][1]+"-result"

                                            var commandStatusKey = vSiloCommandRequestHistory[j][1]+"-status"

                                            var commandResultTimeInstant = {}
                                            var commandStatusTimeInstant = {}

                                            if (typeof dataBodyLD[vSiloCommandRequestHistory[j][1]+"_info"].TimeInstant !== "undefined") {
                                                commandResultTimeInstant = JSON.parse(JSON.stringify(dataBodyLD[vSiloCommandRequestHistory[j][1]+"_info"].TimeInstant))
                                                dataBodyLDmod[commandResultKey] = {"type":"Property","value": obtainCommand1, "TimeInstant": commandResultTimeInstant} 
                                            } else {
                                                dataBodyLDmod[commandResultKey] = {"type":"Property","value": obtainCommand1} 
                                            }

                                            if (typeof dataBodyLD[vSiloCommandRequestHistory[j][1]+"_status"].TimeInstant !== "undefined") {
                                                commandStatusTimeInstant = JSON.parse(JSON.stringify(dataBodyLD[vSiloCommandRequestHistory[j][1]+"_status"].TimeInstant))
                                                dataBodyLDmod[commandStatusKey] = {"type":"Property","value": obtainCommand2, "TimeInstant": commandStatusTimeInstant} 
                                            } else {
                                                dataBodyLDmod[commandStatusKey] = {"type":"Property", "value": obtainCommand2}
                                            }

                                            //Obtaining vSilo topic to response.

                                            const vSiloIDaux = vSiloCommandRequestHistory[j][2].meta.vSiloID
                                            const vThingIDaux = vSiloCommandRequestHistory[j][3]

                                            var listCMDNURI = processCMDNURI(dataBodyLDmod[commandResultKey].value["cmd-nuri"])

                                            if(listCMDNURI.length > 0) {
                                                const responseSendInfoStatusMQTT = await sendCommandInfoStatusMQTT(vSiloIDaux, vThingIDaux, dataBodyLDmod, listCMDNURI)
                                            } else  {
                                                console.log("Send using data_out topic (1).")
                                                const responseSendInfoStatusMQTT_data_out = await sendCommandInfoStatusMQTT_data_out(vThingIDaux, dataBodyLDmod)
                                            }
                                        } 
                                    }
                                    
                                    break;
                                }
                            }
                        }

                        //if(obtainRequest == false) {
                        //    console.log("vSilo Request NOT FOUND.")
                        //}
                        
                    }
                   
                }

            } else {

                for(var i = 0; i < dataBody.length; i++) {
                 
                    const dataBodyLD = obtainNGSILDPayload(service,dataBody[i])

                    if (isEmpty(dataBodyLD) == false){
                        if (isAggregated) {
                            const responseStoreData = await storeData(dataBody[i], dataBodyLD, service, servicePath)
                        } else {
                            const responseSendDataMQTT = await sendDataMQTT(dataBody[i], dataBodyLD, service, servicePath)
                        }
                    }
                }
            }    
        }
        
        res.status(200).send({description: 'Operation has been completed successfully'})
    } catch(e) {
        console.error(e)
        res.status(500).send({ error: e })
    }
})

// Launch service.
app.listen(notificacion_port_container,() => {        

    setTimeout(async function() {
        console.log(util.unixTime(Date.now()) + ` - API running, port: ${notificacion_port_container}`)

        var responseStartThingVisor = await startThingVisor()                                    

    }, 25000); //Wait 25 seconds

})


function processCMDNURI(valueArg) {

    var resultArray = []

    try {
        
        var typeCMDNURI = typeof valueArg

        if (typeCMDNURI !== "undefined") {

            if (typeCMDNURI == "string" && valueArg.startsWith("viriot://") ) {

                resultArray.push(valueArg.substring("viriot://".length))

            } else if (typeCMDNURI == "object") {

                for(var k = 0; k < valueArg.length; k++) {

                    if (typeof valueArg[i] == "string" && valueArg[i].startsWith("viriot://") ) {

                        resultArray.push(valueArg[i].substring("viriot://".length))
                    }
                }
            }
        }

    } catch(e) {
        resultArray = resultArray
    }

    return resultArray
}



function obtainParams(paramsString) {

    var paramsJSON = {}

    try {
        paramsJSON = JSON.parse(paramsString)
    } catch(e) {
        try {
            paramsJSON = JSON.parse(paramsString.replace(/'/g,'"'))
        } catch(e1) {
            paramsJSON = {}
        }
    }

    return paramsJSON
}

async function startThingVisor() {
    try {
        //console.log("startThingVisor")

        var responseInitProces = await initProcess()

        //TODO: process responseInitProces value (true or false) send topic message¿?¿?

        console.log("")
        console.log("******* ThingVisor is completly configured!!! *******")

        return responseInitProces

    } catch(e) {
        console.error("startThingVisor: " + e.toString())
        return false
    }  
}

function addCommandToSubcriptionList(serviceArg, servicePathArg, typeArg, keyArg) {
    try {

        //["service","servicePath", "type", "command", ""subscriptionID"]
        
        if (subscriptionIdOCBCommandAttributeList.length == 0) {
            subscriptionIdOCBCommandAttributeList.push({IdOCB: "", Service: serviceArg, ServicePath: servicePathArg, Type: typeArg, Command: keyArg})
        } else {
            var addCommand = true
            for(var i = 0; i < subscriptionIdOCBCommandAttributeList.length;i++) {
                if ( serviceArg == subscriptionIdOCBCommandAttributeList[i].Service && servicePathArg == subscriptionIdOCBCommandAttributeList[i].ServicePath && 
                    typeArg == subscriptionIdOCBCommandAttributeList[i].Type && keyArg == subscriptionIdOCBCommandAttributeList[i].Command) {
                    addCommand = false
                    break;
                }
            }  
            if (addCommand)  {
               subscriptionIdOCBCommandAttributeList.push({IdOCB: "", Service: serviceArg, ServicePath: servicePathArg, Type: typeArg, Command: keyArg})
            }
        }

        return true

    } catch(e) {
        console.error("addCommandToSubcriptionList: " + e.toString())
        return false
    }

}

function addCommandToSubcriptionListAux(serviceArg, servicePathArg, typeArg, keyArg) {
    try {

        //["service","servicePath", "type", "command", ""subscriptionID"]
        
        if (subscriptionIdOCBCommandAttributeListAux.length == 0) {
            subscriptionIdOCBCommandAttributeListAux.push({Service: serviceArg, ServicePath: servicePathArg, Type: typeArg, Command: keyArg})
        } else {
            var addCommand = true
            for(var i = 0; i < subscriptionIdOCBCommandAttributeListAux.length;i++) {
                if ( serviceArg == subscriptionIdOCBCommandAttributeListAux[i].Service && servicePathArg == subscriptionIdOCBCommandAttributeListAux[i].ServicePath && 
                    typeArg == subscriptionIdOCBCommandAttributeListAux[i].Type && keyArg == subscriptionIdOCBCommandAttributeListAux[i].Command) {
                    addCommand = false
                    break;
                }
            }  
            if (addCommand)  {
               subscriptionIdOCBCommandAttributeListAux.push({Service: serviceArg, ServicePath: servicePathArg, Type: typeArg, Command: keyArg})
            }
        }

        return true

    } catch(e) {
        console.error("addCommandToSubcriptionListAux: " + e.toString())
        return false
    }

}


async function initProcess() {
    try {
        console.log("")
        console.log("******* Start ThingVisor - INIT PROCESS *******")
        
        //STEP 1: Obtain all Orion Context Broker entities, the request are limited by a register fixed number (100). This process store the
        //traceability between NGSI-v2 id and NGSI-LD id.

        var keyVThingID = 0
        var entityGroupCounter = 0

        var numEntities = 0

        for(var h = 0; h < ocb_service.length;h++) {

            for(var k = 0; k < ocb_type[h].length;k++) {
                var obtainMore = true
                var offset = 100
                var actualOffset = 0
                var limit = 100

                while (obtainMore) {

                    var responseCBEntities

                    try {
                        //Obtain actual entities in Context Broker
                        if (isGreedy || isActuator) {
                            responseCBEntities = await orion.obtainALLCBEntities(actualOffset, limit, ocb_ip, ocb_port, ocb_service[h], ocb_servicePath[h])
                        } else {
                            responseCBEntities = await orion.obtainALLCBEntitiesPerType(actualOffset, limit, ocb_ip, ocb_port, ocb_service[h], ocb_servicePath[h], ocb_type[h][k])
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

                            if (isActuator) { 

                                var deleteCommandKey = []
                                var commandList = []

                                for(var key in responseCBEntities[i]) {

                                    if(findArrayElement(["id","type","@context"],key) == false) {

                                        var isCommandAttr = false
                                        if (typeof responseCBEntities[i][key].type !== "undefined") {

                                            if (findArrayElement(["command","commandResult","commandStatus"],responseCBEntities[i][key].type)) {
                                                    isCommandAttr = true
                                                    deleteCommandKey.push(key)
                                            }

                                            if (findArrayElement(["command"],responseCBEntities[i][key].type)) {
                                                commandList.push(key)
                                                var addCommandResult = addCommandToSubcriptionList(ocb_service[h], ocb_servicePath[h], responseCBEntities[i].type, key)
                                            }
                                        }
                                    }
                                }

                                //Delete unshared properties (commands) from payload.
                                for(var j = 0; j < deleteCommandKey.length; j++) {
                                    delete responseCBEntities[i][deleteCommandKey[j]]
                                }

                                //Add command key 
                                if (commandList.length > 0) {
                                    responseCBEntities[i].commands = {type: "StructuredValue", value: commandList}
                                }

                            }

                            var valuevThingLocalID

                            // DEPRECATED isGroupingByType
                            //if (isGroupingByType) {
                            ////Find if entity service/servicepath/type is in the array to obtain the corresponding keyVThingID value.
                            var element = ocb_service[h] + "_" + ocb_servicePath[h] + "_" + responseCBEntities[i].type
                            var valueIndex = obtainArrayIndex(typeServiceList,element)

                            if (valueIndex!=-1) { //Found.
                                keyVThingID = valueIndex
                            } else { //Not Found.
                                typeServiceList.push(element)
                                keyVThingID = obtainArrayIndex(typeServiceList,element)
                            }
                            // DEPRECATED isGroupingByType
                            //} else {
                            //    if (entitiesPerVThingID != 0 && entityGroupCounter >= entitiesPerVThingID && isGreedy) {
                            //        //New vThingID
                            //        entityGroupCounter = 0
                            //        keyVThingID = keyVThingID + 1
                            //    }
                            //}

                            valuevThingLocalID = keyVThingID //+ "-" + entityGroupCounter

                            var dataBodyLD

                            if (isGreedy) {

                                dataBodyLD = libfromNGSIv2.fromNGSIv2toNGSILD(responseCBEntities[i],"")

                                if (isEmpty(dataBodyLD) == false) {
                                    vThingList.push({
                                        rThingID: responseCBEntities[i].id, //Used by "orionSubscription" function.
                                        rThingType: responseCBEntities[i].type, //Used by "orionSubscription" function.
                                        rThingService: ocb_service[h], //Used by "orionSubscription" function.
                                        rThingServicePath: ocb_servicePath[h], //Used by "orionSubscription" function.
                                        vThingLD: libWrapperUtils.format_uri(responseCBEntities[i].type,responseCBEntities[i].id),
                                        vThingLocalID: valuevThingLocalID,
                                        vThingID: thingVisorID + "/" + valuevThingLocalID,
                                        data: dataBodyLD //Establishing data_context 
                                    })
                                }

                            } else if (isActuator) {

                                dataBodyLD = libfromNGSIv2.fromNGSIv2toNGSILD(responseCBEntities[i],"")

                                valuevThingLocalID = responseCBEntities[i].type + valuevThingLocalID

                                if (isEmpty(dataBodyLD) == false) {
                                    vThingList.push({
                                        rThingID: responseCBEntities[i].id, //Used by "orionSubscription" function.
                                        rThingType: responseCBEntities[i].type, //Used by "orionSubscription" function.
                                        rThingService: ocb_service[h], //Used by "orionSubscription" function.
                                        rThingServicePath: ocb_servicePath[h], //Used by "orionSubscription" function.
                                        vThingLD: libWrapperUtils.format_uri(responseCBEntities[i].type,responseCBEntities[i].id),
                                        vThingLocalID: valuevThingLocalID,
                                        vThingID: thingVisorID + "/" + valuevThingLocalID,
                                        data: dataBodyLD //Establishing data_context 
                                    })
                                }

                            } else {
                                //NGSI-LD type entity, changing to calculate vThingLD and data
                                if(isAggregated){
                                    valuevThingLocalID = vThingLocalIDAggregated
                                } else {
                                    valuevThingLocalID = dest_ocb_type[h][k]
                                }
                                
                                if(isAggregated){
                                    dataBodyLD = libfromNGSIv2.fromNGSIv2toNGSILD(responseCBEntities[i],"")
                                } else {
                                    //Create valid payload before notification
                                    dataBodyLD = obtainNGSILDPayload(ocb_service[h],responseCBEntities[i])
                                }

                                if (isEmpty(dataBodyLD) == false) {
                                    vThingList.push({
                                        rThingID: responseCBEntities[i].id,
                                        rThingType: responseCBEntities[i].type,   //Real type entity
                                        rThingService: ocb_service[h], //Used by "orionSubscription" function.
                                        rThingServicePath: ocb_servicePath[h], //Used by "orionSubscription" function.
                                        vThingLD: libWrapperUtils.format_uri(dest_ocb_type[h][k],responseCBEntities[i].id),
                                        vThingLocalID: valuevThingLocalID,
                                        vThingID: thingVisorID + "/" + valuevThingLocalID,
                                        data: dataBodyLD  //Establishing data_context 
                                    })
                                }
                            }

                            if (isEmpty(dataBodyLD) == false) {
                                numEntities = numEntities + 1

                                //if (entitiesPerVThingID != 0 && isGreedy) {
                                entityGroupCounter = entityGroupCounter + 1
                                //}
                            }

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
            }
        }

        console.log("Orion Context Broker entities number: " + numEntities)

        //console.log("vThing List after init process: ")
        //console.log(vThingList)

        if (isActuator) {
            console.log("broker Command Attribute List: " )
            console.log(subscriptionIdOCBCommandAttributeList)
        }

        //STEP 2: Establishing topic's subscriptions using vThingID of vThingList array.
        //STEP 3: Subscribe to Orion Context Broker.
        //STEP 4: Send createVThings topic message to Master-Controller.
        const responseInitProcessAux = await initProcessAux()

        //TODO: process responseInitProcessAux value (true or false) send topic message¿?¿?

        return true

    } catch(e) {
        console.error("initProcess: " + e.toString())
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
            if (findArrayElement(mqttSubscriptionListControl,topicElement) == false && findArrayElement(topicArray,topicElement) == false ) {
                topicArray.push(topicElement)
       
                counter = counter + 1    
            }

            if (counter>=10 || i == vThingList.length-1 ) {
                        
                if (subscribeMQTT(topicArray,'0',thingVisorID,"control") == false) {
                    console.error("Error - connecting MQTT-server: Can't subscribe topics.")
                    return false
                } else {

                    //Push into mqttSubscriptionListControl array new topic subscriptions array
                    mqttSubscriptionListControl = mqttSubscriptionListControl.concat(topicArray)
                }
       
                counter = 0
                topicArray = []
            }
        }


        counter = 0
        topicArray = []
                       
        for(var i = 0; i < vThingList.length;i++) {
            //"/vThing/vThingID/data_in" topic

            const topicElement = MQTTbrokerApiKeyvThing + "/" + vThingList[i].vThingID + "/" + MQTTbrokerTopicDataIn
            //topicArray.push(MQTTbrokerApiKeyvThing + "/" + vThingList[i].vThingID + "/" + MQTTbrokerTopicDataIn)

            //To avoid two equals subscriptions.
            if (findArrayElement(mqttSubscriptionListData,topicElement) == false && findArrayElement(topicArray,topicElement) == false ) {
                topicArray.push(topicElement)
       
                counter = counter + 1    
            }

            if (counter>=10 || i == vThingList.length-1 ) {
                        
                if (subscribeMQTT(topicArray,'0',thingVisorID,"data") == false) {
                    console.error("Error - connecting MQTT-server: Can't subscribe topics.")
                    return false
                } else {

                    //Push into mqttSubscriptionListData array new topic subscriptions array
                    mqttSubscriptionListData = mqttSubscriptionListData.concat(topicArray)
                }
       
                counter = 0
                topicArray = []
            }
        }

        console.log("")

        console.log("MQTT Data Subscription Topic List: ")
        console.log(mqttSubscriptionListData)
        console.log("MQTT Control Subscription Topic List: ")
        console.log(mqttSubscriptionListControl)
              
        //STEP 3: Subscribe to Orion Context Broker.
        var responseOrionSubscription

        // DEPRECATED isGroupingByType
        //if (isGroupingByType) {
        responseOrionSubscription = await orionSubscriptionByType()        
        
        if (isActuator) {
            responseOrionSubscription = await orionSubscriptionByTypeCommands()
        }
        
        // DEPRECATED isGroupingByType            
        //} else {
        //    responseOrionSubscription = await orionSubscription()    
        //}
      
        //TODO: process responseOrionSubscription value (true or false) send topic message¿?¿?

        //console.log("ThingVisor subscribed to all Orion Context Broker entities.")

        //STEP 4: Send createVThings topic message to Master-Controller.
        var responseSendCreateVThingMessages
        responseSendCreateVThingMessages = await sendCreateVThingMessages()
               
        //TODO: process responseSendCreateVThingMessages value (true or false) send topic message¿?¿?

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

        var testObservedAt = false

        var date = new Date();

        dateObserved = util.ISODateString(date)

        for(var i = 0; i < vThingList.length;i++) {

            if (vThingIDValue == "") {
                vThingIDValue = vThingList[i].vThingID
            }

            if (typeof vThingList[i].data.freeParkingSpaces.value !== 'undefined') {
                totalFreeParkingSpaces = totalFreeParkingSpaces + parseInt(vThingList[i].data.freeParkingSpaces.value)
            }

            try {
                if (typeof vThingList[i].data.observedAt.value['@value'] !== 'undefined' &&
                    vThingList[i].data.observedAt.value['@value'] > maxObservedAt){
                    testObservedAt = true
                    maxObservedAt = vThingList[i].data.observedAt.value['@value']
                }
            } catch(e) {
                maxObservedAt = maxObservedAt
            }
        }

        if (maxObservedAt == "") {
            maxObservedAt = dateObserved
        }

        if (vThingListAggValueContext.length == 0) {
            vThingListAggValueContext.push(
                {
                    vThingID: thingVisorID + "/" + vThingLocalIDAggregated,
                    data: {   
                            type: 'parkingsite',
                            totalFreeParkingSpaces: { type: 'Property', value: totalFreeParkingSpaces },
                            '@context': 
                                [ 'https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld',
                                  'https://odins.es/smartParkingOntology/parkingsite-context.jsonld' ],
                            observedAt: 
                                { type: 'Property',
                                value: { '@type': 'DateTime', '@value': maxObservedAt } },
                            id: 'urn:ngsi-ld:parkingsite:vThingParkingSite' 
                        }
                }
            )
        } else {
            vThingListAggValueContext[0].data.totalFreeParkingSpaces.value = totalFreeParkingSpaces
            vThingListAggValueContext[0].data.observedAt.value['@value'] = maxObservedAt

        }
       
        //It sent to MQTT data broker when change.
        if (globalTotalFreeParkingSpaces != totalFreeParkingSpaces || (globalMaxObservedAt != maxObservedAt && testObservedAt)) {

            globalTotalFreeParkingSpaces = totalFreeParkingSpaces 
            globalMaxObservedAt = maxObservedAt

            if (vThingIDValue != "") {

                const topic = MQTTbrokerApiKeyvThing + "/" + vThingIDValue + "/" + MQTTbrokerTopicDataOut;
                    
                const topicMessage = {"data": [vThingListAggValueContext[0].data], "meta": {"vThingID": vThingIDValue}}

                console.log("Sending message... " + topic + " " + JSON.stringify(topicMessage));

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

        if (isGreedy || isActuator || isAggregated == false) {
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

        //clientMosquittoMqttControl.end()
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

/* DEPRECATED isGroupingByType
//Create Orion Context Broker subscriptions.
async function orionSubscription() {
    try {
        
        console.log("orionSubscription")
        var vThingListCopy

        vThingListCopy = vThingList

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
                    responseCBSubscriptions = await orion.obtainCBSubscriptions(actualOffset, limit, ocb_ip, ocb_port, ocb_service[h], ocb_servicePath[h])
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
                                    ocb_servicePath[h]==vThingListCopy[k].rThingServicePath && 
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
        
                if (vThingListCopy[i].rThingServicePath.length != 0) {
                    headersPost["fiware-servicepath"] = vThingListCopy[i].rThingServicePath;
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
                                subscriptionIdOCBList[k].Service == vThingListCopy[i].rThingService &&
                                subscriptionIdOCBList[k].ServicePath == vThingListCopy[i].rThingServicePath) {
                                foundID = true
                                break;
                            }
                        }

                        if (foundID == false) {
                            //console.log("registra subscriptionIdOCBList: " + JSON.stringify({IdOCB: subscriptionIdOCB, Service: vThingListCopy[i].rThingService}))
                            subscriptionIdOCBList.push({IdOCB: subscriptionIdOCB, Service: vThingListCopy[i].rThingService, ServicePath: vThingListCopy[i].rThingServicePath})
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
*/

//Create Orion Context Broker subscriptions.
async function orionSubscriptionByType() {
    try {

        //console.log("orionSubscriptionByType")
        var vThingListCopy

        vThingListCopy = vThingList

        var arrayTextServiceTypes = []
        var arrayObjectServiceTypes = []
        //Obtain all service/type pairs from real entities.
        for(var h = 0; h < vThingListCopy.length;h++) {

            var element = vThingListCopy[h].rThingService + "_" + vThingListCopy[h].rThingServicePath + "_" + vThingListCopy[h].rThingType

            if (obtainArrayIndex(arrayTextServiceTypes,element) == -1) {
                arrayTextServiceTypes.push(element)    
                arrayObjectServiceTypes.push({
                    rThingType: vThingListCopy[h].rThingType,
                    rThingService: vThingListCopy[h].rThingService,
                    rThingServicePath: vThingListCopy[h].rThingServicePath
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
                    responseCBSubscriptions = await orion.obtainCBSubscriptions(actualOffset, limit, ocb_ip, ocb_port, ocb_service[h], ocb_servicePath[h])
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

                        if (responseCBSubscriptions[i].notification.http.url==urlNotify && responseCBSubscriptions[i].description.startsWith("TV:")) {
                            
                            //Find in the arrayServiceTypes array an element with the same service and type 
                            //as the subscriptions ones.
                            //ocb_service[h]
                            //responseCBSubscriptions.subject.entities[0].type
                            //responseCBSubscriptions.subject.entities[0].id

                            var element = ocb_service[h] + "_" + ocb_servicePath[h] + "_" + responseCBSubscriptions[i].subject.entities[0].type

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
        
                if (arrayObjectServiceTypes[i].rThingServicePath.length != 0) {
                    headersPost["fiware-servicepath"] = arrayObjectServiceTypes[i].rThingServicePath;
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
                                subscriptionIdOCBList[k].ServicePath == arrayObjectServiceTypes[i].rThingServicePath &&
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
                                                        ServicePath: arrayObjectServiceTypes[i].rThingServicePath,
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
        console.error("orionSubscriptionByType: " + e.toString())
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

                urlNotify = notificacion_protocol + '://' + notify_ip + ':' + mapped_port + notify_service

                //console.log("urlNotify: " + urlNotify)

                while (obtainMore) {

                    var responseCBSubscriptions

                    try {
                        //Obtain actual subscriptions in Context Broker
                        responseCBSubscriptions = await orion.obtainCBSubscriptions(actualOffset, limit, ocb_ip, ocb_port, 
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
                            //Compare notification URL subscription and urlNotify variable value.

                            if (responseCBSubscriptions[i].notification.http.url == urlNotify && 
                                    responseCBSubscriptions[i].description.startsWith("actuatorTV:"+ subscriptionIdOCBCommandAttributeList[h].Command +":") &&
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
                    subscriptionOCB.description = "actuatorTV:" + subscriptionIdOCBCommandAttributeList[h].Command + ": " + thingVisorID + " subscription."
                    subscriptionOCB.subject = {
                                                entities: [
                                                            {
                                                                idPattern: ".*", 
                                                                type: subscriptionIdOCBCommandAttributeList[h].Type
                                                            }
                                                ],
                                                condition: {
                                                    attrs: [ 
                                                                subscriptionIdOCBCommandAttributeList[h].Command+"_info"
                                                                //,subscriptionIdOCBCommandAttributeList[h].Command+"_status"
                                                    ]
                                                }
                                            };  
                    subscriptionOCB.notification = {}
                    subscriptionOCB.notification.http = {url: urlNotify}
                    subscriptionOCB.notification.attrs = [ 
                                                            subscriptionIdOCBCommandAttributeList[h].Command+"_info"
                                                            ,subscriptionIdOCBCommandAttributeList[h].Command+"_status"
                                                        ]
                    //Preparing subscription request.
                    const instance = axios.create({
                        baseURL: 'http://' + ocb_ip + ':' + ocb_port
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

                if (isGreedy || isActuator) {
                    // DEPRECATED isGroupingByType
                    //if (isGroupingByType) {
                    body = {"command": commandCreateVThing, "thingVisorID": thingVisorID, 
                        "vThing": {label: "Type:" + vThingList[i].rThingType + " # Service:" + vThingList[i].rThingService + " # ServicePath:" + vThingList[i].rThingServicePath, 
                                id: vThingList[i].vThingID, 
                                description: ""}}
                    // DEPRECATED isGroupingByType                                
                    //} else if (entitiesPerVThingID == 1) {
                    //    body = {"command": commandCreateVThing, "thingVisorID": thingVisorID, 
                    //    "vThing": {label: "id:" + vThingList[i].rThingID + " # Type:" + vThingList[i].rThingType + " # Service:" + vThingList[i].rThingService + " # ServicePath:" + vThingList[i].rThingServicePath, 
                    //            id: vThingList[i].vThingID, 
                    //            description: ""}}
                    //} else {
                    //    body = {"command": commandCreateVThing, "thingVisorID": thingVisorID, 
                    //    "vThing": {label: "Service:" + vThingList[i].rThingService + " # ServicePath:" + vThingList[i].rThingServicePath, 
                    //            id: vThingList[i].vThingID, 
                    //            description: ""}}
                    //}
                } else {
                    body = {"command": commandCreateVThing, "thingVisorID": thingVisorID, 
                        "vThing": {label: "Service:" + vThingList[i].rThingService + " # ServicePath:" + vThingList[i].rThingServicePath, 
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



async function sendDataMQTT(dataBody, dataBodyLD, service, servicePath) {
    try {
        //Obtain vThingID
        //Find in the vThingList array an element with the same type and id as notification entity ones.
        //dataBody.type
        //dataBody.id

        var vThingIDValue = await storeData(dataBody, dataBodyLD, service, servicePath)

        //If we find it
        if (vThingIDValue!="") {

            const topic = MQTTbrokerApiKeyvThing + "/" + vThingIDValue + "/" + MQTTbrokerTopicDataOut;
                
            const topicMessage = {"data": [dataBodyLD], "meta": {"vThingID": vThingIDValue}}

            console.log("Sending message... " + topic + " " + JSON.stringify(topicMessage));

            await clientMosquittoMqttData.publish(topic, JSON.stringify(topicMessage), {qos: 0}, function (err) {
                if (!err) {
                    //console.log("Message has been sent correctly.")
                } else {
                    console.error("ERROR: Sending MQTT message (publish): ",err)
                }
            })
                    
        } else {
            //TODO: Handle error situation.
        }

        return true

    } catch(e) {
        console.error("sendDataMQTT: " + e.toString())
        return false
    }  
}

async function sendCommandInfoStatusMQTT(vSiloID, vThingID, dataBodyLD, cmdnuriArg) {
    try {

        //"/vSilo/<ID>/data_in" topic
        const topic = MQTTbrokerApiKeySilo + "/" + vSiloID + "/" + MQTTbrokerTopicDataIn;
                
        const topicMessage = {"data": [dataBodyLD], "meta": {"vThingID": vThingID}}

        console.log("Sending message... " + topic + " " + JSON.stringify(topicMessage));

        await clientMosquittoMqttData.publish(topic, JSON.stringify(topicMessage), {qos: 0}, function (err) {
            if (!err) {
                //console.log("Message has been sent correctly.")
            } else {
                console.error("ERROR: Sending MQTT message (publish): ",err)
            }
        })
                    
        for(var k = 0; k < cmdnuriArg.length;k++) {
            if (cmdnuriArg[k] != topic) {
                console.log("Sending message... " + cmdnuriArg[k] + " " + JSON.stringify(topicMessage));

                await clientMosquittoMqttData.publish(cmdnuriArg[k], JSON.stringify(topicMessage), {qos: 0}, function (err) {
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
        console.error("sendCommandInfoStatusMQTT: " + e.toString())
        return false
    }  
}

async function sendCommandInfoStatusMQTT_data_out(vThingIDArg, dataBodyLD) {
    try {
        const topic = MQTTbrokerApiKeyvThing + "/" + vThingIDArg + "/" + MQTTbrokerTopicDataOut;
                
        const topicMessage = {"data": [dataBodyLD], "meta": {"vThingID": vThingIDArg}}

        console.log("Sending message... " + topic + " " + JSON.stringify(topicMessage));

        await clientMosquittoMqttData.publish(topic, JSON.stringify(topicMessage), {qos: 0}, function (err) {
            if (!err) {
                //console.log("Message has been sent correctly.")
            } else {
                console.error("ERROR: Sending MQTT message (publish): ",err)
            }
        })
                    
        return true

    } catch(e) {
        console.error("sendCommandInfoStatusMQTT_data_out: " + e.toString())
        return false
    }  
}



async function storeData(dataBody, dataBodyLD, service, servicePath) {
    try {
        //Obtain vThingID
        //Find in the vThingList array an element with the same type and id as notification entity ones.
        //dataBody.type
        //dataBody.id

        var vThingIDValue = ""

        for(var k = 0; k < vThingList.length;k++) {
            if (service==vThingList[k].rThingService && servicePath==vThingList[k].rThingServicePath &&
                dataBody.type==vThingList[k].rThingType && dataBody.id==vThingList[k].rThingID) {
                    
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

        //Define baseURL --> URL of OCB source.
        const instance = axios.create({
                baseURL: 'http://' + ocb_ip + ':' + ocb_port
        })

        for(var i = 0; i < subscriptionCBArray.length;i++) {

            if (subscriptionCBArray[i].IdOCB != "") {

                var headersDelete = {}
                headersDelete["Accept"] = 'application/json';

                if (subscriptionCBArray[i].Service.length != 0) {
                    headersDelete["fiware-service"] = subscriptionCBArray[i].Service;
                }

                if (subscriptionCBArray[i].ServicePath.length != 0) {
                    headersDelete["fiware-servicepath"] = subscriptionCBArray[i].ServicePath;
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

async function shutdown(param) {

    try {

        //STEP 1: The TV unsubscribes from all active subscription.
        var responseOrionUnsubscription

        console.log('Orion Context Broker subscriptions deleting...');

        //Subscribe to Orion Context Broker.

        if (isActuator) {
            responseOrionUnsubscription = await orionUnsubscription(subscriptionIdOCBCommandAttributeList)

            if (responseOrionUnsubscription) {
                subscriptionIdOCBCommandAttributeList = []
            }

        }
            
        responseOrionUnsubscription = await orionUnsubscription(subscriptionIdOCBList)

        if (responseOrionUnsubscription) {
            subscriptionIdOCBList = []
        }
        

        //TODO: process responseOrionUnsubscription value (true or false) send topic message¿?¿?

        console.log('All Orion Context Broker subscriptions deleted.');
        console.log('MQTT Subscriptions deleting...');

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
            vThingList = []
            vThingListAggValueContext = []
        }

        //TODO: process response_sendDeleteMessages value (true or false) send topic message¿?¿?
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

// To capture signals.
const capt_signals = ['SIGHUP', 'SIGINT', 'SIGTERM'];

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

// PERIODIC PROCESS
setInterval(async  function() {
    try {
        if (isAggregated) {
            sendDataMQTT_AggregatedValue()
        } else if (isActuator) {

            for(var i = 0; i < subscriptionIdOCBCommandAttributeListAux.length;i++) {
                var addCommandResult = addCommandToSubcriptionList(
                        subscriptionIdOCBCommandAttributeListAux[i].Service,
                        subscriptionIdOCBCommandAttributeListAux[i].ServicePath,
                        subscriptionIdOCBCommandAttributeListAux[i].Type,
                        subscriptionIdOCBCommandAttributeListAux[i].Command
                        )

            }

            var responseOrionSubscription = await orionSubscriptionByTypeCommands()
        }
    } catch(e) {
        var a
    }
}, config.frecuency_mseg);  
