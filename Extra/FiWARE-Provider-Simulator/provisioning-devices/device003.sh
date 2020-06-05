#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

curl -iX POST \
    'http://localhost:4041/iot/devices' \
    -H 'Content-Type: application/json' \
    -H 'fiware-service: demo2' \
    -H 'fiware-servicepath: /demo' \
    -d '{
        "devices": [
            {
                "device_id":   "device003",
                "entity_name": "urn:ngsi-ld:Device:003",
                "entity_type": "Device",
                "protocol": "MQTT_JSON",
                "transport": "MQTT",
                "attributes": [
                    { "object_id": "c", "name": "count", "type": "number" },
                    {  "object_id": "m", "name": "isIncreasing", "type": "boolean" },
                    {  "object_id": "s", "name": "isRunning", "type": "boolean" }
                ],
                "commands": [
                  { "name": "reset", "type": "command" },
                  { "name": "increasing", "type": "command" },
                  { "name": "start", "type": "command" },
                  { "name": "stop", "type": "command" },
                  { "name": "setCounter", "type": "command" }
                ],
                "static_attributes": [
                  {"name":"name", "type": "Text","value": "Device:003 provision"}
                ]
            }
        ]
    }
';