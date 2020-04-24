# Description
This ThingVisor fetchs  data from <openweathermap.org> and creates different vThings for a set of configurable cities. For each city, three vThings are created reporting temperature, humidity and pressure

# How To RUN (local Docker deployment)
Use the VirIoT CLI and run the follwiong command in case of Rome and Tokyo, with a refresh rate equal to 10 seconds  

```bash
f4i.py add-thingvisor -c http://127.0.0.1:8090 -i fed4iot/v-weather-tv:2.2 -n WeatherTV -d "Weather ThingVisor fetching data from open weather" -p "{'cities':['Rome', 'Tokyo'], 'rate':'10'}"
```

# NGSI-LD schema 
Eacy vThing of a city (e.g. Tokyo) is internally represented by the following entities

## Thermometer vThingID: "WeatherTV/Tokyo_temp"

```json
{
    "id": "urn:ngsi-ld:Tokyo:temp",
    "type": "temperature",
    "thermometer": {"type": "Property", "value": 288.19}
}
```

## Hygrometer vThingID : "WeatherTV/Tokyo_humidity"

```json
{
    "id": "urn:ngsi-ld:Tokyo:humidity",
    "type": "humidity",
    "hygrometer": {"type": "Property", "value": 66}
}
```

## Barometer vThingID : "WeatherTV/Tokyo_pressure"

```json
{
    "id": "urn:ngsi-ld:Tokyo:pressure",
    "type": "pressure",
    "barometer": {"type": "Property", "value": 1005}
}
```
