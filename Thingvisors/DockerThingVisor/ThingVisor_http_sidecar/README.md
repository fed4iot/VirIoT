# ThingVisor HTTP Sidecar

This sidecar container can be inserted within the Kubernetes Pod of a ThingVisor to provide HTTP services on port 80. For each vThing of the ThingVisor, the sidecar can connect the uri `tv-svc-ip:80/vThingName` to an external HTTP endpoint. The endpoint can be configured through the Master-Controller REST resource `setVThingEndpoint` or the CLI `set-vthing-endpoint` command

## How To Run

### Local Docker deployment

Not working on Docker because it uses the POD abstraction of Kubernetes 

### Kubernetes deployment

Update the yaml file of the ThingVisor by adding the sidecar container to the Deployment section, e.g.

```yaml
    - name: f4i-http-sidecar
      image: fed4iot/http-sidecar-tv
      ports:
      - containerPort: 5001
```

Update the yaml file of the ThingVisor by adding the sidecar container port 80 to the Service section, e.g.

```yaml
  - port: 80
    targetPort: 5001
    name: http
```

See the [thingVisor-relay-http.yaml](../../../yaml/thingVisor-relay-http.yaml) as an example of the YAML of relay ThingVisor with http sidecar.

Use the VirIoT CLI and run the following command to run the ThingVisor example.  The name of the ThingVisor (relay-tv), the vThingName (timestamp) and the vThingType (timestamp) can be customized.

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -y ../yaml/thingVisor-relay-http.yaml -n relay-tv -d "relay thingvisor with http" -p "{'vThingName':'timestamp','vThingType':'timestamp'}"
```

Add an endpoint to the `timestamp` vThing through the CLI
```bash
python3 f4i.py set-vthing-endpoint -c http://[k8s_node_ip]:[NodePort] -v relay-tv/timestamp -e http://ipv4.download.thinkbroadband.com
```

Test with curl, where 'tv-service-ip' is the IP address (cluster IP, or NodePort) of the ThingVisor
```bash
curl tv-service-ip/timestamp/20MB.zip
```

