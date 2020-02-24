# public IP address through which it is possible to access the default zone of k8s cluster
default_gateway_IP = ""

# MQTT settings (possibly two brokers one for control and another one for control messages)
MQTT_data_broker_IP = "vernemq-mqtt.default.svc.cluster.local"
MQTT_data_broker_port = 1883
MQTT_control_broker_svc_name = "vernemq-mqtt"
MQTT_control_broker_IP = MQTT_control_broker_svc_name + ".default.svc.cluster.local"
MQTT_control_broker_port = 1883

# Mongo settings
# mongoDb Service Name
mongodb_svc_name = "db-svc-mc-noauth"
mongo_IP = mongodb_svc_name + ".default.svc.cluster.local"
mongo_port = 27017

# container_manager [DOCKER, KUBERNETES]
container_manager = "KUBERNETES"

# True if master controller running as a container inside a Pod
# False if master controller running as a python script
master_controller_in_container = True

# Namespace for kubernetes element
working_namespace = "default"

#Authentication settings
JWT_SECRET_KEY = "UYG867ti867f(/&$SWRUco)(YPO/T"  # secret key used to encrypt password
