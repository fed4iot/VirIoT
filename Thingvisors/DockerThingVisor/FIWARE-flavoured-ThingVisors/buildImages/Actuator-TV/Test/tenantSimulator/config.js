/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

module.exports = {

    tenantID: process.env.tenantID,

    vSiloProtocol: process.env.vSiloProtocol || 'http',
    vSiloHost: process.env.vSiloHost,
    vSiloPort: process.env.vSiloPort,
      
    actuatorDevice001: process.env.actuatorDevice001 || 0,
    frecuency_mseg_Device001: process.env.frecuency_mseg_Device001 || 60000,

    actuatorDevice002: process.env.actuatorDevice002 || 0,
    frecuency_mseg_Device002: process.env.frecuency_mseg_Device002 || 60000,

    actuatorDevice003: process.env.actuatorDevice003 || 0,
    counterValue_Device003: process.env.counterValue_Device003 || 11,
    frecuency_mseg_Device003: process.env.frecuency_mseg_Device003 || 60000

}