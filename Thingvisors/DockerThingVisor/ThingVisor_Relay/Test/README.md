# ThingVisor Relay Test

This test uses the Relay ThingVisor to measure end-to-end latency between a producer and a consumer whode data items cross VirIoT system.

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

`consumerMQTT.py` is a consumer which connects to a MQTT vSilo identified by a server IP address (e.g. 172.17.0.1) and port (e.g. 30031) of the MQTT broker of the vSilo. It receives data item produced by `producer.py` on the vThing (e.g. timestamp) of a Relay ThingVisor (e.g. RelayTV) and prints one-way delay statistics (producer and consumer clocks shoud be nearly syncronized). 

Note: it is necessary to preliminary add the vThing the MQTT vSilo. 

```bash
python3 consumerMQTT.py -s 172.17.0.1 -p 30031 -v relayTV/timestamp
```

## oneM2M Consumer

`consumeroneM2M.py` is a consumer which connects to a oneM2M Mobius vSilo identified by its server URL (e.g. 172.17.0.1:30035). It receives data item produced by `producer.py` through the vThing (e.g. timestamp) of a Relay ThingVisor (e.g. RelayTV). These data items are inserted in a oneM2M container with an Absolute Resource Name (e.g. relayTV:timestamp/urn:ngsi-ld:relayTV:timestamp/msg).

The consumer can connect the Mobius broker either through HTTP or MQTT. In case of HTTP, the consumer shoud be reachable through a public URL (notification URI, nuri), where it is contacted by the Mobius broker when a data item arrives in the oneM2M container. The nuri is `http://consumerIP:5000/notify`. In case of MQTT, no notificatin URI is rquired.

Note: it is necessary to preliminary add the vThing the MQTT vSilo.

```bash
python3 consumeroneM2M.py -su <Mobius vSilo Server URL> -cnt <Absolute Resource Name of oneM2M container> -m HTTP -nuri <http://consumerIP:5000/notify>
```

```bash
python3 consumeroneM2M.py -su <Mobius vSilo Server URL> -cnt <Absolute Resource Name of oneM2M container> -m MQTT 
```
