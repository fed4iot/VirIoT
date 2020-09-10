# Weather ThingVisor

This ThingVisor fetches  data from [OpenWeatherMap](openweathermap.org) and creates different vThings for a set of configurable cities. For each city, three vThings are created that report temperature, humidity and pressure

# How To RUN

## Local Docker deployment

Use the VirIoT CLI and run the following command in case of Rome and Tokyo, with a refresh rate equal to 10 seconds  

```bash
f4i.py add-thingvisor -i fed4iot/v-weather-tv:2.2 -n weathertv -d "Weather ThingVisor fetching data from open weather" -p "{'cities':['Rome', 'Tokyo'], 'rate':'10'}"
```

## Kubernetes deployment

Use the VirIoT CLI and run the following command in case of Rome and Tokyo, with a refresh rate equal to 10 seconds.
The `-z` argument is optional, it can be used to specify the deployment zone. If not specified,   
Kubernetes will randomly choose a node in the default zone.

```bash
python3 f4i.py add-thingvisor -c http://[k8s_node_ip]:[NodePort] -n weathertv -d "Weather ThingVisor fetching data from open weather" -p '{"cities":["Rome", "Tokyo"], "rate":10}' -y "../yaml/thingVisor-weather.yaml" -z Japan  
```


# NGSI-LD data model

Each vThing of a city (e.g. Tokyo) is internally represented by the following entities

## Thermometer vThingID: "weathertv/Tokyo_temp"

```json
{
    "id": "urn:ngsi-ld:Tokyo:temp",
    "type": "temperature",
    "thermometer": {"type": "Property", "value": 288.19}
}
```

## Hygrometer vThingID : "weathertv/Tokyo_humidity"

```json
{
    "id": "urn:ngsi-ld:Tokyo:humidity",
    "type": "humidity",
    "hygrometer": {"type": "Property", "value": 66}
}
```

## Barometer vThingID : "weathertv/Tokyo_pressure"

```json
{
    "id": "urn:ngsi-ld:Tokyo:pressure",
    "type": "pressure",
    "barometer": {"type": "Property", "value": 1005}
}
```
