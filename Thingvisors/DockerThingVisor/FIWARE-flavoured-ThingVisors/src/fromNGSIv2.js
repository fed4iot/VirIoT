/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

"use strict";

var libWrapperUtils = require("./wrapperUtils");

var urlNGSILDOntology = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld";

//body --> Only One Orion Context Entity (NGSI v2)
//return --> Only One Orion Context Entity (NGSI-LD)
function fromNGSIv2toNGSILD(body,ldContext){

  /*
  var bodyData = []
  var bodyLength
 
  bodyData.push(body)

  if (typeof body.subscriptionId == "undefined") { //Subscription body
    bodyData = []
    bodyData.push(body)
  } else { //Simple entity body
    bodyData = body.data;  
  }

  bodyLength = bodyData.length
  */

  var bodyData = body

  //var entity
  //var entities={};
  var attributes={};
  var ocbType="", ocbId=""
  var matchKeyResponse=[]

  /*
  for(var j=0; j< bodyLength;j++){
      entity = bodyData[j];
      attributes = {};

      ocbType=""
      ocbId=""

      matchKeyResponse=[]

      for(let i in entity){
          if ( i != "id" && i != "type"){
              matchKeyResponse =  match_keyNGSIv2(i, entity[i], "", "", "")

              if (matchKeyResponse.length=2) {
                attributes[matchKeyResponse[0]] =  matchKeyResponse[1]
              }
              
          } else if (i == "id"){
              attributes[i] = entity[i];
              ocbId = entity[i]
          } else {//type
            attributes[i] = entity[i];
            ocbType = entity[i]
          }
      }

      attributes["id"] = format_uri(ocbType,ocbId)
      entities[attributes["id"]] = attributes
  }
  */
  for(let i in bodyData){

    if ( i != "id" && i != "type"){
        matchKeyResponse =  match_keyNGSIv2(i, bodyData[i], "", "", "")

        if (matchKeyResponse.length=2) {
          attributes[matchKeyResponse[0]] =  matchKeyResponse[1]
        }
    } else if (i == "id"){
        //attributes[i] = bodyData[i];
        ocbId = bodyData[i]
    } else if (i == "type"){
      attributes[i] = bodyData[i];
      ocbType = bodyData[i]
    }
  }

  //TODO: Test this code.
  var test = false
  if (typeof attributes["@context"] != "undefined") {
    for(var k=0; k< attributes["@context"].length; k++) {
      if (attributes["@context"][k] == urlNGSILDOntology) {
        test = true
        break;
      }
    }
    if (test == false) {
      attributes["@context"].push(urlNGSILDOntology)
    }
  } else {
    attributes["@context"]=[urlNGSILDOntology]
  }

  attributes["id"] = libWrapperUtils.format_uri(ocbType,ocbId)

  return attributes
}  

