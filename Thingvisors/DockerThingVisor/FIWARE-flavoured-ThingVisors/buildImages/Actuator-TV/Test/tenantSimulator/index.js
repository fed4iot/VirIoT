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
      
var actuatorDevice001
var frecuency_mseg_Device001

var actuatorDevice002
var frecuency_mseg_Device002

var actuatorDevice003
var counterValue_Device003
var frecuency_mseg_Device003

var nextCommand_Device001
var nextIncreasing_Device002
var nextCommand_Device003

var executionStart
var executionStop
var executionReset

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
    
    actuatorDevice001 = true
    if (config.actuatorDevice001 == 0) {
        actuatorDevice001 = false
    }
    frecuency_mseg_Device001 = config.frecuency_mseg_Device001

    actuatorDevice002 = true
    if (config.actuatorDevice002 == 0) {
        actuatorDevice002 = false
    }
    frecuency_mseg_Device002 = config.frecuency_mseg_Device002

    actuatorDevice003 = true
    if (config.actuatorDevice003 == 0) {
        actuatorDevice003 = false
    }
    counterValue_Device003 = config.counterValue_Device003
    frecuency_mseg_Device003 = config.frecuency_mseg_Device003

    nextCommand_Device001 = "start"
    nextIncreasing_Device002 = true
    nextCommand_Device003 = "reset"

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

    executionStart = 0
    executionStop = 0
    executionReset = 0

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

// PERIODIC PROCESS - device001 (attrs)
setInterval(async  function() {

    if (actuatorDevice001) {
        var payLoadObject 

        if(nextCommand_Device001 == "start") {

            executionStart = executionStart + 1

            console.log(util.unixTime(Date.now()) + " - " + tenantID + " - Device001 - start")

            payLoadObject =  
                {
                    "id": "urn:ngsi-ld:Device:001",
                    "type": "Device",
                    "start": {
                        "type": "command",
                        "value": tenantID.toString() + ":" + executionStart.toString()
                    }
                }

            nextCommand_Device001 = "stop"

        } else {

            executionStop = executionStop + 1

            console.log(util.unixTime(Date.now()) + " - " + tenantID + " - Device001 - stop")

            payLoadObject =  
                {
                    "id": "urn:ngsi-ld:Device:001",
                    "type": "Device",
                    "stop": {
                        "type": "command",
                        "value": tenantID.toString() + ":" + executionStop.toString()
                    }
                }

            nextCommand_Device001 = "start"

        }
    
        const response = await appendCBEntity(payLoadObject,vSiloUrlCB)
    }

}, config.frecuency_mseg_Device001);  

// PERIODIC PROCESS - device002 (attrs)
setInterval(async function() {

    if (actuatorDevice002) {

        console.log(util.unixTime(Date.now()) + " - " + tenantID + " - Device002 - increasing: " + nextIncreasing_Device002)

        var payLoadObject =  
                {
                    "id": "urn:ngsi-ld:Device:002",
                    "type": "Device",
                    "increasing": {
                        "type": "command",
                        "value": nextIncreasing_Device002.toString()
                    }
                }

        const response = await appendCBEntity(payLoadObject,vSiloUrlCB)

        if(nextIncreasing_Device002) {
            nextIncreasing_Device002 = false
        } else {
            nextIncreasing_Device002 = true
        }
        
    }

}, config.frecuency_mseg_Device002);  


// PERIODIC PROCESS - device003 (attrs)
setInterval(async  function() {

    if (actuatorDevice003) {
      
        var payLoadObject

        if(nextCommand_Device003 == "reset") {
    
            executionReset = executionReset + 1

            console.log(util.unixTime(Date.now()) + " - " + tenantID + " - Device003 - reset")

            payLoadObject =  
                {
                    "id": "urn:ngsi-ld:Device:003",
                    "type": "Device",
                    "reset": {
                        "type": "command",
                        "value": tenantID.toString() + ":" + executionReset.toString()
                    }
                }

            nextCommand_Device003 = "setCounter"

        } else {

            console.log(util.unixTime(Date.now()) + " - " + tenantID + " - Device003 - setCounter: " + counterValue_Device003)

            payLoadObject =  
                {
                    "id": "urn:ngsi-ld:Device:003",
                    "type": "Device",
                    "setCounter": {
                        "type": "command",
                        "value": counterValue_Device003.toString()
                    }
                }

            nextCommand_Device003 = "reset"

        }

        const response = await appendCBEntity(payLoadObject,vSiloUrlCB)

    }

}, config.frecuency_mseg_Device003);  

