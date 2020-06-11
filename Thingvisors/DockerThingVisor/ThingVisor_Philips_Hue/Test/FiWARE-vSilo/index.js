/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

'use strict'

const app = require('./app')

const axios = require('axios');

const config = require('./config')

var util = require("./util")

var tenantID

var vSiloProtocol
var vSiloHost
var vSiloPort

var actuatorLight1
var frecuency_mseg_Light1

var actuatorLight2
var initialValueColorLight2
var increasingStepColorLight2
var frecuency_mseg_Light2

var actuatorLight3
var frecuency_mseg_Light3

var nextValueCommand_Ligth1
var nextValueCommand_Light2
var nextValueCommand_Light3

var vSiloUrlCB

console.log("")
console.log("")
console.log("**********" + util.unixTime(Date.now()) + " ***************")

//Processing environment variables...
try {

    tenantID = config.tenantID

    vSiloProtocol = config.vSiloProtocol
    vSiloHost = config.vSiloHost
    vSiloPort = config.vSiloPort
    
    actuatorLight1 = true
    if (config.actuatorLight1 == 0) {
        actuatorLight1 = false
    }
    frecuency_mseg_Light1 = config.frecuency_mseg_Light1

    actuatorLight2 = true
    if (config.actuatorLight2 == 0) {
        actuatorLight2 = false
    }
    initialValueColorLight2 = parseInt(config.initialValueColorLight2)
    increasingStepColorLight2 = parseInt(config.increasingStepColorLight2)
    frecuency_mseg_Light2 = config.frecuency_mseg_Light2

    actuatorLight3 = true
    if (config.actuatorLight3 == 0) {
        actuatorLight3 = false
    }
    frecuency_mseg_Light3 = config.frecuency_mseg_Light3

    nextValueCommand_Ligth1 = "False"
    nextValueCommand_Light2 = initialValueColorLight2
    nextValueCommand_Light3 = "False"

    vSiloUrlCB = vSiloProtocol + '://' + vSiloHost + ':' + vSiloPort

    if (vSiloProtocol == '' || typeof vSiloProtocol === 'undefined') {
        console.error("Error - processing environment variables: 'vSiloProtocol' param not found.")
        return
    }

    if (vSiloHost == '' || typeof vSiloHost === 'undefined') {
        console.error("Error - processing environment variables: 'vSiloHost' param not found.")
        return
    }

    if (vSiloPort == '' || typeof vSiloPort === 'undefined') {
        console.error("Error - processing environment variables: 'vSiloPort' param not found.")
        return
    }

} catch(e) {
    console.error("Error - processing environment variables: " + e)
    return
}

//Create/Update Orion Context Broker entity.
//async function appendCBEntity (service,servicePath,subscriptionIdOCB) {
async function appendCBEntity(payLoadObject,urlCB) {
    try {
        const instance = axios.create({
            baseURL: urlCB
        })

        //Defining headers.
        var headersPost = {}

        headersPost["Content-Type"] = 'application/json';

        const options = {
            headers: headersPost
        }
        
        //Definimos el body de la actualización.
        var entities = []
        entities.push(payLoadObject)

        var updatebody = {
            actionType: "APPEND",
            entities
            }

        try {
            const responsePost = await instance.post(`/v2/op/update`, updatebody, options)

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

// PERIODIC PROCESS - Light1
setInterval(async  function() {

    if (actuatorLight1) {
        var payLoadObject 

        console.log(util.unixTime(Date.now()) + " - Light1 - set-on: " + nextValueCommand_Ligth1)

        payLoadObject =  
            {
                "id": "urn:ngsi-ld:pHueActuator:light1",
                "type": "Extended_color_light",
                "set-on": {
                    "type": "command",
                    "value": nextValueCommand_Ligth1.toString()
                }
            }

        if(nextValueCommand_Ligth1.toString() == "False") {
            nextValueCommand_Ligth1 = "True"
        } else {
            nextValueCommand_Ligth1 = "False"
        }
    
        const response = await appendCBEntity(payLoadObject,vSiloUrlCB)
    }

}, config.frecuency_mseg_Light1);  

// PERIODIC PROCESS - Light2
setInterval(async function() {

    if (actuatorLight2) {


        console.log(util.unixTime(Date.now()) + " - Light2 - set-hue: " + nextValueCommand_Light2)

        var payLoadObject =  
                {
                    "id": "urn:ngsi-ld:pHueActuator:light2",
                    "type": "Extended_color_light",
                    "set-hue": {
                        "type": "command",
                        "value": nextValueCommand_Light2.toString()
                    }
                }

        const response = await appendCBEntity(payLoadObject,vSiloUrlCB)

        nextValueCommand_Light2 = nextValueCommand_Light2 + increasingStepColorLight2

        if (nextValueCommand_Light2 > 65535) {
            nextValueCommand_Light2 = 1
        }
      
    }

}, config.frecuency_mseg_Light2);  


// PERIODIC PROCESS - Light3
setInterval(async  function() {

    if (actuatorLight3) {
        var payLoadObject 

        console.log(util.unixTime(Date.now()) + " - Light3 - set-on: " + nextValueCommand_Light3)

        payLoadObject =  
            {
                "id": "urn:ngsi-ld:pHueActuator:light3",
                "type": "Extended_color_light",
                "set-on": {
                    "type": "command",
                    "value": nextValueCommand_Light3.toString()
                }
            }

        if(nextValueCommand_Light3.toString() == "False") {
            nextValueCommand_Light3 = "True"
        } else {
            nextValueCommand_Light3 = "False"
        }
    
        const response = await appendCBEntity(payLoadObject,vSiloUrlCB)
    }

}, config.frecuency_mseg_Light3); 
