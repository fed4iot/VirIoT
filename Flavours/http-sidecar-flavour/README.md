# HTTP Sidecar for flavour

This sidecar container can be inserted within the Kubernetes Pod of a vSilo Flavour to provide HTTP services on port 80. For each vThing of the vSilo, the sidecar connect the uri `silo-service-ip:80/vstream/ThingVisorID/vThingName` to the external HTTP endpoint bound with the vThing by the ThingVisor.

## How To Run

### Local Docker deployment

Not working on Docker because it uses the POD abstraction of Kubernetes 

### Kubernetes deployment

Update the yaml file of the Flavour by adding the sidecar container to the Deployment section, e.g.

```yaml
    - name: http-sidecar-f
      image: fed4iot/http-sidecar-flavour:latest
      ports:
      - containerPort: 5001
```

Update the yaml file of the Flavour by adding the sidecar container port 80 to the Service section, e.g.

```yaml
  - port: 80
    targetPort: 5001
    name: http
```

See the [flavours-raw-mqtt-actuator-http.yaml](../../yaml/flavours-raw-mqtt-actuator-http.yaml) as an example of the YAML of mqtt flavour with http sidecar.

Use the VirIoT CLI and run the following command to run the Flavour example.  The example assume that the relay thingVisor with http is running, see [here](../../Thingvisors/DockerThingVisor/ThingVisor_http_sidecar/README.md).

```bash
python3 f4i.py add-flavour -f Raw-base-actuator-f -s Raw -d "silo with a MQTT broker and HTTP service" -y ../yaml/flavours-raw-mqtt-actuator-http.yaml 
python3 f4i.py create-vsilo -f Raw-base-actuator-f -t tenant1 -s Silo1
python3 f4i.py add-vthing -v relay-tv/timestamp
```

Test with curl, where 'vsilo-service-ip' is the IP address (cluster IP, or NodePort) of the ThingVisor
```bash
curl vsilo-service-ip/vstream/relay-tv/timestamp/20MB.zip
```