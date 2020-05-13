/*

Copyright Odin Solutions S.L. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

*/

'use strict'

const express = require('express')

//Para poder parsear las peticiones.
const bodyParser = require('body-parser')

const app = express()

const api = require('./routes')

//Cada vez que se realice una petición HTTP pasará por las capas definidas.
//app.use(bodyParser.urlencoded({extended: false}))

//Para poder admitir peticiones con body en formato JSON.
//app.use(bodyParser.json())

app.use(bodyParser.json({limit: '50mb'}));
app.use(bodyParser.urlencoded({limit: '50mb', extended: true, parameterLimit: 1000000}));


app.use('/',api)

module.exports = app
