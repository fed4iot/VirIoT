/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

"use strict";

var keyrock = require("./keyrock");
var capman = require("./capman");
var pepproxy = require("./pepproxy");
var config = require("./config.json");

async function mainProcedure() {

    var keyrockHeaders = {"Content-Type":"application/json"}
    var keyrockBody = {"name": config.keyrock_user_mail,"password":config.keyrock_usep_pass}

    var keyrockMethod="POST"
    var keyrockPath="/v1/auth/tokens"


    console.log("******* Sending authentication request to KeyRock... *******")
    console.log("Method: " + keyrockMethod)
    console.log("URL: " + config.keyrock_protocol + "://" + config.keyrock_host + ":" + config.keyrock_port + keyrockPath)
    console.log("Headers: " + JSON.stringify(keyrockHeaders))
    console.log("Body: " + JSON.stringify(keyrockBody))

    try {

        if (config.keyrock_protocol == "https" || config.keyrock_protocol == "http") {
            var responseKeyrock = await keyrock.POST_LoginToGetToken (keyrockHeaders, keyrockBody, config.keyrock_protocol, 
                                                                      config.keyrock_host, config.keyrock_port, keyrockPath);
            //console.log(responseKeyrock)

            var status = responseKeyrock.statusCode

            if (status == 201 ) {

                var keyrockToken = responseKeyrock.headers["x-subject-token"]

                console.log("\nAUTH SUCCESS: Authentication Keyrock Token obtained : " + keyrockToken)

                var capmanHeaders = {"Content-Type":"application/json"}
                var capmanBody = {"token":keyrockToken,"ac":config.policy_action,"de":config.policy_device,"re":config.policy_resource}

                var capmanMethod="POST"
                var capmanPath="/"

                console.log("\n******* Sending authorisation request to Capability Manager... *******")
                console.log("Method: " + capmanMethod)
                console.log("URL: " + config.capman_protocol + "://" + config.capman_host + ":" + config.capman_port + capmanPath)
                console.log("Headers: " + JSON.stringify(capmanHeaders))
                console.log("Body: " + JSON.stringify(capmanBody))

                if (config.keyrock_protocol == "https" || config.keyrock_protocol == "http") {

                    var responseCapManager = await capman.POST_ObtainCapabilityToken (capmanHeaders, capmanBody, config.capman_protocol, 
                                                                                  config.capman_host, config.capman_port, capmanPath);
                    //console.log(responseCapManager)

                    var status = responseCapManager.statusCode

                    if(status==200){

                        console.log("\nSUCCESS: Authorisation Granted --> Capability token obtained : " + responseCapManager.body)

                        var pepproxyHeaders = config.pepproxy_targetRequestHeaders
                        pepproxyHeaders["x-auth-token"] = responseCapManager.body
                        
                        var pepproxyMethod=config.policy_action  
                        var pepproxyPath=config.policy_resource                        
                
                        console.log("\n******* Sending API query to Target through PEP_PROXY... *******")
                        console.log("Method: " + pepproxyMethod)
                        console.log("URL: " + config.pepproxy_protocol + "://" + config.pepproxy_host + ":" + config.pepproxy_port + pepproxyPath)
                        console.log("Headers: " + JSON.stringify(pepproxyHeaders))

                        if (config.keyrock_protocol == "https" || config.keyrock_protocol == "http") {

                            var responsePepProxy = await pepproxy.GET_Resource (pepproxyHeaders, config.pepproxy_protocol, 
                                                                                config.pepproxy_host, config.pepproxy_port, pepproxyPath);

                            console.log("\nSUCCESS: PEP-Proxy response (from target API):\n")
                            console.log("* Status: " + responsePepProxy.statusCode)
                            console.log("* Headers:\n" + JSON.stringify(responsePepProxy.headers))
                            console.log("* Body:\n" + responsePepProxy.body)

                        } else {
                            console.log("Error PEP-Proxy: bad protocol")
                        } 

                    } else {
                        console.log("\nFAILURE Authorisation Error --> Capability Manager.")
                        console.log("Status: " + responseKeyrock.statusCode)
                        console.log("Body: " + responseKeyrock.body)
                    }

                } else {
                    console.log("Error Capability Manager: bad protocol")
                }

            } else {
                console.log("\nFAILURE: Authentication Error --> Keyrock")
                console.log("Status: " + responseKeyrock.statusCode)
                console.log("Body: " + responseKeyrock.body)
            }

        } else {
            console.log("Error Keyrock: bad protocol")
        }

    } catch(e) {
        console.log(`\t\t       SUCCESS: ERROR : Get fails(2): ` + e.toString());                        
    }


    
}

mainProcedure()