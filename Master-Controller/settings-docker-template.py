# public IP address through the which it is possible to access thingvisors, database, vSilos, etc.
default_gateway_IP = ""

# MQTT settings (possibly two brokers one for control and another one for control messages)
MQTT_data_broker_IP = "172.17.0.1"
MQTT_data_broker_port = 1883
MQTT_control_broker_IP = "172.17.0.1"
MQTT_control_broker_port = 1883

# Mongo settings
# mongoDb port
# mongo_IP is required but can be empty !!
mongo_IP = ""
mongo_port = 27017

container_manager = "DOCKER"

#Authentication settings
JWT_SECRET_KEY = "UYG867ti867f(/&$SWRUco)(YPO/T"  # secret key used to encrypt password
