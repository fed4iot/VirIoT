
#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

#!/bin/bash

mosquitto_pub -h localhost -p 1883 -t vThing/thingVisorID_Actuator/Device/data_in -q 0 -m '{"meta":{"vSiloID":"tenantID_orionv2"},"data":[{"id":"urn:ngsi-ld:Device:001","type":"Device","configuration":{"type":"Property","value":{"cmd-value": {"num": "1","value": "10002","mul": "1"},"cmd-qos":"0","cmd-id":"4","cmd-nuri":["viriot:vSilo/tenantID_orionv2/data_in"]}}}]}';