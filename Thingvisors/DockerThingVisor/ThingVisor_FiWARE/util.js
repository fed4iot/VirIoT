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

function ISODateString(d) {
    function pad(n) {return n<10 ? '0'+n : n}
    return d.getUTCFullYear()+'-'
         + pad(d.getUTCMonth()+1)+'-'
         + pad(d.getUTCDate())+'T'
         + pad(d.getUTCHours())+':'
         + pad(d.getUTCMinutes())+':'
         + pad(d.getUTCSeconds())+'Z'
}

module.exports.unixTime = unixTime; 
module.exports.ISODateString = ISODateString;
