/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

"use strict";

//Convert timestamp format to string
function unixTime(unixDate) {

    var date = new Date(parseInt(unixDate));
  
    //Obtain local time string
    var cadena1 = date.getFullYear() + '-' +
    ('0' + (parseInt(date.getMonth())+1).toString()).slice(-2) + '-' +
    ('0' + date.getDate()).slice(-2) + ' ' +
    ('0' + date.getHours()).slice(-2) + ':' +
    ('0' + date.getMinutes()).slice(-2) + ':' +
    ('0' + date.getSeconds()).slice(-2)
  
    return cadena1
};

module.exports.unixTime = unixTime; 
