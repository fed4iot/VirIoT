# Neutral-Format

The *neutral-format* is the JSON schema used by the messages internally exchanged among VirIoT entities both to transport data and control information.

These messages are tranferred as MQTT payload on specific data and control topics (see D4.1 fig.6)  

## Neutral-format for data messages

```json
{
    "data":"<NGSI-LD Entity Array>",
    "meta": {"vThingID":"<vThingID>", "<otherMetadata>":"<value>"}
}
```

where `NGSI-LD Entity Array` is an array of NGSI-LD entities.

For instance, the ThingVisor [HelloWorldTV](../Thingvisors/DockerThingVisor/ThingVisor_HelloWorld) handles a vThing named `HelloWorldTV/hello`. This vThing produces data items related to two NGSI-LD entities, namely `urn:ngsi-ld:HelloSensor1` and `urn:ngsi-ld:HelloSensor2`. An example of a neutra-format message used by the ThingVisor to send data update to connected vSilos is:

```json
{
    "data":
        [
            {
                "id": "urn:ngsi-ld:HelloSensor1",
                "type": "my-counter",
                "counter": {"type": "Property", "value": 497}
            },
            {
                "id": "urn:ngsi-ld:HelloSensor2",
                "type": "my-double-counter",
                "double-counter": {"type": "Property", "value": 994}
            }
        ],
    "meta": {"vThingID": "HelloWorldTV/hello"}
}
```

## Neutral-format for command messages

Command messages transport control information (see D3.1 Figure 3).
The neutral format includes the name of the command in the `command` key and other key/value couples that contain the arguments of the command and that depend on the type of command.

```json
{
    "command":"<Command name>",
    "<arg1-key>": "<arg1-value>",
    
    "<arg#n-key>": "<arg#n-value>"
}
```

An example of a neutra-format message used by the ThingVisor `HelloWorldTV` to announce a new vThing `HelloWorldTV/hello` to the Master-Controller is :

```json
{
    "command": "createVThing",
    "thingVisorID": "HelloWorldTV",
    "vThing":
        {
                "label": "helloWorld",
                "id": "HelloWorldTV/hello",
                "description": "hello world virtual thing"
        }
}
```
