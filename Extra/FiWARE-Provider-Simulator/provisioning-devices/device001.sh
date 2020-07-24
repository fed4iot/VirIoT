#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

curl -iX POST \
    'http://localhost:4041/iot/devices' \
    -H 'Content-Type: application/json' \
    -H 'fiware-service: demo1' \
    -H 'fiware-servicepath: /demo' \
    -d '{
        "devices": [
            {
                "device_id":   "device001",
                "entity_name": "urn:ngsi-ld:Device:001",
                "entity_type": "Device",
                "protocol": "MQTT_JSON",
                "transport": "MQTT",
                "attributes": [
                    { "object_id": "s", "name": "isOpen", "type": "boolean" }
                ],
                "commands": [
                  { "name": "start", "type": "command" },
                  { "name": "stop", "type": "command" }
                ],
                "static_attributes": [
                  {"name":"name", "type": "Text","value": "Device:001 provision"}
                ]
            }
        ]
    }
';