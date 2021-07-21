/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

"use strict";

var request = require("request");

function POST_LoginToGetToken (reqHeaders, reqBody, url_protocol, url_ip, url_port, url_resource) {
    return new Promise(function(resolve, reject) {

        var options = { method: "post",
                        url: url_protocol + "://" + url_ip+":"+url_port+url_resource,
                        headers: reqHeaders,
                        body: JSON.stringify(reqBody)
                    };

        request(options, function (error, response, body) {
            
            if (error) { 
                console.log(reqBody)
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


module.exports.POST_LoginToGetToken = POST_LoginToGetToken;
