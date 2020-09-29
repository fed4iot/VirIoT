# ThingVisor Relay Test

This test uses the Relay ThingVisor to measure end-to-end latency between a producer and a consumer whose data items cross VirIoT system.

## Producer

`producer.py` send JSON objects at a given rate (e.g. 1 msg/s) to a Relay ThingVisor, identified by a ThingVisorUrl (e.g.: http://vm1:32303/notify).

```bash
python3 producer.py -t http://vm1:32303/notify -r 1
```

The JSON objects schema is the following:

```json
{
    "timestamp": <current time millisecond>, 
    "sqn": <counter>}
}
```

## MQTT Consumer

`consumerMQTT.py` is a consumer that connects to a MQTT vSilo identified by a server IP address (e.g. 172.17.0.2) and port (e.g. 1883) of the MQTT broker of the vSilo. It receives data items produced by `producer.py` on the vThing (e.g. timestamp) of a Relay ThingVisor (e.g. RelayTV) and prints one-way delay statistics (producer and consumer clocks should be nearly synchronized). 

```bash
python3 consumerMQTT.py -s 172.17.0.2 -p 1883 -v relayTV/timestamp
```

Note: preliminary steps are: to add the MQTT flavour, create the vSilo, and add the vThing the vSilo. For instance:

```bash
python3 f4i.py add-flavour -y ../yaml/flavours-raw-mqtt-actuator.yaml -f Raw-base-actuator-f -s Raw -d "silo with a MQTT broker"
python3 f4i.py create-vsilo -f Raw-base-actuator-f -t tenant1 -s Silo1
python3 f4i.py add-vthing -t tenant1 -s Silo1 -v relayTV/timestamp
```

## oneM2M Consumer

`consumeroneM2M.py` is a consumer which connects to a oneM2M Mobius vSilo identified by its server IP (e.g. 172.17.0.2), HTTP port (e.g. 7579) and MQTT port (e.g. 1883). It receives data item produced by `producer.py` through the vThing (e.g. timestamp) of a Relay ThingVisor (e.g. RelayTV). These data items are inserted in a oneM2M container and from the oneM2M container they are pushed to `consumeroneM2M.py`

The consumer can connect the Mobius broker either through HTTP or MQTT. In the case of HTTP, the consumer should be reachable through a public URL (notification URI, nuri), where it is contacted by the Mobius broker when a data item arrives in the oneM2M container. The nuri is `http://consumerIP:consumerPort/notify`, where `consumerPort` can be selected by the user. In the case of MQTT, no notification URI is required. Possible examples are.

```bash
python3 consumerOneM2M.py -s 172.17.0.2 -p 7579 -pm 1883 -m HTTP -nuri http://172.17.0.1:5000/notify -v relayTV/timestamp
```

Note: preliminary steps are: to add the oneM2M flavour, create the vSilo, and add the vThing the vSilo. For instance:

```bash
python3 f4i.py add-flavour -f Mobius-base-actuator-f -s Mobius -d "silo with a oneM2M Mobius broker" -y "../yaml/flavours-mobius-pub-sub-actuator.yaml"
python3 f4i.py create-vsilo -f Mobius-base-actuator-f -t tenant1 -s Silo3
python3 f4i.py add-vthing -t tenant1 -s Silo3 -v relayTV/timestamp
```

## NGSI Consumer

`consumerNGSI.py` is a consumer which connects to an Orion vSilo identified by its server IP (e.g. 172.17.0.2) and port (e.g. 1026). It receives data item produced by `producer.py` through the vThing (e.g. timestamp) of a Relay ThingVisor (e.g. RelayTV). These data items are inserted in an Orion Context Broker inside orion vSilo container and from this container they are pushed to `consumerNGSI.py`

The consumer should be reachable through a public URL (notification URI, nuri), where it is contacted by the Orion Context broker when a data item arrives in the Orion container. The nuri is `http://consumerIP:consumerPort/notify`, where `consumerPort` can be selected by the user.

```bash
python3 consumerNGSI.py -s 172.17.0.2 -p 1026 -nuri http://172.17.0.1:5001/notify -v relayTV/timestamp -t timestamp
```

Note: preliminary steps are: to add the Orion flavour, create the vSilo, and add the vThing the vSilo. For instance:

```bash
python3 f4i.py add-flavour -f orion-f -s "" -d "silo with a FIWARE Orion Context Broker" -y "../yaml/flavours-orion.yaml"
python3 f4i.py create-vsilo -f orion-f -t tenant1 -s Silo1
python3 f4i.py add-vthing -t tenant1 -s Silo1 -v relayTV/timestamp
```