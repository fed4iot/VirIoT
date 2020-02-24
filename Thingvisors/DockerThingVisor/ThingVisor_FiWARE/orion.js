"use strict";

var http = require('http');

//Send request
function httpRequest(params, postData) {
    return new Promise(function(resolve, reject) {

        var req = http.request(params, function(res) {
            // reject on bad status
            if (res.statusCode < 200 || res.statusCode >= 300) {
                return reject(new Error('statusCode=' + res.statusCode));
            }
            // cumulate data
            var body = [];
            res.on('data', function(chunk) {
                body.push(chunk);
            });
            // resolve on end
            res.on('end', function() {
                try {
                    if (body.length>0) { //To prevent: [SyntaxError: Unexpected end of input]
                        body = JSON.parse(Buffer.concat(body).toString());    
                    }

                } catch(e) {
                    reject(e);
                }
                resolve(body);
            });
        });
        // reject on request error
        req.on('error', function(err) {
            // This is not a "Second reject", just a different sort of failure
            reject(err);
        });
        if (postData) {
            req.write(postData);
        }
        // IMPORTANT
        req.end();
    });
}

//Access to Orion Context Broker entity.
function obtainCBEntity (idOCB, ocb_service, ocb_servicePath, ocb_ip, ocb_port) {
    return new Promise(function(resolve, reject) {
        
        var params = {
                        method: 'get',
                        host: ocb_ip,
                        path: '/v2/entities/'+idOCB,
                        port: ocb_port,
                        headers: {'Accept': 'application/json',
                                'Fiware-Service' : ocb_service,
                                'Fiware-ServicePath' : ocb_servicePath}
                    }

        httpRequest(params).then(function(body) {
            resolve(body);
            reject('');
//            return httpRequest(otherParams);
        }).then(function(body) {
        }).catch(err => {
            reject(err)
        });
    });
};

//Access to all Orion Context Broker entities.
function obtainALLCBEntities (offset, limit, ocb_ip, ocb_port, ocb_service, ocb_servicePath) {
    return new Promise(function(resolve, reject) {
        
        var params = {
                method: 'get',
                host: ocb_ip,
                path: '/v2/entities?offset=' + offset + '&limit=' + limit + '&options=count',
                port: ocb_port,
                headers: {'Accept': 'application/json',
                'Fiware-Service' : ocb_service,
                'Fiware-ServicePath' : ocb_servicePath}
                }
        
        httpRequest(params).then(function(body) {
            resolve(body);
            reject('');
//            return httpRequest(otherParams);
        }).then(function(body) {
        }).catch(err => {
            reject(err)
        });
    });
};

//Access to all Orion Context Broker entities.
function obtainALLCBEntitiesPerType (offset, limit, ocb_ip, ocb_port, ocb_service, ocb_servicePath, ocb_type) {
    return new Promise(function(resolve, reject) {
        
        var params = {
                method: 'get',
                host: ocb_ip,
                path: '/v2/entities?type=' + ocb_type + '&offset=' + offset + '&limit=' + limit + '&options=count',
                port: ocb_port,
                headers: {'Accept': 'application/json',
                'Fiware-Service' : ocb_service,
                'Fiware-ServicePath' : ocb_servicePath}
                }
        
        console.log(params)
        
        httpRequest(params).then(function(body) {
            resolve(body);
            reject('');
//            return httpRequest(otherParams);
        }).then(function(body) {
        }).catch(err => {
            reject(err)
        });
    });
};


//Access to Orion Context Broker Subscriptions...
function obtainCBSubscriptions (offset, limit, ocb_ip, ocb_port, ocb_service, ocb_servicePath) {
    return new Promise(function(resolve, reject) {
        
        var params = {
                method: 'get',
                host: ocb_ip,
                path: '/v2/subscriptions?offset=' + offset + '&limit=' + limit + '&options=count',
                port: ocb_port,
                headers: {'Accept': 'application/json',
                'Fiware-Service' : ocb_service,
                'Fiware-ServicePath' : ocb_servicePath}
                }
        
        httpRequest(params).then(function(body) {
            resolve(body);
            reject('');
//            return httpRequest(otherParams);
        }).then(function(body) {
        }).catch(err => {
            reject(err)
        });
    });
};

module.exports.obtainCBEntity = obtainCBEntity; 
module.exports.obtainALLCBEntities = obtainALLCBEntities;
module.exports.obtainALLCBEntitiesPerType = obtainALLCBEntitiesPerType;
module.exports.obtainCBSubscriptions = obtainCBSubscriptions;
