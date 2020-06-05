/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

'use strict'

const config = require('./config')

var util = require("./util")

var mqtt = require('mqtt')



var MQTTBrokerHost
var MQTTBrokerPort

var commandStart
var commandStop
var commandReset
var commandIncreasing
var commanSetCounter

var MQTTbrokerApiKey
    
var MQTTbrokerTopicCmd
var MQTTbrokerTopicCmdExe
var MQTTbrokerTopicAttrs

var device001
var frecuency_mseg_device001
var isOpen_device001

var device002
var frecuency_mseg_device002
var count_device002
var isIncreasing_device002
var isRunning_device002

var device003
var frecuency_mseg_device003
var count_device003
var isIncreasing_device003
var isRunning_device003

var optionsMQTT

var mqttSubscriptionList

var clientMosquittoMqtt

console.log("")
console.log("")
console.log("**********" + util.unixTime(Date.now()) + " ***************")


try {

    MQTTBrokerHost = config.MQTTBrokerHost
    MQTTBrokerPort = config.MQTTBrokerPort

    commandStart = config.commandStart
    commandStop = config.commandStop
    commandReset = config.commandReset
    commandIncreasing = config.commandIncreasing
    commanSetCounter = config.commanSetCounter

    MQTTbrokerApiKey = config.MQTTbrokerApiKey
    
    MQTTbrokerTopicCmd = config.MQTTbrokerTopicCmd
    MQTTbrokerTopicCmdExe = config.MQTTbrokerTopicCmdExe
    MQTTbrokerTopicAttrs = config.MQTTbrokerTopicAttrs

    device001 = "device001"
    frecuency_mseg_device001 = config.frecuency_mseg_device001
    isOpen_device001 = false

    device002 = "device002"
    frecuency_mseg_device002 = config.frecuency_mseg_device002
    count_device002 = 250
    isIncreasing_device002 = false
    isRunning_device002 = true

    device003 = "device003"
    frecuency_mseg_device003 = config.frecuency_mseg_device003
    count_device003 = 11
    isIncreasing_device003 = false
    isRunning_device003 = false

    //Options MQTT connection
    optionsMQTT = {
            clean: false,
            clientId: 'mqttjs_' + Math.random().toString(16).substr(2, 8)
    };

    mqttSubscriptionList = []

} catch(e) {
    console.error("Processing configuration - Error: " + e.toString())
    return
}


//setTimeout(async function() {
    //Connecting to MQTT-server...
    try {

        clientMosquittoMqtt = mqtt.connect("mqtt://" + MQTTBrokerHost + ":" + MQTTBrokerPort,optionsMQTT);

    } catch(e) {
        console.error("Error - connecting MQTT-server...: " + e.toString())
        return 
    }

    //Mapping connect function
    clientMosquittoMqtt.on("connect", function() {
        try {

            console.log("")
            console.log(util.unixTime(Date.now()) + " - MQTT connected")
            //Establishing topic's subscriptions
            mqttSubscriptionList = [
                                MQTTbrokerApiKey + "/" + device001 + "/" + MQTTbrokerTopicCmd,
                                MQTTbrokerApiKey + "/" + device002 + "/" + MQTTbrokerTopicCmd,
                                MQTTbrokerApiKey + "/" + device003 + "/" + MQTTbrokerTopicCmd
            ]

            if (subscribeMQTT(mqttSubscriptionList) == false) {
                console.error("Error - connecting MQTT-server: Can't subscribe topics.")
                return
            }

            console.log("")
            console.log("MQTT Subscription Topic List: ")
            console.log(mqttSubscriptionList)
                
            return
        } catch(e) {
          //log.error(error.toString());
          console.error(e.toString());
          return;
        }
    })

    //Mapping error function
    clientMosquittoMqtt.on("error", function(error) {
        try {
            clientMosquittoMqtt.reconnect()
            return;
        } catch(e) {
          console.error(e.toString());
          return;
        }
    })

    //Mapping reconnect function
    clientMosquittoMqtt.on("reconnect", function(a) {
        try {
            console.log(util.unixTime(Date.now()) + " - Reconnecting clientMosquittoMqtt...")
            return;
        } catch(e) {
          console.error(e.toString());
          return;
        }
    })

    //Mapping topic's subscriptions function
    clientMosquittoMqtt.on("message", async function(topic, payload) {
        
        try {
            console.log("");
            console.log(util.unixTime(Date.now()) + " - Received topic: " + topic + " ; payload: " + payload.toString());
            
            var indexIni = (MQTTbrokerApiKey+"/").length

            var initialElement = topic.substring(0, (MQTTbrokerApiKey+"/").length)

            //Processing topic's message
            var topicAux = topic.substring(indexIni, topic.length)

            var topicLevelLength = topicAux.split("/").length
            var topicLevelElement = []

            var centralElement = ""

            var responseSendMQTT

            for(var k = 0; k < topicLevelLength-1;k++) {

                if (centralElement.length==0) {
                    centralElement = topicAux.split("/")[k]    
                } else {
                    centralElement = centralElement + "/" + topicAux.split("/")[k]    
                }
            }

            var finalElement = topicAux.split("/")[topicLevelLength-1]

            if (initialElement == MQTTbrokerApiKey+"/" && findArrayElement([device001,device002,device003],centralElement) && finalElement==MQTTbrokerTopicCmd) {
                //Handling "fed4iot/deviceID/cmd" message
                const payLoadObject = JSON.parse(payload.toString().replace(/'/g, '"'));
                //}

                if (typeof payLoadObject[commandStart] !== "undefined") {

                    if(centralElement == device001) {

                        isOpen_device001 = true

                    } else if (centralElement == device002) {

                        isRunning_device002 = true

                    } else {

                        isRunning_device003 = true
                    }

                    responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, centralElement, MQTTbrokerTopicAttrs, {"s": "true"})

                    responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, centralElement, MQTTbrokerTopicCmdExe, payLoadObject)

                } else if (typeof payLoadObject[commandStop] !== "undefined") {

                    if(centralElement == device001) {

                        isOpen_device001 = false

                    } else if (centralElement == device002) {

                        isRunning_device002 = false

                    } else {

                        isRunning_device003 = false
                    }

                    responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, centralElement, MQTTbrokerTopicAttrs, {"s": "false"})

                    responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, centralElement, MQTTbrokerTopicCmdExe, payLoadObject)

                } else if (typeof payLoadObject[commandReset] !== "undefined" && findArrayElement([device002,device003],centralElement)) {

                    if (centralElement == device002) {

                        count_device002 = 0

                    } else {

                        count_device003 = 0
                    }

                    responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, centralElement, MQTTbrokerTopicAttrs, {"c": "0"})

                    responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, centralElement, MQTTbrokerTopicCmdExe, payLoadObject)

                } else if (typeof payLoadObject[commandIncreasing] !== "undefined" && findArrayElement([device002,device003],centralElement)) {

                    if (centralElement == device002) {

                        isIncreasing_device002 = payLoadObject[commandIncreasing].value

                    } else {

                        isIncreasing_device003 = payLoadObject[commandIncreasing].value
                    }

                    responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, centralElement, MQTTbrokerTopicAttrs, {"m": payLoadObject[commandIncreasing].value.toString()})

                    responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, centralElement, MQTTbrokerTopicCmdExe, payLoadObject)

                } else if (typeof payLoadObject[commanSetCounter] !== "undefined"&& findArrayElement([device003],centralElement)) {

                    count_device003 = payLoadObject[commanSetCounter].value

                    responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, centralElement, MQTTbrokerTopicAttrs, {"c": payLoadObject[commanSetCounter].value.toString()})
                    
                    responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, centralElement, MQTTbrokerTopicCmdExe, payLoadObject)

                } else {
                    console.error("invalid command (" + payLoadObject + ") in topic '" + topic + "'");                      
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
    
//}, 15000); //Wait 15 seconds

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


// PERIODIC PROCESS - device001 (attrs)
setInterval(async  function() {

    const dataBody = {"s": isOpen_device001}

    const responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, device001, MQTTbrokerTopicAttrs, dataBody)

}, config.frecuency_mseg_device001);  