function match_keyNGSIv2(key, attribute, paramIn, paramOut, ldReversedContext) {
  var attrObject

  if (key.toUpperCase() == "dateCreated".toUpperCase() ) {
    return ["createdAt", attribute.value]
  } else if (key.toUpperCase() == "dateModified".toUpperCase() ) {
    return ["modifiedAt", attribute.value]
  } else if (key.toUpperCase() == "@context".toUpperCase() ) {

    var valueContext = ""
    if (typeof attribute.value === "undefined") {
      valueContext = attribute
    } else {
      valueContext = attribute.value
    }

    //return ["@context", attribute.value]
    return ["@context", valueContext]
  //NGSI-LD DateTime format "observedAt"
  //Response: Error: "title": "Attribute must be a JSON object",
  } else if (key.toUpperCase() == "timestamp".toUpperCase() ) {
    //return ["observedAt", attribute.value]
    //return ["observedAt", {type: 'Property', value: attribute.value} ]
    return ["observedAt", {type: 'Property', value: {"@type": attribute.type, "@value": attribute.value}} ]
  } else {

    if (libWrapperUtils.AnyProp(key)) {

      attrObject={}

      const declType = attribute.type || attribute.Property || ""
      var isRelationship = false

      //Testing if the attribute will be a NGSI-LD relationship.
      if (!libWrapperUtils.ReferenceAttr(key) && declType != "Relationship" && declType != "Reference") { //No NGSI-LD relationship.
/*      
        if (declType.toUpperCase() == "geo:json".toUpperCase() ||        // { type:, value: {type: , coordinates:} }
            declType.toUpperCase() == "geo:point".toUpperCase() ||       // { type:, value: }
            declType.toUpperCase() == "geo:line".toUpperCase() ||        // { type:, value: }
            declType.toUpperCase() == "geo:box".toUpperCase() ||         // { type:, value: }
            declType.toUpperCase() == "geo:polygon".toUpperCase() ||     // { type:, value: }
            declType.toUpperCase() == "coords".toUpperCase() ||          // { type:, value: }
            declType.toUpperCase() == "Point".toUpperCase() ||           // {type: , coordinates:}
            declType.toUpperCase() == "LineString".toUpperCase() ||      // {type: , coordinates:}
            declType.toUpperCase() == "Polygon".toUpperCase() ||         // {type: , coordinates:}
            declType.toUpperCase() == "MultiPoint".toUpperCase() ||      // {type: , coordinates:}
            declType.toUpperCase() == "MultiLineString".toUpperCase() || // {type: , coordinates:}
            declType.toUpperCase() == "MultiPolygon".toUpperCase() ||    // {type: , coordinates:}
            key == "location") {
*/
        //Version 0: Only consider NGSI-v2 geo:json type attribute as a NGSI-LD GeoProperty.
        //Version 1: consider NGSI-v2 coords type attribute as a NGSI-LD GeoProperty geo:json point type.
        //Version 2: consider NGSI-v2 geo:point type attribute as a NGSI-LD GeoProperty geo:json point type.
        if (declType == "geo:json" || declType == "coords" || declType == "geo:point" || declType == "geo:polygon") {
          attrObject["type"] = "GeoProperty";
        } else {
          attrObject["type"] = "Property";
        }

        var valueType = ""

        if (declType.toUpperCase() == "DateTime".toUpperCase()) {
          valueType = "DateTime"
        }

        var valueAttr = attribute.value

        if (typeof valueAttr == "undefined") {
          valueAttr = attribute
        }

        //Version 1: consider NGSI-v2 coords type attribute as a NGSI-LD GeoProperty geo:json point type.
        //Version 2: consider NGSI-v2 geo:point type attribute as a NGSI-LD GeoProperty geo:json point type.
        if (declType == "coords" || declType == "geo:point") {
          valueAttr = {type: "Point", 
                      coordinates:[ parseFloat(attribute.value.split(",")[1]), parseFloat(attribute.value.split(",")[0]) ]
                      }
        } else if (declType == "geo:polygon") {
          var aux = []
          
          for(var i=0; i< attribute.value.length; i++){

            aux.push([ parseFloat(attribute.value[i].split(",")[1]), parseFloat(attribute.value[i].split(",")[0]) ])
          }

          valueAttr = {type: "Polygon", 
                      coordinates:[ aux ]
                      }
          
        }

        attrObject["value"] = libWrapperUtils.format_value(attrObject["type"], valueAttr, "",  valueType)

      } else { //NGSI-LD relationship.
          isRelationship = true
          attrObject["type"] = "Relationship";
          attrObject["object"] = "";

          attrObject.object = libWrapperUtils.format_value(attrObject["type"], attribute.value, "",  "")
      }

      if (typeof attribute.metadata != "undefined") {
        var metadataBody = attribute.metadata

        for(let i in metadataBody){
          if (i.toUpperCase()=="timestamp".toUpperCase()) {
            //TODO: Review --> I think it may do.
            //TODO: Review --> NGSI-LD DateTime format?.
            //attrObject["observedAt"] = metadataBody[i].value.split(".")[0]
            attrObject["observedAt"] = metadataBody[i].value
          } else if (i.toUpperCase()=="unitCode".toUpperCase()) {
            attrObject[i] = metadataBody[i].value
          } else if (i.toUpperCase()=="entityType".toUpperCase()) {

            if (isRelationship && typeof metadataBody[i].value != "undefined") {
              attrObject.object = libWrapperUtils.format_uri(metadataBody[i].value, attribute.value)
            }
          } else { 
            var matchKeyResponse = []

            matchKeyResponse = match_keyNGSIv2(i, metadataBody[i], "", "", "")

            if (matchKeyResponse.length==2) {
              attrObject[i] = matchKeyResponse[1]
            }
          }
        }
      }

      return [key, attrObject]

    } else {
      //No attribute name.
      return []
    }
  }
}

module.exports.fromNGSIv2toNGSILD = fromNGSIv2toNGSILD;
