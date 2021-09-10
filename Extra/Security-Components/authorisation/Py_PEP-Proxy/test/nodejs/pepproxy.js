/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

"use strict";

var request = require("request");

function GET_Resource (reqHeaders, url_protocol, url_ip, url_port, url_resource) {
    return new Promise(function(resolve, reject) {

        var options = { method: "get",
                        url: url_protocol + "://" + url_ip+":"+url_port+url_resource,
                        headers:  reqHeaders
                    };
        
        request(options, function (error, response, body) {
            
            if (error) { 
                console.log(cuerpo)
                console.log(error)
                reject(error)    
            }
            else {
                resolve(response);
                reject('');
            }
            
        })
    })
}

module.exports.GET_Resource = GET_Resource;