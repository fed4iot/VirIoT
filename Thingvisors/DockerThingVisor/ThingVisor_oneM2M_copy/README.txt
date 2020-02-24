example of params to use with f4i.py add-thingvisor :
-p "{'CSEurl':'http://172.17.0.3:7579','cntArn':'Sensor1/temp','vThingName':'Sensor1','vThingDescription':'OneM2M data from sensor1','origin':'Superman'}"

*EGM test*
-p "{'CSEurl':'https://fed4iot.eglobalmark.com','origin':'Superman','cntArn':'Abbas123456/humidity/value','vThingName':'EGM-Abbas123456-h','vThingDescription':'OneM2M humidity data from EGM Abbass sensor'}"

CLI for EGM

python3 f4i.py add-thingvisor -c http://127.0.0.1:8090 -i fed4iot/onem2m-tv:2.2 -n EGM-Abbass -d "OneM2M data from EGM Abbass sensor" -p "{'CSEurl':'https://fed4iot.eglobalmark.com','origin':'Superman', 'poaPort':'8089','cntArn':'Abbas123456/humidity/value','poaIP':'127.0.0.1','vThingName':'EGM-Abbas123456-humidity','vThingDescription':'OneM2M humidity data from EGM Abbass sensor'}"
