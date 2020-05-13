/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

"use strict";

var libWrapperUtils = require("./wrapperUtils");

//body --> Only One Orion Context Entity (NGSI-LD)
//return --> Only One Orion Context Entity (NGSI v2) or Only One Orion Context Entity (NGSI v1) --> An element of contextResponses object

//Differences: 
// -  Id: NGSI-LD builds a format_uri id value if NGSIv* doesn't have this format.
// -  Attribute Types: In NGSI-LD all attributes have a generic value (Property, Relationship, ...) in attribute type.
// -  Attribute @context: In NGSI-LD this attribute hasn't a type but, if in NGSIv* we use NGSIv2 APPEND by default the system assigns "StructuredValue" 
//    value to Attribute @context type.

function fromNGSILDtoNGSI(body, param, ldContext){
  //param="v1" or "v2"
  
  /*
  var bodyData
  var bodyLength
 
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

    ocbType="", ocbId=""

    matchKeyResponse=[]

    for(let i in entity){
      if ( i != "id" && i != "type" && i != "@context"){
        if (param.toUpperCase()=="v2".toUpperCase()) { //To NGSIv2
          matchKeyResponse =  match_key_v2_NGSILD(i, entity[i], "", "", "", "")
        } else if (param.toUpperCase()=="v1".toUpperCase()) { //To NGSIv1
          matchKeyResponse =  match_key_v1_NGSILD(i, entity[i], "", "", "". "")
        }
        if (matchKeyResponse.length=2) {
          attributes[matchKeyResponse[0]] =  matchKeyResponse[1]
        }
      } else if (i == "@context"){
        attributes[i] = entity[i];
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

  var attributesv1=[]

  for(let i in bodyData){
    //if ( i != "id" && i != "type"){

    if ( i != "id" && i != "type" && i != "@context" && i != "observedAt" && i != "createdAt" && i != "modifiedAt"){//Processing attributes
      if (param.toUpperCase()=="v2".toUpperCase()) { //To NGSIv2
        matchKeyResponse =  match_key_v2_NGSILD(i, bodyData[i], "", "", "", "")
      } else if (param.toUpperCase()=="v1".toUpperCase()) { //To NGSIv1
        matchKeyResponse =  match_key_v1_NGSILD(i, bodyData[i], "", "", "", "")
      }
      if (matchKeyResponse.length=2) {

        if (param.toUpperCase()=="v2".toUpperCase()) {
          attributes[matchKeyResponse[0]] =  matchKeyResponse[1]
        } else if (param.toUpperCase()=="v1".toUpperCase()) {
          attributesv1.push(matchKeyResponse[1])
        }
        
      }
    } else if (i == "@context"){
      //attributes[i] = bodyData[i];
      if (param.toUpperCase()=="v2".toUpperCase()) {
        attributes[i] = {value: bodyData[i], type: "StructuredValue", metadata: {} }
      } else if (param.toUpperCase()=="v1".toUpperCase()) {
        attributesv1.push({name: i, type: "StructuredValue", value: bodyData[i]})
      }
    } else if (i == "createdAt"){
      if (param.toUpperCase()=="v2".toUpperCase()) {
        attributes["dateCreated"] = {value: bodyData[i], type: "DateTime", metadata: {} }
      } else if (param.toUpperCase()=="v1".toUpperCase()) {
        attributesv1.push({name: "dateCreated", type: "DateTime", value: bodyData[i]})
      }
    } else if (i == "modifiedAt"){
      if (param.toUpperCase()=="v2".toUpperCase()) {
        attributes["dateModified"] = {value: bodyData[i], type: "DateTime", metadata: {} }
      } else if (param.toUpperCase()=="v1".toUpperCase()) {
        attributesv1.push({name: "dateModified", type: "DateTime", value: bodyData[i]})
      }
    } else if (i == "observedAt"){
      //NGSI-LD DateTime format "observedAt"
      if (param.toUpperCase()=="v2".toUpperCase()) {
        //attributes["timestamp"] = {value: bodyData[i], type: "DateTime", metadata: {} }
        //attributes["timestamp"] = {value: bodyData[i].value, type: "DateTime", metadata: {} }

        var valueTimestamp
        if (typeof bodyData[i].value["@value"] != "undefined") { //More frecuent option
          valueTimestamp = bodyData[i].value["@value"]
        } else if (typeof bodyData[i].value.value != "undefined") { //Less frecuent option
          valueTimestamp = bodyData[i].value.value
        } else { //Never access option...
          valueTimestamp = bodyData[i].value
        }

        attributes["timestamp"] = {value: valueTimestamp, type: "DateTime", metadata: {} }
      } else if (param.toUpperCase()=="v1".toUpperCase()) {
        //attributesv1.push({name: "timestamp", type: "DateTime", value: bodyData[i]})
        //attributesv1.push({name: "timestamp", type: "DateTime", value: bodyData[i].value})

        var valueTimestamp
        if (typeof bodyData[i].value["@value"] != "undefined") { //More frecuent option
          valueTimestamp = bodyData[i].value["@value"]
        } else if (typeof bodyData[i].value.value != "undefined") { //Less frecuent option
          valueTimestamp = bodyData[i].value.value
        } else { //Never access option...
          valueTimestamp = bodyData[i].value
        }

        attributesv1.push({name: "timestamp", type: "DateTime", value: valueTimestamp})
      }
    } else if (i == "id"){
      attributes[i] = bodyData[i];
      ocbId = bodyData[i]
    } else if (i == "type"){
      attributes[i] = bodyData[i];
      ocbType = bodyData[i]
    }
  }

  if  (param.toUpperCase() == "v1".toUpperCase()) {
    attributes["attributes"] = attributesv1
    attributes["isPattern"] = false
  }    
  
  //attributes["id"] = format_uri(ocbType,ocbId)
  
  return attributes
}


function match_key_v2_NGSILD(key, attribute, paramIn, paramOut, parentKey, ldReversedContext) {

  var attrObject = {}
  var metadataObject = {}
  
  for(let attr in attribute){

    if (attr == "type") {
      if (attribute.type.toUpperCase() == "Property".toUpperCase()){

        var typeProperty=""
        var value2Property=""
        var type2Property=""

        if (typeof attribute.value == "object") {
          
          if (typeof attribute.value["type"] != "undefined") {
            typeProperty = attribute.value["type"] || ""
          }

          if (typeof attribute.value["@value"] != "undefined") {
            value2Property = attribute.value["@value"] || ""
          }
          if (typeof attribute.value["@type"] != "undefined") {
            type2Property = attribute.value["@type"] || ""
          }

          if (typeProperty == "") {
            typeProperty = type2Property
          }

          if (value2Property != "") {
            if (typeProperty != "") {
              attrObject.type = typeProperty
            } else {
              attrObject.type = libWrapperUtils.obtain_NGSIAttributeValue(typeof value2Property)
            }
            attrObject.value = value2Property
          } else {
            attrObject.type = "StructuredValue"
            attrObject.value = attribute.value
          }
        } else {
          //attrObject.type = "Property"
          attrObject.type = libWrapperUtils.obtain_NGSIAttributeValue(typeof attribute.value)
          attrObject.value = attribute.value
        }
      } else if (attribute.type.toUpperCase() == "Relationship".toUpperCase()) {
          if (typeof attribute.object != "undefined") {
            attrObject.type = "Relationship"
            //attrObject.type = libWrapperUtils.obtain_NGSIAttributeValue(typeof attribute.object)
            attrObject.value = attribute.object

            if (parentKey == "") {
              var resultArray = []

              resultArray = libWrapperUtils.UrnPattern(attribute.object)

              if (resultArray.length==2) {
                metadataObject.entityType={value: resultArray[0], type: libWrapperUtils.obtain_NGSIAttributeValue(typeof resultArray[0]) }
                //metadataObject.entityType=resultArray[1]
              }
            }
          }
      } else if (attribute.type.toUpperCase() == "GeoProperty".toUpperCase()) {
          
          attrObject.type = "geo:json"
          attrObject.value = attribute.value
      }
    } else if (attr.toUpperCase() == "observedAt".toUpperCase()) {
      //NGSI-LD DateTime format.
      metadataObject.timestamp = {value: attribute[attr], type: "DateTime"}

    } else if (attr.toUpperCase() == "unitCode".toUpperCase()) {

      metadataObject.unitCode = {value: attribute[attr], type: libWrapperUtils.obtain_NGSIAttributeValue(typeof attribute[attr])}

    //} else if (attr.toUpperCase() == "@context".toUpperCase()) {
    //  attrObject.type = "StructuredValue"
    //  attrObject.value = attribute.value

    } else if (attr.toUpperCase() == "entityType".toUpperCase()) {
      metadataObject.entityType = {value: attribute[attr], type: libWrapperUtils.obtain_NGSIAttributeValue(typeof attribute[attr])}

    } else if (attr != "value" && attr != "object") {
      var matchKeyResponse = []

      matchKeyResponse = match_key_v2_NGSILD(attr,attribute[attr],"",metadataObject,key,ldReversedContext) 

      if (matchKeyResponse.length==2) {
        metadataObject[matchKeyResponse[0]] = matchKeyResponse[1]
      }
    }
  }
  if (parentKey == "")   {
    attrObject.metadata = metadataObject
  }
  return [key, attrObject]
}

function match_key_v1_NGSILD(key, attribute, paramIn, paramOut, parentKey, ldReversedContext) {

  var attrObject = {}
  //var metadataObject = {}
  var metadataObject = []

  for(let attr in attribute){

    if (attr == "type") {
      if (attribute.type.toUpperCase() == "Property".toUpperCase()){

        var typeProperty=""
        var value2Property=""
        var type2Property=""

        if (typeof attribute.value == "object") {
          
          if (typeof attribute.value["type"] != "undefined") {
            typeProperty = attribute.value["type"] || ""
          }

          if (typeof attribute.value["@value"] != "undefined") {
            value2Property = attribute.value["@value"] || ""
          }
          if (typeof attribute.value["@type"] != "undefined") {
            type2Property = attribute.value["@type"] || ""
          }

          if (typeProperty == "") {
            typeProperty = type2Property
          }

          if (value2Property != "") {
            if (typeProperty != "") {

              attrObject.type = typeProperty
            } else {
              attrObject.type = libWrapperUtils.obtain_NGSIAttributeValue(typeof value2Property)
            }
            attrObject.value = value2Property
            attrObject.name = key
          } else {
            attrObject.type = "StructuredValue"
            attrObject.value = attribute.value
          }

        } else {
          
          //attrObject.type = "Property"
          attrObject.type = libWrapperUtils.obtain_NGSIAttributeValue(typeof attribute.value)
          attrObject.value = attribute.value
          attrObject.name = key
        }
      } else if (attribute.type.toUpperCase() == "Relationship".toUpperCase()) {
          if (typeof attribute.object != "undefined") {
            attrObject.type = "Relationship"
            //attrObject.type = libWrapperUtils.obtain_NGSIAttributeValue(typeof attribute.object)
            attrObject.value = attribute.object
            attrObject.name = key
       
            if (parentKey == "") {
              var resultArray = []

              resultArray = libWrapperUtils.UrnPattern(attribute.object)

              if (resultArray.length==2) {
                //metadataObject.entityType={name: "entityType", value: resultArray[0], type: libWrapperUtils.obtain_NGSIAttributeValue(typeof resultArray[0]) }
                metadataObject.push({name: "entityType", value: resultArray[0], type: libWrapperUtils.obtain_NGSIAttributeValue(typeof resultArray[0])})
                //metadataObject.entityType=resultArray[1]
              }
            }
          }
      } else if (attribute.type.toUpperCase() == "GeoProperty".toUpperCase()) {
          attrObject.type = "geo:json"
          attrObject.value = attribute.value
          attrObject.name = key
      }
    } else if (attr.toUpperCase() == "observedAt".toUpperCase()) {
      //metadataObject.timestamp = {name: "timestamp", value: attribute[attr], type: "DateTime"}
      metadataObject.push({name: "timestamp", value: attribute[attr], type: "DateTime"})

    } else if (attr.toUpperCase() == "unitCode".toUpperCase()) {
      //metadataObject.unitCode = {name: "unitCode", value: attribute[attr], type: libWrapperUtils.obtain_NGSIAttributeValue(typeof attribute[attr])}
      metadataObject.push({name: "unitCode", value: attribute[attr], type: libWrapperUtils.obtain_NGSIAttributeValue(typeof attribute[attr])})

    //} else if (attr.toUpperCase() == "@context".toUpperCase()) {
    //  attrObject.type = "StructuredValue"
    //  attrObject.value = attribute.value

    } else if (attr.toUpperCase() == "entityType".toUpperCase()) {
      //metadataObject.entityType = {name: "entityType", value: attribute[attr], type: libWrapperUtils.obtain_NGSIAttributeValue(typeof attribute[attr])}
      metadataObject.push({name: "entityType", value: attribute[attr], type: libWrapperUtils.obtain_NGSIAttributeValue(typeof attribute[attr])})

    } else if (attr != "value" && attr != "object") {
      var matchKeyResponse = []

      matchKeyResponse = match_key_v1_NGSILD(attr,attribute[attr],"",metadataObject,key,ldReversedContext) 

      if (matchKeyResponse.length==2) {
        /*
        var objectVar = {}
        objectVar = matchKeyResponse[1] 
        objectVar.name = attr
        objectVar.type = libWrapperUtils.obtain_NGSIAttributeValue(typeof objectVar.value)
        //metadataObject[matchKeyResponse[0]] = objectVar
        metadataObject.push(objectVar)
        */

        metadataObject.push(matchKeyResponse[1])
      }
    }
  }

  if (parentKey == "" && metadataObject.length > 0)   {
    attrObject.metadatas = metadataObject
  }
  return [key, attrObject]
  
}

module.exports.fromNGSILDtoNGSI = fromNGSILDtoNGSI; 
