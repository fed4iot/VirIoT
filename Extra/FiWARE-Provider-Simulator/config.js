/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

module.exports = {

    MQTTBrokerHost: process.env.MQTTBrokerHost,
    MQTTBrokerPort: process.env.MQTTBrokerPort,
    
    commandStart: 'start',
    commandStop: 'stop',
    commandReset: 'reset',
    commandIncreasing: 'increasing',
    commanSetCounter: 'setCounter',

    MQTTbrokerApiKey: '/fed4iot',
    
    MQTTbrokerTopicCmd: 'cmd',
    MQTTbrokerTopicCmdExe: 'cmdexe',
    MQTTbrokerTopicAttrs: 'attrs',

    frecuency_mseg_device001: process.env.frecuency_mseg_device001 || 60000,
    frecuency_mseg_device002: process.env.frecuency_mseg_device002 || 60000,
    frecuency_mseg_device003: process.env.frecuency_mseg_device003 || 60000
}