// PERIODIC PROCESS - device002 (attrs)
setInterval(async  function() {

    if(isRunning_device002){
        if(isIncreasing_device002){
            count_device002 = count_device002 + 1
        } else {
            count_device002 = count_device002 - 1
        }
    }

    const dataBody = {"c": count_device002, "m": isIncreasing_device002, "s": isRunning_device002}
    
    const responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, device002, MQTTbrokerTopicAttrs, dataBody)

}, config.frecuency_mseg_device002);  

// PERIODIC PROCESS - device003 (attrs)
setInterval(async  function() {

    if(isRunning_device003){
        if(isIncreasing_device003){
            count_device003 = count_device003 + 1
        } else {
            count_device003 = count_device003 - 1
        }
    }

    const dataBody = {"c": count_device003, "m": isIncreasing_device003, "s": isRunning_device003}

    const responseSendMQTT = await sendMQTT(MQTTbrokerApiKey, device003, MQTTbrokerTopicAttrs, dataBody)

}, config.frecuency_mseg_device003);  



//Create mqtt subscriptions.
async function subscribeMQTT(topicArray) {
    try {
                     
        //console.log("Subscribe topics: ")
        //console.log(topicArray)
        await clientMosquittoMqtt.subscribe(topicArray, {qos: 0}, function (err, granted) {
            if (!err) {
                //console.log(granted)
                //console.log(granted)
            } else {
                console.error("Error topic's subscription ")
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
        await clientMosquittoMqtt.unsubscribe(topicArray, function (err) {

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

async function sendMQTT(apiKey, device, topicSufix, dataBody) {
    try {
        
        const topic = apiKey + "/" + device + "/" + topicSufix;
                
        console.log("Sending message... " + topic + " " + JSON.stringify(dataBody));

        await clientMosquittoMqtt.publish(topic, JSON.stringify(dataBody), {qos: 0}, function (err) {
            if (!err) {
                //console.log("Message has been sent correctly.")
            } else {
                console.error("ERROR: Sending MQTT message (publish): ",err)
            }
        })
                    
        return true

    } catch(e) {
        console.error("sendMQTT: " + e.toString())
        return false
    }  
}

async function shutdown(param) {

    try {

        console.log('MQTT Subscriptions deleting...');

        const response_unsubscribeMQTT = await unsubscribeMQTT(mqttSubscriptionList)

        if (response_unsubscribeMQTT) {
            //Emptly mqttSubscriptionList
            mqttSubscriptionList = []
        }

        //TODO: process response_unsubscribeMQTT value (true or false) send topic message¿?¿?
        console.log('MQTT Subscriptionsd deleted.');

        clientMosquittoMqtt.end()
        //console.log('MQTT disconnected.');

        console.log('Components stopped, exiting now');
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

