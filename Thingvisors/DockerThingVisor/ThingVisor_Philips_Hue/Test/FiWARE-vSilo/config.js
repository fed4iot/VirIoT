/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

module.exports = {

    tenantID: process.env.tenantID,

    vSiloProtocol: process.env.vSiloProtocol || 'http',
    vSiloHost: process.env.vSiloHost,
    vSiloPort: process.env.vSiloPort,
      
    actuatorLight1: process.env.actuatorLight1 || 0,
    frecuency_mseg_Light1: process.env.frecuency_mseg_Light1 || 2000,

    actuatorLight2: process.env.actuatorLight2 || 0,
    initialValueColorLight2: process.env.initialValueColorLight2 || 23536,
    increasingStepColorLight2: process.env.increasingStepColorLight2 || 5000,
    frecuency_mseg_Light2: process.env.frecuency_mseg_Light2 || 3000,

    actuatorLight3: process.env.actuatorLight3 || 0,
    frecuency_mseg_Light3: process.env.frecuency_mseg_Light3 || 6000

}