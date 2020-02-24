example of params to use with f4i.py add-thingvisor :
-p "{'CSEurl':'http://172.17.0.3:7579','cntArns':['Sensor1/temp'],'vThingName':'Sensor1','vThingDescription':'OneM2M data from sensor1','origin':'Superman'}"

*EGM test*
-p "{'CSEurl':'https://fed4iot.eglobalmark.com','origin':'Superman','cntArns':['Abbas123456/humidity/value','Abbas123456/temperature/value'],'vThingName':'EGM-Abbas123456','vThingDescription':'OneM2M  data from EGM Abbass sensor'}"

CLI for EGM

python3 f4i.py add-thingvisor -c http://127.0.0.1:8090 -i fed4iot/onem2m-multisub-tv:2.2 -n EGM-Abbass-multiple -d "OneM2M data from EGM Abbass sensor (temperature and humidity" -p "{'CSEurl':'https://fed4iot.eglobalmark.com','origin':'Superman', 'poaPort':'8089','cntArns':['Abbas123456/humidity/value','Abbas123456/temperature/value'],'poaIP':'127.0.0.1','vThingName':'EGM-Abbas123456','vThingDescription':'OneM2M data from multiple EGM Abbass sensors'}"
