/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

"use strict";

function format_value(nodeType, value, entityType, valueType)  {
  //
  if (nodeType.toUpperCase() == "Relationship".toUpperCase()) {
    return format_uri(entityType, value)
  }

  //This code looks deprecated??
  //Example:
  //
  //https://github.com/FIWARE/NGSI-LD_Experimental     
  //"observedAt": "2018-05-04T10:18:16Z"
  //Response: Error: "title": "Attribute must be a JSON object",
  //
  //or
  //
  //https://github.com/Fiware/dataModels/blob/master/tools/normalized2LD.py
  //"observedAt": {    
  //      "type": "Property",
  //      "value": {
  //        "@type": "Datetime",
  //        "@value": "2018-05-04T10:18:16Z"
  //      }
  //  },
  //Response: OK.
  //
  //or
  //
  //https://github.com/GSMADeveloper/NGSI-LD-Entities/blob/master/definitions/Water-Quality-Observed.md
  //https://github.com/GSMADeveloper/NGSI-LD-Entities/blob/master/definitions/Smart-Meter-Observed.md
  //https://github.com/GSMADeveloper/NGSI-LD-Entities/blob/master/definitions/Market-Price-Observed.md
  //"observedAt": {
  //      "type": "Property",
  //      "value": "2018-05-04T10:18:16Z"
  //  },
  //Response: OK.
  if (valueType.length > 0) {
    return {"@value": value, "@type": valueType}
    //return {"value": value, "type": valueType}
  }

  return value
}


// TODO: Refine this to a proper regular expression as per attribute name rules
function AnyProp(ocbAttr) {
  var re = /(.+)/

  //return ocbAttr.replace(re, '$1')
  return re.test(ocbAttr)
}

// Reference type to recognize relationships
function ReferenceAttr(ocbAttr) {
  var re = /ref(.+)/

  //return ocbAttr.replace(re, '$1')
  return re.test(ocbAttr)
}

//Obtain id (NGSI-LD)
//Entry: Params with NGSIv2 type and id values.
//Return: String with NGSI-LD id value.
function format_uri(ocbType, ocbId) {
    
  var calcType = ocbType || "Thing"
  var idLD

  var resultArray = []

  resultArray = UrnPattern(ocbId)

  if (resultArray.length==2) {
    if (resultArray[0].toUpperCase() == "Thing".toUpperCase()) {
      idLD = toURN(calcType, ocbId)
    } else {
      idLD = ocbId
    }
  }
  else {
    idLD = toURN(calcType, ocbId)
  }

  return  idLD
}


//Verify if NGSIv2 id value has NGSI-LD id syntax requirements.
//Entry: Param with NGSIv2 id value.
//Return: Array with two possible elements (type and id).
function UrnPattern(ocbId) {
  //If entity ID has ":" an error will occur.

  //var re = /urn:ngsi-ld:(.+):(.+)/
  //return ocbId.replace(re, '$1#$2').split('#')

  //If entity ID has ":" an error will not occur, but if entity type has ":" an error will occur.
  var pattern = /\s*:\s*/;
  var ocbIdList = ocbId.split(pattern)
  
  var result = []

  if (ocbIdList[0]=='urn' && ocbIdList[1]=='ngsi-ld') {
    if (ocbIdList.length>2) {
      result.push(ocbIdList[2])
      if (ocbIdList.length>3) {
        var idValue = ""
        for(var i=3; i< ocbIdList.length; i++){
          if (idValue == "") {
            idValue = ocbIdList[i]
          } else {
            idValue = idValue + ":" + ocbIdList[i]
          }
        }
        result.push(idValue)  
      }
    }
  }

  return result
}

//Build NGSI-LD id value.
//Entry: Params with NGSIv2 type and id values.
//Return: String with NGSI-LD id value.
function toURN(ocbType, ocbId) {
  return  "urn:ngsi-ld:" + ocbType + ":" + ocbId
}

function obtain_NGSIAttributeValue(typeofAttribute) {

  if (typeofAttribute.toUpperCase()=="String".toLocaleUpperCase()) {
    return "Text"
  } else if (typeofAttribute.toUpperCase()=="number".toLocaleUpperCase())
    return "Number"
  else {
    return typeofAttribute
  }
}

module.exports.format_value = format_value; 
module.exports.AnyProp = AnyProp; 
module.exports.ReferenceAttr = ReferenceAttr; 
module.exports.format_uri = format_uri; 
module.exports.UrnPattern = UrnPattern; 
module.exports.obtain_NGSIAttributeValue = obtain_NGSIAttributeValue; 
