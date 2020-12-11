# ThingVisor Relay Test

This test uses the Relay ThingVisor to measure end-to-end latency between a producer and a consumer whose data items cross the VirIoT system like this: Producer -> ThingVisor -> MQTT -> vSilo (controller + Broker) -> Consumer.

## Producer

`producer.py` sends JSON objects at a given rate (e.g. 1 msg/s) to the Relay ThingVisor, specifically to a dedicated /notify REST endpoint exposed by the Relay ThingVisor Url (e.g.: http://vm1:32303/notify, please check the current port and IP the Relay ThingVisor is using, by inspecting your Docker or Kubernets deployment of VirIoT).

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

`consumerMQTT.py` is a consumer that connects to a MQTT vSilo identified by a server IP address (e.g. 172.17.0.2) and port (e.g. 1883) of the MQTT broker running inside the vSilo. It receives data items produced by `producer.py` on the vThing (e.g. timestamp) of a Relay ThingVisor (e.g. relay-tv) and prints one-way delay statistics (producer and consumer clocks should be nearly synchronized). 

```bash
python3 consumerMQTT.py -s 172.17.0.2 -p 1883 -v relay-tv/timestamp
```
The -v option is used to tell the consumer what is the ThingVisor/vThing (-v relay-tv/timestamp) of the data itemes produced by the producer.py + Relay ThingVisor.

Note: preliminary steps are: to add the MQTT flavour, create the vSilo, and add the vThing the vSilo. For instance:

```bash
python3 f4i.py add-flavour -y ../yaml/flavours-raw-mqtt-actuator.yaml -f Raw-base-actuator-f -s Raw -d "silo with a MQTT broker"
python3 f4i.py create-vsilo -f Raw-base-actuator-f -t tenant1 -s Silo1
python3 f4i.py add-vthing -t tenant1 -s Silo1 -v relay-tv/timestamp
```

## oneM2M Consumer

`consumeroneM2M.py` is a consumer which connects to a oneM2M Mobius vSilo identified by its server IP (e.g. 172.17.0.2), HTTP port (e.g. 7579) and MQTT port (e.g. 1883). It receives data items produced by `producer.py` through the vThing (e.g. timestamp) of a Relay ThingVisor (e.g. relay-tv). These data items are inserted in a oneM2M container and from the oneM2M container they are pushed to `consumeroneM2M.py`

The consumer can connect the Mobius broker either through HTTP or MQTT. In the case of HTTP, the consumer should be reachable through a public URL (notification URI, nuri), where it is contacted by the Mobius broker when a data item arrives in the oneM2M container. The nuri is `http://consumerIP:consumerPort/notify`, where `consumerPort` can be selected by the user. In the case of MQTT, no notification URI is required. Possible examples are.

The -v option is used to tell the consumer what is the ThingVisor/vThing (-v relay-tv/timestamp) of the data itemes produced by the producer.py + Relay ThingVisor.

```bash
python3 consumerOneM2M.py -s 172.17.0.2 -p 7579 -pm 1883 -m HTTP -nuri http://172.17.0.1:5000/notify -v relay-tv/timestamp
```

Note: preliminary steps are: to add the oneM2M flavour, create the vSilo, and add the vThing the vSilo. For instance:

```bash
python3 f4i.py add-flavour -f Mobius-base-actuator-f -s Mobius -d "silo with a oneM2M Mobius broker" -y "../yaml/flavours-mobius-pub-sub-actuator.yaml"
python3 f4i.py create-vsilo -f Mobius-base-actuator-f -t tenant1 -s Silo3
python3 f4i.py add-vthing -t tenant1 -s Silo3 -v relay-tv/timestamp
```

 ## Mobius2 Consumer
 
 `consumerMobius2.py` is a consumer which connects to a oneM2M Mobius2 vSilo identified by its server IP (e.g. 172.17.0.2), HTTP port (e.g. 7579) and MQTT port (e.g. 1883). It receives data items produced by `producer.py` through the vThing (e.g. timestamp) of a Relay ThingVisor (e.g. relay-tv). These data items are inserted in a oneM2M container and from the oneM2M container they are pushed to `consumerMobius2.py`

The consumer can connect the Mobius2 broker either through HTTP or MQTT. In the case of HTTP, the consumer should be reachable through a public URL (notification URI, nuri), where it is contacted by the Mobius broker when a data item arrives in the oneM2M container. The nuri is `http://consumerIP:consumerPort/notify`, where `consumerPort` can be selected by the user. In the case of MQTT, no notification URI is required. Possible examples are.

The -v option is used to tell the consumer what is the ThingVisor/vThing (-v relay-tv/timestamp) of the data itemes produced by the producer.py + Relay ThingVisor.

```bash
python3 consumerMobius2.py -s 172.17.0.2 -p 7579 -pm 1883 -m HTTP -nuri http://172.17.0.1:5000/notify -v relay-tv/timestamp
```

Note: preliminary steps are: to add the oneM2M flavour with Mobius2 IoT Broker, create the vSilo, and add the vThing the vSilo. For instance:

```bash
python3 f4i.py add-flavour -f Mobius2-base-actuator-f -s Mobius -d "silo with a oneM2M Mobius2 broker" -y "../yaml/flavours-mobius2-pub-sub-actuator.yaml"
python3 f4i.py create-vsilo -f Mobius2-base-actuator-f -t tenant1 -s Silo1
python3 f4i.py add-vthing -t tenant1 -s Silo1 -v relay-tv/timestamp

## NGSI Consumer
`consumerNGSI.py` is a consumer which connects to an Orion vSilo identified by its server IP (e.g. 172.17.0.2) and port (e.g. 1026). It receives data items produced by `producer.py` through the vThing (e.g. timestamp) of a Relay ThingVisor (e.g. relay-tv). These data items are inserted in an Orion Context Broker inside orion vSilo container and from this container they are pushed to `consumerNGSI.py`

The consumer has to be reachable through a public URL (notification URI, nuri), where it is contacted by the Orion Broker when a data item arrives. The nuri is `http://consumerIP:consumerPort/notify`, where `consumerPort` can be freely selected by the user and consumerIP is a reachable IP address of the machine where consumerNGSI.py is going to run.

The -v and -t options are used to tell the consumer what are the ThingVisor/vThing (-v relay-tv/timestamp) and type (-t timestamp) of the data itemes produced by the producer.py + Relay ThingVisor.

```bash
python3 consumerNGSI.py -s 172.17.0.2 -p 1026 -nuri http://172.17.0.1:5001/notify -v relay-tv/timestamp -t timestamp
```
Note: preliminary steps are: to add the Orion flavour, create the vSilo, and add the vThing the vSilo. For instance:

```bash
python3 f4i.py add-flavour -f orion-f -s "" -d "silo with a FIWARE Orion Context Broker" -y "../yaml/flavours-orion.yaml"
python3 f4i.py create-vsilo -f orion-f -t tenant1 -s Silo1
python3 f4i.py add-vthing -t tenant1 -s Silo1 -v relay-tv/timestamp
```


## NGSI-LD Consumer
`consumerNGSILD.py` is a consumer which connects to an NGSI-LD vSilo identified by its server IP (e.g. 172.17.0.2) and port (e.g. 1026 if the Broker running inside the vSilo is OrionLD, 9090 if Scorpio, 8090 if Stellio). It receives data items produced by `producer.py` through the vThing (e.g. timestamp) of a Relay ThingVisor (e.g. relay-tv). These data items are inserted in the Context Broker inside the NGSI-LD vSilo container, and from this container they are pushed to `consumerNGSILD.py`

The consumer has to be reachable through a public URL (notification URI, nuri), where it is notified by the Context Broker when a data item arrives in the broker. The nuri is `http://consumerIP:consumerPort/notify`, where `consumerPort` can be freely selected by the user and consumerIP is a reachable IP address of the machine where consumerNGSILD.py is going to run.

The -v and -t options are used to tell the consumer what are the ThingVisor/vThing (-v relay-tv/timestamp) and type (-t timestamp) of the data itemes produced by the producer.py + Relay ThingVisor.

```bash
python3 consumerNGSILD.py -s 172.17.0.2 -p 1026 -nuri http://172.17.0.1:5001/notify -v relay-tv/timestamp -t timestamp
```

Note: preliminary steps are: to add the NGSI-LD flavour, create the vSilo, and add the vThing the vSilo. For instance:

```bash
python3 f4i.py add-flavour -f ngsild-f -s '{"brokerport":1026}' -d "silo with a OrionLD NGSI-LD Context Broker" -y "../yaml/flavours-ngsild-orionld-multicontainer.yaml"
python3 f4i.py create-vsilo -f ngsild-f -t tenant1 -s Silo1
python3 f4i.py add-vthing -t tenant1 -s Silo1 -v relay-tv/timestamp
```

## Big Buck Bunny fake MPEG DASH player
`bbbPlayer.py` is a fake player for the Big Buck Bunny MPEG dash video stream that is provided by a Relay-TV with [http-sidecard](../../../../Thingvisors/DockerThingVisor/ThingVisor_http_sidecar/README.md and with the internal webserver in [Extra](../../../../Extra/webserver/README.md) folder.  
To deploy this kind of ThingVisor the following command can be used

```bash
f4i.py add-thingvisor -y ../yaml/thingVisor-relay-http-webserver.yaml -n relay-tv -d "relay thingvisor with http" -p "{'vThingName':'timestamp','vThingType':'timestamp'}" 
f4i.py set-vthing-endpoint -v relay-tv/timestamp -e http://127.0.0.1:8081 
```

The player issues HTTP GETS to a vSilo which should have the  [http-sidecar](../../../../Flavours/http-sidecar-flavour/README.md) too. To deploy this kind of vSilo (e.g. MQTT based) the following command can be used


```bash
python3 f4i.py add-flavour -y ../yaml/flavours-raw-mqtt-actuator-http.yaml -f Raw-base-actuator-f-h -s Raw -d "silo with a MQTT broker and HTTP services"
python3 f4i.py create-vsilo -f Raw-base-actuator-f-h -t tenant1 -s Silo1
python3 f4i.py add-vthing -t tenant1 -s Silo1 -v relay-tv/timestamp
```

The  `bbbPlayer.py` script emulates live streaming in the sense that it requests MPEG DASH segments according to the segment duration (4s) and taking into consideration the start time of the video that should be passed as parameters (`-u`).

The following command runs a player that issues HTTP GETs to a vSilo (with http-sidecar runing on port 80) whose IP address is 172.17.0.2. The player gets MPEG DAS bbb segments offered by a vThing whose id is `relay-tv/timestamp` and the video start time is  1604917348 (Unix Epoch Time)

```bash
python3 bbbPlayer.py -s 172.17.0.2 -p 80 -v relay-tv/timestamp -u 1604917348
```

