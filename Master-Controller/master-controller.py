# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Fed4IoT system controller

# -*- coding: utf-8 -*-
from __future__ import print_function
import datetime
import json
import sys
import time
import traceback
import logging
from threading import Thread

from user import User

import docker
import paho.mqtt.client as mqtt
from bson.json_util import dumps
from flask import Flask
from flask import Response
from flask import json
from flask import request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_raw_jwt, get_jti
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import kubernetes
from kubernetes import client, config

import time
import kubernetes.client
from kubernetes.client.rest import ApiException

import data.settings as settings
import db_setup
import kubernetes_functions as k8s
import requests


# public IP address through the which it is possible to access thingvisors, database, vSilos, etc.
default_gateway_IP = settings.default_gateway_IP

# MQTT settings (possibly two brokers one for control and another one for control messages)
MQTT_data_broker_IP = settings.MQTT_data_broker_IP
MQTT_data_broker_port = settings.MQTT_data_broker_port
MQTT_control_broker_IP = settings.MQTT_control_broker_IP
MQTT_control_broker_port = settings.MQTT_control_broker_port

mqttc = mqtt.Client()

# Flask settings
flask_host = "0.0.0.0"
flask_port = 8090  # port of the controller
# auth = HTTPBasicAuth()

master_controller_prefix = "master"  # prefix name for Master-Controller communication topic
v_silo_prefix = "vSilo"  # prefix name for Virtual Silo communication topic
v_thing_prefix = "vThing"  # prefix name for virtual Thing data and control topics
thing_visor_prefix = "TV"  # prefix name for ThingVisor communication topic
in_control_suffix = "c_in"
out_control_suffix = "c_out"

# Mongo settings
mongo_IP = settings.mongo_IP
mongo_port = settings.mongo_port
db_name = "viriotDB"
v_silo_collection = "vSiloC"
v_thing_collection = "vThingC"
flavour_collection = "flavourC"
thing_visor_collection = "thingVisorC"
user_collection = "userC"

USER_ROLE_USER = "user"
USER_ROLE_ADMIN = "admin"

STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_STOPPING = "stopping"
STATUS_STOPPED = "stopped"
STATUS_SHUTTING_DOWN = "shutting_down"
STATUS_TERMINATED = "terminated"
STATUS_READY = "ready"
STATUS_ERROR = "error"

container_manager = settings.container_manager

# working_namespace = ""


def create_virtual_silo_on_docker(v_silo_id, v_silo_name, tenant_id, flavour_params,
                                  debug_mode, flavour_image_name, flavour_id, yamls_file=None, deploy_zone=None):
    try:
        # Add mqtt subscription to silo control topics
        mqttc.message_callback_add(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix,
                                   on_silo_out_control_message)
        mqttc.subscribe(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)

        env = {"tenantID": tenant_id, "flavourParams": flavour_params,
               "MQTTDataBrokerIP": MQTT_data_broker_IP, "MQTTDataBrokerPort": MQTT_data_broker_port,
               "MQTTControlBrokerIP": MQTT_control_broker_IP, "MQTTControlBrokerPort": MQTT_control_broker_port,
               "vSiloID": v_silo_id, "systemDatabaseIP": mongo_IP, "systemDatabasePort": mongo_port}

        if not debug_mode:
            # run Docker container for Mobius broker
            docker_client.containers.run(flavour_image_name, name=v_silo_id, tty=True, detach=True, remove=True,
                                         environment=env, publish_all_ports=True)
            # get IP of Docker. TODO Docker must use default network (bridge), remove this constraint
            time.sleep(1)
            container = docker_client.containers.get(v_silo_id)  # need new get (network is assigned a bit later)
            ip_address = container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
            container_name = container.name
            container_id = container.id
            exposed_ports = {}
            mapped_port = container.attrs['NetworkSettings']['Ports']
            for key in mapped_port.keys():
                exposed_ports[key] = mapped_port[key][0]['HostPort']

        else:
            container_name = tenant_id
            container_id = "debug_mode"
            ip_address = "127.0.0.1"
            exposed_ports = {"none": "none"}
        # registering silo in system database
        silo_entry = {"creationTime": datetime.datetime.now().isoformat(), "tenantID": tenant_id,
                      "flavourParams": flavour_params, "containerName": container_name, "containerID": container_id,
                      "ipAddress": ip_address, "port": exposed_ports, "vSiloID": v_silo_id,
                      "vSiloName": v_silo_name, "status": STATUS_RUNNING, "flavourID": flavour_id}
        db[v_silo_collection].update_one({"vSiloID": v_silo_id}, {"$set": silo_entry})

    except Exception:
        db[v_silo_collection].delete_one({"vSiloID": v_silo_id})
        print(traceback.format_exc())

# -t [TENANT_ID] -s [VSILO_NAME] -f [FLAVOUR_NAME]
# python3 f4i.py create-vsilo -c http://127.0.0.1:8090 -t tenant1 -f mqtt-f-k8s -s Silo2
def create_virtual_silo_on_kubernetes(v_silo_id, v_silo_name, tenant_id, flavour_params,
                                  debug_mode, flavour_image_name, flavour_id, yamls_file, deploy_zone):
    print("Creation of vSilo on k8s")
    global working_namespace
    try:

        # Add mqtt subscription to silo control topics
        mqttc.message_callback_add(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix,
                                   on_silo_out_control_message)
        mqttc.subscribe(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)

        env = {"tenantID": tenant_id, "flavourParams": flavour_params,
               "MQTTDataBrokerIP": MQTT_data_broker_IP, "MQTTDataBrokerPort": MQTT_data_broker_port,
               "MQTTControlBrokerIP": MQTT_control_broker_IP, "MQTTControlBrokerPort": MQTT_control_broker_port,
               "vSiloID": v_silo_id, "systemDatabaseIP": mongo_IP, "systemDatabasePort": mongo_port}

        service_name = "error"
        deployment_name = "error"
        label_app = str("%s-%s") % (tenant_id.lower(), v_silo_name.lower())
        api_response_service = None
        if not debug_mode:
            for yaml in yamls_file:
                if yaml["kind"] == "Deployment":
                    print("Deployment Creation")
                    yaml["spec"]["selector"]["matchLabels"]["siloID"] = label_app
                    yaml["spec"]["template"]["metadata"]["labels"]["siloID"] = label_app
                    yaml["spec"]["template"]["spec"]["containers"][0]["env"] = k8s.convert_env(env)
                    if deploy_zone is not None and deploy_zone:
                        yaml["spec"]["template"]["spec"]["nodeSelector"] = {"zone": deploy_zone["zone"]}
                        gateway_IP = deploy_zone["gw"] if "gw" in deploy_zone.keys() else default_gateway_IP
                    else:
                        # This variable set the node anti affinity to deploy the resources in the default zone,
                        # composed of the node without label "zone"
                        yaml["spec"]["template"]["spec"]["affinity"] = k8s.zone_affinity
                        gateway_IP = default_gateway_IP
                    deployment_name = yaml["metadata"]["name"] + str("-%s-%s") % (tenant_id.lower(), v_silo_name.lower())
                    yaml["metadata"]["name"] = deployment_name
                    # print(yaml)
                    api_response_deployment = k8s.create_deployment_from_yaml(namespace="default", body=yaml)
                    # print(api_response_deployment)

                elif yaml["kind"] == "Service":
                    print("Service Creation")
                    service_name = yaml["metadata"]["name"] + str("-%s-%s") % (tenant_id.lower(), v_silo_name.lower())
                    yaml["metadata"]["name"] = service_name
                    yaml["spec"]["selector"]["siloID"] = label_app
                    api_response_service = k8s.create_service_from_yaml(namespace="default", body=yaml)
                    # print(api_response_service)

                else:
                    print("Error: yaml kind not supported (vSilo)")

                # TODO handle error in create_service/create_deployment

            time.sleep(1)
            ip_address = "%s.%s.svc.cluster.local" % (service_name, working_namespace)
            container_name = deployment_name
            container_id = deployment_name
            exposed_ports = {}
            mapped_port = api_response_service.spec.ports
            for port in mapped_port:
                exposed_ports["%s/tcp" % str(port.port)] = str(port.node_port)

        else:
            container_name = tenant_id
            container_id = "debug_mode"
            ip_address = "127.0.0.1"
            exposed_ports = {"none": "none"}

        # registering silo in system database
        silo_entry = {"creationTime": datetime.datetime.now().isoformat(), "tenantID": tenant_id,
                      "flavourParams": flavour_params, "containerName": container_name, "containerID": container_id,
                      "deploymentName": deployment_name, "serviceName": service_name,
                      # "ipAddress": ip_address, "port": exposed_ports, "vSiloID": v_silo_id,
                      "ipAddress": gateway_IP, "port": exposed_ports, "vSiloID": v_silo_id,
                      "vSiloName": v_silo_name, "status": STATUS_RUNNING, "flavourID": flavour_id}
        db[v_silo_collection].update_one({"vSiloID": v_silo_id}, {"$set": silo_entry})

    except Exception:
        db[v_silo_collection].delete_one({"vSiloID": v_silo_id})
        print(traceback.format_exc())


def destroy_virtual_silo_on_docker(silo_entry):

    v_silo_id = silo_entry["vSiloID"]
    container_id = silo_entry["containerID"]
    if not container_id == "debug_mode":
        print("stopping docker container with ID: " + container_id)
        if docker_client.containers.get(container_id).kill() is not None:
            print('ERROR:\tDelete fails')
            return json.dumps({"message": 'Error on silo destroy, v_silo_id: ' + v_silo_id}), 401


def destroy_virtual_silo_on_kubernetes(silo_entry):

    deployment_name = silo_entry["deploymentName"]
    service_name = silo_entry["serviceName"]
    if not deployment_name == "" or service_name == "":
        print("Stopping deployment: %s, and service: %s" % (deployment_name, service_name))
        if not k8s.delete_deployment(namespace=working_namespace, name=deployment_name)[0]:
            print('ERROR:\tDelete fails')
            return json.dumps(
                {"message": 'Error on silo destroy, problem with delete deployment: ' + deployment_name}), 401
        if not k8s.delete_service(namespace=working_namespace, name=service_name)[0]:
            print('ERROR:\tDelete fails')
            return json.dumps(
                {"message": 'Error on silo destroy, problem with delete service: ' + service_name}), 401


def create_thing_visor_on_docker(tv_img_name, debug_mode, tv_id, tv_params, tv_description, yamls_file=None, deploy_zone=None):
    try:
        if not dockerImageExist(tv_img_name) and not debug_mode:
            docker_client.images.pull(tv_img_name)
        # Add mqtt subscription to TV control topics
        mqttc.message_callback_add(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix,
                                   on_tv_out_control_message)
        mqttc.subscribe(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)

        # Sleep 1 sec before run container (delay for the creation of mqtt callback)
        time.sleep(1)

        env = {"MQTTDataBrokerIP": MQTT_data_broker_IP, "MQTTDataBrokerPort": MQTT_data_broker_port,
               "MQTTControlBrokerIP": MQTT_control_broker_IP, "MQTTControlBrokerPort": MQTT_control_broker_port,
               "params": tv_params, "thingVisorID": tv_id, "systemDatabaseIP": mongo_IP,
               "systemDatabasePort": mongo_port}

        exposed_ports = {}
        if not debug_mode:
            # new entry: start thingVisor container and insert in system database
            docker_client.containers.run(tv_img_name, name=tv_id, tty=True, detach=True, remove=True,
                                         environment=env, publish_all_ports=True)
            time.sleep(1)  # need new get because network is assigned a bit later

            container = docker_client.containers.get(tv_id)
            ip_address = container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
            container_id = container.id
            mapped_port = container.attrs['NetworkSettings']['Ports']
            for key in mapped_port.keys():
                exposed_ports[key] = mapped_port[key][0]['HostPort']
        else:
            container_id = "debug_mode"
            ip_address = "127.0.0.1"

        mqtt_data_broker = {"ip": MQTT_data_broker_IP, "port": MQTT_data_broker_port}
        mqtt_control_broker = {"ip": MQTT_control_broker_IP, "port": MQTT_control_broker_port}

        # registering thingVisor in system database
        thing_visor_entry = {"creationTime": datetime.datetime.now().isoformat(),
                             "tvDescription": tv_description, "containerID": container_id,
                             "thingVisorID": tv_id, "imageName": tv_img_name, "ipAddress": ip_address,
                             "debug_mode": debug_mode, "vThings": [], "params": tv_params,
                             "MQTTDataBroker": mqtt_data_broker,
                             "MQTTControlBroker": mqtt_control_broker,
                             "port": exposed_ports,
                             "IP": default_gateway_IP,
                             "status": STATUS_RUNNING
                             }
        db[thing_visor_collection].update_one({"thingVisorID": tv_id}, {"$set": thing_visor_entry})

        print("insert thingVisorID into DB")

    except Exception as ex:
        # db[thing_visor_collection].delete_one({"thingVisorID": tv_id})
        db[thing_visor_collection].update_one({"thingVisorID": tv_id}, {"$set": {"status": STATUS_ERROR,
                                                                                 "error": "%s" % ex}})
        # print(traceback.format_exc())


def create_thing_visor_on_kubernetes(tv_img_name, debug_mode, tv_id, tv_params, tv_description, yamls_file, deploy_zone):
    global working_namespace
    try:
        print("Creation of ThingVisor on k8s")

        # Add mqtt subscription to TV control topics
        mqttc.message_callback_add(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix, on_tv_out_control_message)
        mqttc.subscribe(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)

        # Sleep 1 sec before run container (delay for the creation of mqtt callback)
        time.sleep(1)

        env = {"MQTTDataBrokerIP": MQTT_data_broker_IP, "MQTTDataBrokerPort": MQTT_data_broker_port,
               "MQTTControlBrokerIP": MQTT_control_broker_IP, "MQTTControlBrokerPort": MQTT_control_broker_port,
               "params": tv_params, "thingVisorID": tv_id, "systemDatabaseIP": mongo_IP,
               "systemDatabasePort": mongo_port}

        exposed_ports = {}
        deployment_name = "error"
        service_name = ""
        if not debug_mode:
            api_response_service = None

            for yaml in yamls_file:
                if yaml["kind"] == "Deployment":
                    print("Deployment Creation")
                    yaml["metadata"]["name"] += "-" + tv_id.lower().replace("_", "-")
                    yaml["spec"]["template"]["spec"]["containers"][0]["env"] = k8s.convert_env(env)
                    tv_img_name = yaml["spec"]["template"]["spec"]["containers"][0]["image"]

                    url = "https://hub.docker.com/v2/repositories/%s" % tv_img_name.split(":")[0]
                    print("Request_url", url)
                    response = requests.head(url, allow_redirects=True)
                    if not response.status_code == 200:
                        raise docker.errors.ImageNotFound("ImageNotFound")

                    if deploy_zone is not None and deploy_zone:

                        yaml["spec"]["template"]["spec"]["nodeSelector"] = {"zone": deploy_zone["zone"]}
                        gateway_IP = deploy_zone["gw"] if "gw" in deploy_zone.keys() else default_gateway_IP
                    else:
                        # This variable set the node anti affinity to deploy the resources in the default zone,
                        # composed of the node without label "zone"
                        yaml["spec"]["template"]["spec"]["affinity"] = k8s.zone_affinity
                        gateway_IP = default_gateway_IP
                    deployment_name = yaml["metadata"]["name"]
                    api_response_deployment = k8s.create_deployment_from_yaml(namespace="default", body=yaml)
                    # print(api_response_deployment)

                elif yaml["kind"] == "Service":
                    print("Service Creation")
                    service_name = yaml["metadata"]["name"] + tv_id.lower().replace("_", "-")
                    yaml["metadata"]["name"] = service_name
                    api_response_service = k8s.create_service_from_yaml(namespace="default", body=yaml)
                    # print(api_response_service)
                else:
                    print("Error: yaml kind not supported (thingVisor)")

            time.sleep(1)  # need new get because network is assigned a bit later

            ip_address = "%s.%s.svc.cluster.local" % (service_name, working_namespace)
            container_id = deployment_name
            if api_response_service:
                mapped_port = api_response_service.spec.ports
                for port in mapped_port:
                    exposed_ports["%s/tcp" % str(port.port)] = str(port.node_port)
        else:
            container_id = "debug_mode"
            ip_address = "127.0.0.1"

        mqtt_data_broker = {"ip": MQTT_data_broker_IP, "port": MQTT_data_broker_port}
        mqtt_control_broker = {"ip": MQTT_control_broker_IP, "port": MQTT_control_broker_port}

        # registering thingVisor in system database
        thing_visor_entry = {"creationTime": datetime.datetime.now().isoformat(),
                             "tvDescription": tv_description, "containerID": container_id,
                             "thingVisorID": tv_id, "imageName": tv_img_name, "ipAddress": ip_address,
                             "deploymentName": deployment_name, "serviceName": service_name,
                             "debug_mode": debug_mode, "vThings": [], "params": tv_params,
                             "MQTTDataBroker": mqtt_data_broker,
                             "MQTTControlBroker": mqtt_control_broker,
                             "port": exposed_ports,
                             "IP": gateway_IP,
                             "status": STATUS_RUNNING
                             }
        db[thing_visor_collection].update_one({"thingVisorID": tv_id}, {"$set": thing_visor_entry})

        print("insert thingVisorID into DB")

    except Exception as ex:
        # db[thing_visor_collection].delete_one({"thingVisorID": tv_id})
        db[thing_visor_collection].update_one({"thingVisorID": tv_id}, {"$set": {"status": STATUS_ERROR,
                                                                                 "error": "%s" % ex}})
        # print(traceback.format_exc())

def delete_thing_visor_on_docker(tv_entry):
    container_id = tv_entry["containerID"]
    if docker_client.containers.get(container_id).kill() is not None:
        print('ERROR:\tDelete fails')
    # docker_client.images.remove(tv_entry["imageName"], force=True)
    # uncomment previous line to remove the docker image too

def delete_thing_visor_on_kubernetes(tv_entry):

    tv_id = tv_entry["thingVisorID"]
    print("Delete Deployment %s" % tv_id)
    deployment_name = tv_entry["deploymentName"]
    service_name = tv_entry["serviceName"]

    if not deployment_name == "":
        print("stopping deployment: %s, and service: %s" % (deployment_name, service_name))
        if not k8s.delete_deployment(namespace=working_namespace, name=deployment_name)[0]:
            print('ERROR:\tDelete fails')
            return json.dumps(
                {"message": 'Error on ThingVisor destroy, problem with delete deployment: ' + deployment_name}), 401

    if not service_name == "":
        if not k8s.delete_service(namespace=working_namespace, name=service_name)[0]:
            print('ERROR:\tDelete fails')
            return json.dumps(
                {"message": 'Error on ThingVisor destroy, problem with delete service: ' + service_name}), 401


# yamls_file only for compatibility with Kubernetes implementation (not used)
def add_flavour_on_docker(image_name, flavour_id, flavour_params, flavour_description, yamls_file):
    try:
        # docker image name must do not contains upper case characters
        if not image_name.islower():
            db[flavour_collection].delete_one({"flavourID": flavour_id})
            print("Add fails - image name must be lowercase")
            return  # "Add fails - image name must be lowercase", 409

        if not dockerImageExist(image_name):
            docker_client.images.pull(image_name)
        # docker_client.images.get(image_name)  # raise an an exception if images does not exist

        db[flavour_collection].update_one({"flavourID": flavour_id},
                                          {"$set": {"flavourParams": flavour_params, "imageName": image_name,
                                                    "flavourDescription": flavour_description,
                                                    "creationTime": datetime.datetime.now().isoformat(),
                                                    "status": STATUS_READY}})
        print("Flavour " + flavour_id + " added")
        return

    except docker.errors.ImageNotFound as err:
        # db[flavour_collection].delete_one({"flavourID": flavour_id})
        db[flavour_collection].update_one({"flavourID": flavour_id},
                                          {"$set": {"flavourParams": flavour_params, "imageName": image_name,
                                                    "flavourDescription": flavour_description,
                                                    "creationTime": datetime.datetime.now().isoformat(),
                                                    "status": STATUS_ERROR,
                                                    "error": "%s" % err}})
        print('Add fails - Could not find the Docker image of the flavour')
        return  # 'Add fails - Could not find the Docker image of the flavour', 409
    except docker.errors.APIError as err:
        # db[flavour_collection].delete_one({"flavourID": flavour_id})
        db[flavour_collection].update_one({"flavourID": flavour_id},
                                          {"$set": {"flavourParams": flavour_params, "imageName": image_name,
                                                    "flavourDescription": flavour_description,
                                                    "creationTime": datetime.datetime.now().isoformat(),
                                                    "status": STATUS_ERROR,
                                                    "error": "%s" % err}})
        print('Add fails - Could not find the Docker image of the flavour')
        return  # 'Add fails - Could not find the Docker image of the flavour', 409
    except Exception:
        print(traceback.format_exc())
        # db[flavour_collection].delete_one({"flavourID": flavour_id})
        db[flavour_collection].update_one({"flavourID": flavour_id},
                                          {"$set": {"flavourParams": flavour_params, "imageName": image_name,
                                                    "flavourDescription": flavour_description,
                                                    "creationTime": datetime.datetime.now().isoformat(),
                                                    "status": STATUS_ERROR}})
        return  # 'Add fails', 401


def add_flavour_on_kubernetes(image_name, flavour_id, flavour_params, flavour_description, yamls_file):
    try:

        for yaml in yamls_file:
            if yaml["kind"] == "Deployment":
                image_name = yaml["spec"]["template"]["spec"]["containers"][0]["image"]
                break

        url = "https://hub.docker.com/v2/repositories/%s" % image_name.split(":")[0]
        response = requests.head(url, allow_redirects=True)
        if not response.status_code == 200:
            raise docker.errors.ImageNotFound("ImageNotFound")

        print("Creation of Flavour on k8s")
        db[flavour_collection].update_one({"flavourID": flavour_id},
                                          {"$set": {"flavourParams": flavour_params,
                                                    "imageName": image_name,
                                                    "flavourDescription": flavour_description,
                                                    "creationTime": datetime.datetime.now().isoformat(),
                                                    "status": STATUS_READY,
                                                    "yamlsFile": yamls_file}})
        print("Flavour " + flavour_id + " added")
        return


    except docker.errors.ImageNotFound as err:
        # db[flavour_collection].delete_one({"flavourID": flavour_id})
        db[flavour_collection].update_one({"flavourID": flavour_id},
                                          {"$set": {"flavourParams": flavour_params,
                                                    "imageName": image_name,
                                                    "flavourDescription": flavour_description,
                                                    "creationTime": datetime.datetime.now().isoformat(),
                                                    "status": STATUS_ERROR,
                                                    "error": "%s" % err,
                                                    "yamlsFile": yamls_file}})
        print('Add fails - Could not find the Docker image of the flavour')
        return  # 'Add fails - Could not find the Docker image of the flavour', 409
    except docker.errors.APIError as err:
        print("%s" % err)
        # db[flavour_collection].delete_one({"flavourID": flavour_id})
        db[flavour_collection].update_one({"flavourID": flavour_id},
                                          {"$set": {"flavourParams": flavour_params,
                                                    "imageName": image_name,
                                                    "flavourDescription": flavour_description,
                                                    "creationTime": datetime.datetime.now().isoformat(),
                                                    "status": STATUS_ERROR,
                                                    "error": "%s" % err,
                                                    "yamlsFile": yamls_file}})
        print('Add fails - Could not find the Docker image of the flavour')
        return  # 'Add fails - Could not find the Docker image of the flavour', 409
    except Exception:
        print(traceback.format_exc())
        # db[flavour_collection].delete_one({"flavourID": flavour_id})
        db[flavour_collection].update_one({"flavourID": flavour_id},
                                          {"$set": {"flavourParams": flavour_params,
                                                    "imageName": image_name,
                                                    "flavourDescription": flavour_description,
                                                    "creationTime": datetime.datetime.now().isoformat(),
                                                    "status": STATUS_ERROR,
                                                    "yamlsFile": yamls_file}})
        return  # 'Add fails', 401


def get_deploy_zone_on_docker(tv_zone):
    return {"zone": None, "gw": settings.floating_public_IP}, None

def get_deploy_zone_on_kubernetes(tv_zone):
    available_zones = k8s.list_available_node_zone()
    print("get_deploy_zone_on_kubernetes -> available_zones", available_zones)
    if tv_zone is not "" and tv_zone in available_zones:
        return {"zone": tv_zone, "gw": available_zones[tv_zone]}, available_zones.keys()
    else:
        return {}, available_zones.keys()

class httpThread(Thread):
    app = Flask(__name__)

    # A storage engine to save revoked tokens. In production if
    # speed is the primary concern, redis is a good bet. If data
    # persistence is more important for you, postgres is another
    # great option. In this example, we will be using an in memory
    # store, just to show you how this might work. For more
    # complete examples, check out these:
    # https://github.com/vimalloc/flask-jwt-extended/blob/master/examples/redis_blacklist.py
    # https://github.com/vimalloc/flask-jwt-extended/tree/master/examples/database_blacklist
    blacklist = set()

    #
    TOKEN_EXPIRES_DELTA = datetime.timedelta(days=50)

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Thread http started")
        global flask_host, flask_port
        # app.run(host=flaskHost,port=flaskPort, debug=True)
        # app.run(port=flaskPort)

        CORS(self.app)  # cross-origin resource sharing HTTP
        # self.app.config['PERMANENT_SESSION_LIFETIME'] = 10
        # Enable blacklisting and specify what kind of tokens to check
        # against the blacklist
        self.app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
        self.app.config['JWT_BLACKLIST_ENABLED'] = True
        self.app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
        jwt = JWTManager(self.app)

        # For this example, we are just checking if the tokens jti
        # (unique identifier) is in the blacklist set. This could
        # be made more complex, for example storing all tokens
        # into the blacklist with a revoked status when created,
        # and returning the revoked status in this call. This
        # would allow you to have a list of all created tokens,
        # and to consider tokens that aren't in the blacklist
        # (aka tokens you didn't create) as revoked. These are
        # just two options, and this can be tailored to whatever
        # your application needs.
        @jwt.token_in_blacklist_loader
        def check_if_token_in_blacklist(decrypted_token):
            jti = decrypted_token['jti']
            return jti in self.blacklist

        @jwt.unauthorized_loader
        def unauthorized_response(callback):
            return json.dumps({'status': 401, 'message': 'Missing Authorization Header'}), 401

        logging.basicConfig(level=logging.INFO)
        self.app.run(host=flask_host, port=flask_port)
        print("Thread '" + self.name + "closed")


    @app.route('/register', methods=['POST'])
    @jwt_required
    def register_user():
        try:
            user_id = request.json.get('userID', None)
            password = generate_password_hash(request.json.get('password', None))
            role = request.json.get('role', None)

            if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
                httpThread.app.logger.warn('%s tried to register a new user', get_jwt_identity())
                return json.dumps({"message": "operation not allowed"}), 401
            if role not in [USER_ROLE_USER, USER_ROLE_ADMIN]:
                return json.dumps({"message": "Provided role (" + role + ") is not supported"}), 409
            if not User(user_id).find_by_username(db, user_collection, user_id)[0]:
                User(user_id, password, role).save_to_db(db, user_collection)
                return json.dumps({"message": "User registered successfully"}), 201
            else:
                return json.dumps({"message": "User already exists"}), 409
        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": "Error"}), 500

    @app.route('/unregister', methods=['POST'])
    @jwt_required
    def unregister_user():
        try:
            user_id = request.json.get('userID', None)
            if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
                httpThread.app.logger.warn('%s tried to unregister an user', get_jwt_identity())
                return json.dumps({"message": "operation not allowed"}), 401
            elif User(user_id).find_by_username(db, user_collection, user_id)[0]:
                token_to_remove = User(user_id).remove_from_db(db, user_collection)
                print(token_to_remove)
                # print(get_jti(token_to_remove))
                if token_to_remove is not None:
                    httpThread.blacklist.add(get_jti(token_to_remove))
                return json.dumps({"message": 'User unregistered successfully'}), 201
            else:
                return json.dumps({"message": "User " + user_id + " does not exists"}), 409
        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": "Error"}), 500

    @app.route('/login', methods=['POST'])
    def login_user():
        try:
            user_id = request.json.get('userID', None)
            password_provided = request.json.get('password', None)
            user, hpassword = User.find_by_username(db, user_collection, user_id)
            if user and check_password_hash(hpassword, password_provided):
                claims = {'role': User(user_id).get_role(db, user_collection)}
                ret = {'access_token': create_access_token(identity=user_id,
                                                           expires_delta=httpThread.TOKEN_EXPIRES_DELTA,user_claims=json.dumps(claims)),
                       'role': User(user_id).get_role(db, user_collection)}
                db[user_collection].update_one({"userID": user},
                                               {"$set": {"lastLogin": datetime.datetime.now().isoformat(),
                                                         "token": ret['access_token']}})
                httpThread.app.logger.info('%s logged in successfully', user)
                return json.dumps(ret), 200
            return json.dumps({"message": "Bad username or password"}), 401
        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": "Error"}), 500

    @app.route('/listUsers', methods=['GET'])
    @jwt_required
    def list_users():
        print(get_jwt_identity())
        try:
            if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
                httpThread.app.logger.warn('%s tried to get the list of users', get_jwt_identity())
                return json.dumps({"message": "operation not allowed"}), 401
            return Response(dumps(db[user_collection].find({}, {"_id": 0, "password": 0, "token": 0})),
                            201, mimetype='application/json'), 201
        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": "Error"}), 500

    @app.route('/logout', methods=['DELETE'])
    @jwt_required
    def logout():
        jti = get_raw_jwt()['jti']
        httpThread.blacklist.add(jti)
        httpThread.app.logger.info('%s logged out successfully', get_jwt_identity())
        return json.dumps({"message": "Successfully logged out"}), 200

    # -t [TENANT_ID] -s [VSILO_NAME] -f [FLAVOUR_NAME]
    # python3 f4i.py create-vsilo -c http://127.0.0.1:8090 -t tenant1 -f mqtt-f-k8s -s Silo2
    @app.route('/siloCreate', methods=['POST'])
    @jwt_required
    def recv_siloCreate():
        try:
            global db, docker_client
            tenant_id = request.json.get('tenantID', None)
            if not User(get_jwt_identity()).check_user_permission(db, user_collection, tenant_id):
                httpThread.app.logger.warn('%s tried to create a silo for the tenant (%s)', get_jwt_identity(),
                                           tenant_id)
                return json.dumps({"message": "operation not allowed"}), 401
            flavour_id = request.json.get('flavourID', None)
            v_silo_name = request.json.get('vSiloName', None)
            v_silo_zone = request.json.get('vSiloZone', None)

            v_silo_id = tenant_id + "_" + v_silo_name

            deploy_zone = {}
            available_zones = []
            if v_silo_zone is not None and v_silo_zone != "":
                deploy_zone, available_zones = get_deploy_zone(v_silo_zone)  # receive {"zone":zone_tv, "gw":floatingIP} if zone exists, otherwise none

                if not deploy_zone:
                    return json.dumps({"message": 'Silo create fails, zone ' + v_silo_zone + ' is not available ' + str(list(available_zones))}), 401

                if deploy_zone["gw"] == "":
                    return json.dumps({"message": 'Silo create fails, gateway for zone ' + v_silo_zone + ' is not defined!'}), 401

            # check if virtual silo ID already exists
            if db[v_silo_collection].count({"vSiloID": v_silo_id}) > 0:
                return json.dumps({'message': 'Create fails - vSiloName ' + v_silo_name +
                                              ' already in use for tenant ' + tenant_id}), 409
            debug_mode = request.json.get('debug_mode', False)

            # check if the flavor ID is correct
            if db[flavour_collection].count({"flavourID": flavour_id}) == 0:
                # Flavour not exists
                return json.dumps({"message": 'Create fails - Requested flavour does not exist'}), 409
            flavour_entry = db[flavour_collection].find_one({"flavourID": flavour_id})
            flavour_image_name = flavour_entry["imageName"]
            flavour_params = flavour_entry["flavourParams"]
            # Check if the falour is not in errore state
            if flavour_entry["status"] == STATUS_ERROR:
                return json.dumps({"message": 'Create fails - Requested flavour status is: %s' % STATUS_ERROR}), 409

            yamls_file = ""
            if "yamlsFile" in flavour_entry:
                yamls_file = flavour_entry["yamlsFile"]

            silo_entry = {"vSiloID": v_silo_id, "status": STATUS_PENDING}

            db[v_silo_collection].insert_one(silo_entry)

            Thread(target=create_virtual_silo,
                   args=(v_silo_id, v_silo_name, tenant_id, flavour_params, debug_mode, flavour_image_name,
                         flavour_id, yamls_file, deploy_zone)).start()

            msg = "Virtual Silo is starting. Please wait... \n\n" \
                  "Check process status with inspectVirtualSilo API, \n" \
                  "POST parameters: {'vSiloID': " + v_silo_id + "}"
            return json.dumps({"message": str(msg), "vSiloID": v_silo_id}), 201

        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": 'Create fails'}, 401)

    @app.route('/siloDestroy', methods=['POST'])
    @jwt_required
    def recv_silo_destroy():
        global working_namespace
        try:
            global db, docker_client
            tenant_id = request.json.get('tenantID', None)
            v_silo_id = tenant_id + "_" + request.json.get('vSiloName', None)
            if not User(get_jwt_identity()).check_user_permission(db, user_collection, tenant_id):
                httpThread.app.logger.warn('%s tried to delete a silo for the tenant (%s)', get_jwt_identity(),
                                           tenant_id)
                return json.dumps({"message": "operation not allowed"}), 401
            silo_entry = db[v_silo_collection].find_one({"vSiloID": v_silo_id})
            if silo_entry is None:
                return json.dumps({"message": 'Delete fails - tenantID or vSiloID not valid'}), 401

            if request.json.get('force', False):

                destroy_virtual_silo(silo_entry)

                db[v_thing_collection].delete_many({"vSiloID": v_silo_id})
                silo_res = db[v_silo_collection].delete_many({"vSiloID": v_silo_id})
                if silo_res.deleted_count > 0:
                    # Remove mqtt subscription to silo control topics
                    mqttc.message_callback_remove(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)
                    mqttc.unsubscribe(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)
                    print('Silo ' + v_silo_id + ' destroyed')
                    return json.dumps({"message": 'Virtual silo ' + v_silo_id + ' destroyed (force=true)'}), 201

            db[v_silo_collection].update_one({"vSiloID": v_silo_id}, {"$set": {"status": STATUS_STOPPING}})

            # Send destroy command to vSilo
            destroy_cmd = {"command": "destroyVSilo", "vSiloID": v_silo_id}
            mqttc.publish(v_silo_prefix + "/" + v_silo_id + "/" + in_control_suffix, str(destroy_cmd).replace("\'", "\""))
            return json.dumps({"message": 'Destroying virtual silo ' + v_silo_id}), 201
        except Exception as ex:
            # db[v_silo_collection].deleteOne({"vSiloID": v_silo_id})
            return json.dumps({"message": 'Error on silo destroy, v_silo_id: ' + v_silo_id}), 401


    # python3 f4i.py add-vthing -c http://127.0.0.1:8090 -t tenant1 -s Silo1 -v ciaoMondo/1
    @app.route('/addVThing', methods=['POST'])
    @jwt_required
    def recv_add_vthing():
        global db, mqttc
        # print ("enter create, POST body: "+str(jres))
        # create the message mqttMsg to be sent to the silo controller of the tenant
        try:
            print(request.json)
            v_thing_id = request.json.get('vThingID', None)
            tenant_id = request.json.get('tenantID', None)

            v_silo_id = tenant_id + "_" + request.json.get("vSiloName", None)
            if not User(get_jwt_identity()).check_user_permission(db, user_collection, tenant_id):
                httpThread.app.logger.warn('%s tried to add vthing for the tenant (%s)', get_jwt_identity(),
                                           tenant_id)
                return json.dumps({"message": "operation not allowed"}), 401

            # check on system database if the virtual thing exists
            vthing_entry = db[thing_visor_collection].find_one({"vThings.id": v_thing_id})

            if db[thing_visor_collection].count({"vThings.id": v_thing_id}) == 0:
                return json.dumps({"message": 'Add fails - virtual thing does not exist'}), 409

            # check if tenantID and vSiloID are valid
            if db[v_silo_collection].count({"vSiloID": v_silo_id}) == 0:
                return json.dumps({"message": 'Add fails - tenantID or vSiloID not valid'}), 401

            # check silo status, must be "running"
            if (db[v_silo_collection].find_one(
                    {"vSiloID": v_silo_id}, {"status": 1, "_id": 0}))["status"] != STATUS_RUNNING:
                httpThread.app.logger.error('virtual silo %s is not ready, add vThing fails', v_silo_id())
                return json.dumps({"message": 'Add fails - virtual silo' + v_silo_id + ' is not ready'}), 409

            mqtt_msg = {"command": "addVThing", "vSiloID": v_silo_id, "vThingID": v_thing_id}

            # check if the tenant is already using the virtual thing in the same virtual IoT system
            if db[v_thing_collection].count({"vThingID": v_thing_id,
                                             "tenantID": tenant_id,
                                             "vSiloID": v_silo_id}) > 0:
                return json.dumps({"message": 'Add fails - Virtual thing \'' + v_thing_id +
                                              '\' already exists for tenantID "' + tenant_id + \
                                              '" and vSiloID "' + v_silo_id + '"'}), 409
        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": 'Add fails'}), 401

        mqttc.publish(v_silo_prefix + "/" + v_silo_id + "/" + in_control_suffix, str(mqtt_msg).replace("\'", "\""))

        # update system database
        v_thing_entry = {"tenantID": tenant_id, "vThingID": v_thing_id,
                         "creationTime": datetime.datetime.now().isoformat(), "vSiloID": v_silo_id}
        v_thing_db_entry = db[v_thing_collection].insert_one(v_thing_entry).inserted_id

        return json.dumps({"message": 'vThing created'}), 201

    @app.route('/deleteVThing', methods=['POST'])
    @jwt_required
    def recv_deleteVThing():
        print("enter vThing delete, POST body: " + str(request.json))
        try:
            v_thing_id = request.json.get("vThingID", None)
            tenant_id = request.json.get("tenantID", None)
            v_silo_id = tenant_id + "_" + request.json.get("vSiloName", None)
            if not User(get_jwt_identity()).check_user_permission(db, user_collection, tenant_id):
                httpThread.app.logger.warn('%s tried to delete vthing for the tenant (%s)', get_jwt_identity(),
                                           tenant_id)
                return json.dumps({"message": "operation not allowed"}), 401

            # check if tenantID the virtual thing name are correct
            if db[v_thing_collection].count({"vThingID": v_thing_id, "tenantID": tenant_id,
                                             "vSiloID": v_silo_id}) == 0:
                return json.dumps({"message": 'Delete fails - Virtual Thing ID, tenantID or vSiloID not valid'}), 409
            # delete vThing entry in db
            result = db[v_thing_collection].delete_one({"vThingID": v_thing_id, "tenantID": tenant_id,
                                                        "vSiloID": v_silo_id})
        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": 'Delete fails'}), 401
        if result.deleted_count > 0:
            # send to involved vSilo the deletion message by publishing on vSilo's in_control topic
            mqtt_msg = {"command": "deleteVThing", "vSiloID": v_silo_id, "vThingID": v_thing_id}
            global mqttc
            mqttc.publish(v_silo_prefix + "/" + v_silo_id + "/" + in_control_suffix, str(mqtt_msg).replace("\'", "\""))
            return json.dumps({"message": 'deleted virtual thing: ' + v_thing_id}), 200
        else:
            return json.dumps({"message": 'Delete fails, vThingID or tenantID not valid'}), 401

    @app.route('/listThingVisors', methods=['GET'])
    @jwt_required
    def recv_listThingVisors():
        if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
            httpThread.app.logger.warn('%s tried to get thing visor list', get_jwt_identity())
            return json.dumps({"message": "operation not allowed"}), 401
        thing_visors = db[thing_visor_collection].find({}, {"_id": 0})
        return Response(dumps(thing_visors), 200, mimetype='application/json'), 200

    @app.route('/listVirtualSilos', methods=['GET'])
    @jwt_required
    def recv_listVirtualSilos():
        if User(get_jwt_identity()).check_admin_permission(db, user_collection):
            silos = db[v_silo_collection].find({}, {"_id": 0})
        else:
            silos = list(db[v_silo_collection].find({"vSiloID": {'$regex': '^' + get_jwt_identity() + '_'}}, {"_id": 0}))

            for silo in silos:
                vsilo_id = silo['vSiloID']
                vthings = db[v_thing_collection].find({"vSiloID": vsilo_id}, {"_id": 0})
                if vthings.count() > 0:
                    silo['vThings'] = json.loads(dumps(vthings))
        return Response(dumps(silos), 200, mimetype='application/json'), 200

    @app.route('/listVThings', methods=['GET'])
    @jwt_required
    def recv_listVThings():
        v_things = []
        v_things_entries = db[thing_visor_collection].find({}, {"_id": 0, "vThings": 1})
        for vThingEntry in v_things_entries:
            for vThing in vThingEntry["vThings"]:
                v_things.append(vThing)
        return Response(dumps(v_things), 200, mimetype='application/json'), 200


    # python3 f4i.py add-thingvisor -c http://127.0.0.1:8090
    #                     -i fed4iot/v-weather-tv:2.2           [IMAGE_NAME]
    #                     -n weather                            [NAME]
    #                     -p "{'cities':['Rome', 'Tokyo','Murcia','Grasse','Heidelberg'],       [PARAMS]
    #                          'rate':60}"
    #                     -d "Weather ThingVisor"               [DESCRIPTION]
    # python3 f4i.py add-thingvisor -c http://127.0.0.1:8090 -i fed4iot/helloworld-tv -n helloWorld -d "hello thingVisor"
    @app.route('/addThingVisor', methods=['POST'])
    @jwt_required
    def recv_addThingVisor():
        try:
            # print(request.get_data(as_text=True))
            tv_description = request.json.get("description", None)
            tv_id = request.json.get("thingVisorID", None)
            tv_img_name = request.json.get("imageName", None)
            tv_params = request.json.get("params", None)
            debug_mode = request.json.get("debug_mode", False)
            yamls_file = request.json.get("yamlsFile", None)
            tv_zone = request.json.get("tvZone", None)


            if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
                httpThread.app.logger.warn('%s tried to add a thingVisor', get_jwt_identity())
                return json.dumps({"message": "operation not allowed"}), 401
            # docker image name must do not contains upper case characters

            if not (tv_img_name.islower() or tv_img_name == ""):
                return json.dumps({"message": "Add fails - image name must be lowercase"}), 409
            # check vThing ID in the database
            if db[thing_visor_collection].count({"thingVisorID": tv_id}) != 0:
                # already exists
                return json.dumps({"message": "Add fails - thingVisor " + tv_id + " already exists"}), 409
            thing_visor_entry = {"thingVisorID": tv_id, "status": STATUS_PENDING, "yamlsFile": yamls_file}


            deploy_zone = {}
            if tv_zone is not None and tv_zone != "":
                deploy_zone, available_zones = get_deploy_zone(tv_zone)  # receive {"zone":zone_tv, "gw":floatingIP} if zone exists, otherwise none

                if not deploy_zone:
                    return json.dumps({"message": 'ThingVisor create fails, zone ' + tv_zone + ' is not available ' + str(list(available_zones))}), 401

                if deploy_zone["gw"] == "":
                    return json.dumps({"message": 'ThingVisor create fails, gateway for zone ' + tv_zone + ' is not defined!'}), 401

            db[thing_visor_collection].insert_one(thing_visor_entry)
            Thread(target=create_thing_visor,
                   args=(tv_img_name, debug_mode, tv_id, tv_params, tv_description, yamls_file, deploy_zone)).start()

            msg = "ThingVisor is starting. Please wait... \n\n" \
                  "Check process status with inspectThingVisor API, \n" \
                  "POST parameters: {'thingVisorID': " + tv_id + "}"

            return json.dumps({"message": str(msg), "thingVisorID": tv_id}), 201

        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": 'Add fails'}), 401


    @app.route('/deleteThingVisor', methods=['POST'])
    @jwt_required
    def recv_deleteThingVisor():
        print("DeleteThingVisor")

        try:
            if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
                httpThread.app.logger.warn('%s tried to delete a thingVisor', get_jwt_identity())
                return json.dumps({"message": "operation not allowed"}), 401
            tv_id = request.json.get("thingVisorID", None)
            if db[thing_visor_collection].count({"thingVisorID": tv_id}) == 0:
                return json.dumps({"message": "Delete fails - thingVisor " + tv_id + " does not exist"}), 409
            else:
                tv_entry = db[thing_visor_collection].find_one({"thingVisorID": tv_id})
                if tv_entry is None:
                    return json.dumps({"message": 'Delete fails - thingVisor ID not valid'}), 401

                if request.json.get('force', False):
                    #tv_v_things = db[thing_visor_collection].find_one({"thingVisorID": tv_id}, {"_id": 0, "vThings": 1})
                    if tv_entry['vThings'] is not None:
                        for v_thing in tv_entry['vThings']:
                            db[v_thing_collection].delete_many({"vThingID": v_thing['id']})
                            msg = {"command": "deleteVThing", "vThingID": v_thing['id'], "vSiloID": "ALL"}
                            mqttc.publish(v_thing_prefix + "/" + v_thing['id'] + "/" + out_control_suffix, str(msg).replace("\'", "\""))
                    tv_entry = db[thing_visor_collection].find_one_and_delete({"thingVisorID": tv_id})
                    # container_id = tv_entry["containerID"]
                    if not tv_entry["debug_mode"]:
                        delete_thing_visor(tv_entry)

                    # Remove mqtt subscription to TV control topics
                    mqttc.message_callback_remove(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)
                    mqttc.unsubscribe(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)
                    return json.dumps({"message": 'thingVisor: ' + tv_id + ' deleted (force=true)'}), 200


                db[thing_visor_collection].update_one({"thingVisorID": tv_id}, {"$set": {"status": STATUS_STOPPING}})

                # Send destroy command to TV
                destroy_cmd = {"command": "destroyTV", "thingVisorID": tv_id}
                mqttc.publish(thing_visor_prefix + "/" + tv_id + "/" + in_control_suffix, str(destroy_cmd).replace("\'", "\""))

                if tv_entry["debug_mode"]:
                    db[thing_visor_collection].delete_one({"thingVisorID": tv_id})

                return json.dumps({"message": 'deleting thingVisor: ' + tv_id}), 200
        except Exception:
            db[thing_visor_collection].delete_one({"thingVisorID": tv_id})
            print(traceback.format_exc())
            return json.dumps({"message": 'thingVisor delete fails'}), 401

    @app.route('/addFlavour', methods=['POST'])
    @jwt_required
    def recv_add_flavour():
        try:
            if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
                httpThread.app.logger.warn('%s tried to add a flavour', get_jwt_identity())
                return json.dumps({"message": "operation not allowed"}), 401
            flavour_id = request.json.get("flavourID", None)
            flavour_params = request.json.get("flavourParams", None)
            image_name = request.json.get("imageName", None)
            flavour_description = request.json.get("flavourDescription", None)
            yamls_file = request.json.get("yamlsFile", None)


            # check if flavour already exists in system database
            if db[flavour_collection].count({"flavourID": flavour_id}) > 0:
                return json.dumps({"message": 'Add fails - flavour name already in use'}), 409
            db[flavour_collection].insert_one({"flavourID": flavour_id, "status": STATUS_PENDING})

            Thread(target=add_flavour,
                   args=(image_name, flavour_id, flavour_params, flavour_description, yamls_file)).start()

            msg = "Flavour is being created. Please wait... \n\n" \
                  "Check process status with inspectFlavour API, \n" \
                  "POST parameters: {'flavourID': " + flavour_id + "}"
            return json.dumps({"message": msg, "flavourID": flavour_id}), 201

        except docker.errors.ImageNotFound:
            return json.dumps({"message": 'Add fails - Could not find the Docker image of the flavour'}), 409
        except docker.errors.APIError:
            return json.dumps({"message": 'Add fails - Could not find the Docker image of the flavour'}), 409
        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": 'Add fails'}), 401

    @app.route('/deleteFlavour', methods=['POST'])
    @jwt_required
    def recv_delete_flavour():
        try:
            if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
                httpThread.app.logger.warn('%s tried to delete a flavour', get_jwt_identity())
                return json.dumps({"message": "operation not allowed"}), 401
            flavour_id = request.json.get("flavourID", None)
            if db[flavour_collection].count({"flavourID": flavour_id}) == 0:
                return json.dumps({"message": "Delete fails - flavour does not exist"}), 409
            else:
                # remove entry
                db[flavour_collection].delete_one({"flavourID": flavour_id})
                return json.dumps({"message": 'Flavour ' + flavour_id + ' deleted'}), 201
        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": 'Delete fails'}), 401

    @app.route('/listFlavours', methods=['GET'])
    @jwt_required
    def recv_list_flavours():
        # if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
        #     httpThread.app.logger.warn('%s tried to get flavour list', get_jwt_identity())
        #     return json.dumps({"message": "operation not allowed"}), 401
        flavours = db[flavour_collection].find({}, {"_id": 0})
        return Response(dumps(flavours), 200, mimetype='application/json'), 200

    @app.route('/inspectTenant', methods=['POST'])
    @jwt_required
    def recv_inspect_tenant():
        # print(json.dumps(request.json))
        try:
            tenant_id = request.json.get("tenantID", get_jwt_identity())
            print(tenant_id)
            # if not User(get_jwt_identity()).check_user_permission(db, user_collection, tenant_id):
            #     httpThread.app.logger.warn('%s tried to inspect the tenant (%s)', get_jwt_identity(), tenant_id)
            #     return json.dumps({"message": "operation not allowed"}), 401
            res = {'vSilos': json.loads(dumps(db[v_silo_collection].find({"tenantID": tenant_id}, {"_id": 0}))),
                   'vThings': json.loads(dumps(db[v_thing_collection].find({"tenantID": tenant_id}, {"_id": 0})))}
            return Response(json.dumps(res), 200, mimetype='application/json')
        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": 'Inspect fails'}), 401

    @app.route('/inspectVirtualSilo', methods=['POST'])
    @jwt_required
    def recv_inspect_virtual_silo():
        # print ("enter create, POST body: "+str(jres))
        try:
            vsilo_id = request.json.get("vSiloID", None)
            tenant_id = str(vsilo_id).split("_")[0]
            if not User(get_jwt_identity()).check_user_permission(db, user_collection, tenant_id):
                httpThread.app.logger.warn('%s tried to inspect silo for the tenant (%s)', get_jwt_identity(),
                                           tenant_id)
                return json.dumps({"message": "operation not allowed"}), 401
            res = {'vSilo': json.loads(dumps(db[v_silo_collection].find_one({"vSiloID": vsilo_id}, {"_id": 0}))),
                   'vThings': json.loads(dumps(db[v_thing_collection].find({"vSiloID": vsilo_id}, {"_id": 0})))}
            return Response(json.dumps(res), 200, mimetype='application/json')

        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": 'Inspect fails'}), 401

    @app.route('/inspectThingVisor', methods=['POST'])
    @jwt_required
    def recv_inspect_thing_visor():
        # print ("enter create, POST body: "+str(jres))
        try:
            thingvisor_id = request.json.get("thingVisorID", None)
            if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
                httpThread.app.logger.warn('%s tried to inspect the thingVisor %s', get_jwt_identity(), thingvisor_id)
                return json.dumps({"message": "operation not allowed"}), 401
            res = json.loads(dumps(db[thing_visor_collection].find({"thingVisorID": thingvisor_id}, {"_id": 0})))
            return Response(json.dumps(res), 200, mimetype='application/json')

        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": 'Inspect fails'}), 401

    @app.route('/inspectFlavour', methods=['POST'])
    @jwt_required
    def recv_inspect_flavour():
        try:
            flavour_id = request.json.get("flavourID", None)
            if not User(get_jwt_identity()).check_admin_permission(db, user_collection):
                httpThread.app.logger.warn('%s tried to inspect the flavour %s', get_jwt_identity(), flavour_id)
                return json.dumps({"message": "operation not allowed"}), 401
            res = json.loads(dumps(db[flavour_collection].find({"flavourID": flavour_id}, {"_id": 0})))
            return Response(json.dumps(res), 200, mimetype='application/json')

        except Exception:
            print(traceback.format_exc())
            return json.dumps({"message": 'Inspect fails'}), 401


# Follow the definition of mqtt callbacks
def on_message_destroy_TV_ack_on_docker(jres):
    try:
        tv_id = jres["thingVisorID"]
        tv_entry = db[thing_visor_collection].find_one_and_delete({"thingVisorID": tv_id})
        container_id = tv_entry["containerID"]
        if not tv_entry["debug_mode"]:
            if docker_client.containers.get(container_id).kill() is not None:
                print('ERROR:\tDelete fails')
            # docker_client.images.remove(tv_entry["imageName"], force=True)
            # uncomment previous line to remove the docker image too

        # Remove mqtt subscription to TV control topics
        mqttc.message_callback_remove(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)
        mqttc.unsubscribe(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)
        return
    except Exception:
        print(traceback.format_exc())

def on_message_destroy_TV_ack_on_kubernetes(jres):
    try:
        tv_id = jres["thingVisorID"]
        tv_entry = db[thing_visor_collection].find_one_and_delete({"thingVisorID": tv_id})
        if not tv_entry["debug_mode"]:

            print("Delete Deployment %s" % tv_id)
            deployment_name = tv_entry["deploymentName"]
            service_name = tv_entry["serviceName"]

            if deployment_name != "" and deployment_name != None:
                print("stopping deployment: %s, and service: %s" % (deployment_name, service_name))
                if not k8s.delete_deployment(namespace=working_namespace, name=deployment_name)[0]:
                    print('ERROR:\tDelete fails deployment')
                    return json.dumps({"message": 'Error on ThingVisor destroy, problem with delete deployment: ' + deployment_name}), 401

            if service_name != "" and service_name != None:
                if not k8s.delete_service(namespace=working_namespace, name=service_name)[0]:
                    print('ERROR:\tDelete fails service')
                    return json.dumps({"message": 'Error on ThingVisor destroy, problem with delete service: ' + service_name}), 401

        # Remove mqtt subscription to TV control topics
        mqttc.message_callback_remove(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)
        mqttc.unsubscribe(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)
        return
    except Exception:
        print(traceback.format_exc())

def on_message_destroy_v_silo_ack_on_docker(jres):
    try:
        v_silo_id = jres["vSiloID"]
        silo_entry = db[v_silo_collection].find_one({"vSiloID": v_silo_id})

        if silo_entry is None:
            print('Delete fails - tenantID or vSiloID not valid')
            return

        container_id = silo_entry["containerID"]
        if not container_id == "debug_mode":
            print("stopping docker container with ID: " + container_id)

            if docker_client.containers.get(container_id).kill() is not None:
                print('ERROR:\tDelete fails')
                return

        thing_res = db[v_thing_collection].delete_many({"vSiloID": v_silo_id})
        silo_res = db[v_silo_collection].delete_many({"vSiloID": v_silo_id})
    except docker.errors.NotFound:
        thing_res = db[v_thing_collection].delete_many({"vSiloID": v_silo_id})
        silo_res = db[v_silo_collection].delete_many({"vSiloID": v_silo_id})
        print("WARNING: Could not find the Docker container for the silo")
    except Exception as ex:
        db[v_thing_collection].delete_many({"vSiloID": v_silo_id})
        db[v_silo_collection].delete_many({"vSiloID": v_silo_id})
        print(traceback.format_exc())
        print('Destroy fails')

    if silo_res.deleted_count > 0:
        # Remove mqtt subscription to silo control topics
        mqttc.message_callback_remove(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)
        mqttc.unsubscribe(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)
        print('destroyed ' + str(silo_res.deleted_count) + ' silos')
        print('destroyed ' + str(thing_res.deleted_count) + ' vThings')
        print('Silo ' + v_silo_id + ' destroyed')
        return
    else:
        print('VSilo destroy fails with vSiloID ' + v_silo_id)
        return


def on_message_destroy_v_silo_ack_on_kubernetes(jres):
    try:
        v_silo_id = jres["vSiloID"]
        silo_entry = db[v_silo_collection].find_one({"vSiloID": v_silo_id})

        if silo_entry is None:
            print('Delete fails - tenantID or vSiloID not valid')
            return

        deployment_name = silo_entry["deploymentName"]
        service_name = silo_entry["serviceName"]
        if not deployment_name == "" or service_name == "":
            print("stopping deployment: %s, and service: %s" % (deployment_name, service_name))
            if not k8s.delete_deployment(namespace=working_namespace, name=deployment_name)[0]:
                print('ERROR:\tDelete fails')
                return json.dumps(
                    {"message": 'Error on silo destroy, problem with delete deployment: ' + deployment_name}), 401
            if not k8s.delete_service(namespace=working_namespace, name=service_name)[0]:
                print('ERROR:\tDelete fails')
                return json.dumps(
                    {"message": 'Error on silo destroy, problem with delete service: ' + service_name}), 401

        thing_res = db[v_thing_collection].delete_many({"vSiloID": v_silo_id})
        silo_res = db[v_silo_collection].delete_many({"vSiloID": v_silo_id})

    except Exception as ex:
        thing_res = db[v_thing_collection].delete_many({"vSiloID": v_silo_id})
        silo_res = db[v_silo_collection].delete_many({"vSiloID": v_silo_id})
        print(traceback.format_exc())
        print('Destroy fails', ex)
    if silo_res.deleted_count > 0:
        # Remove mqtt subscription to silo control topics
        mqttc.message_callback_remove(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)
        mqttc.unsubscribe(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)
        print('destroyed ' + str(silo_res.deleted_count) + ' silos')
        print('destroyed ' + str(thing_res.deleted_count) + ' vThings')
        print('Silo ' + v_silo_id + ' destroyed')
        return
    else:
        print('VSilo destroy fails with vSiloID ' + v_silo_id)
        return


def on_message_create_vThing(jres):
    try:
        v_thing = jres["vThing"]
        tv_id = jres["thingVisorID"]

        # check TV status, must be "running"
        if (db[thing_visor_collection].find_one(
                {"thingVisorID": tv_id}, {"status": 1, "_id": 0}))["status"] != STATUS_RUNNING:
            print("WARNING Add fails - thing Visor " + tv_id + " is not ready")
            return

        # Check if vThing already exists
        if db[thing_visor_collection].count({"vThings.id": v_thing["id"]}) != 0:
            print("WARNING Add fails - vThingID '" + v_thing["id"] + "' already in use")
            return

        # Control vThing ID: thingVisor ID must be prefix of vThing ID
        if v_thing["id"].split("/")[0] != tv_id:
            print("WARNING Add fails - vThingID '" + v_thing["id"] + "' not valid")
            return

        db[thing_visor_collection].update_one({"thingVisorID": tv_id}, {"$addToSet": {"vThings": v_thing}})
        v_thing_id = v_thing["id"]
        mqttc.message_callback_add(v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix,
                                   on_v_thing_out_control_message)
        mqttc.subscribe(v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix)
    except Exception:
        print(traceback.format_exc())


def on_message_delete_vThing(jres):
    try:
        v_thing_id = jres["vThingID"]
        tv_id = v_thing_id.split("/")[0]
        db[v_thing_collection].delete_many({"vThingID": v_thing_id})
        # check TV status, must be "running" or "stopping"
        if (db[thing_visor_collection].find_one(
                {"thingVisorID": tv_id}, {"status": 1, "_id": 0}))["status"] not in [STATUS_RUNNING, STATUS_STOPPING]:
            print("WARNING Add fails - thing Visor " + tv_id + " is not ready")
            return

        # Check if vThing ID exists in the system database
        if db[thing_visor_collection].count({"vThings.id": v_thing_id}) == 0:
            print("WARNING Delete fails - vThingID '" + v_thing_id + "' does not exists")
            return "Delete fails - vThingID '" + v_thing_id + "' does not exists", 409

        tv_v_things = db[thing_visor_collection].find_one({"thingVisorID": tv_id}, {"_id": 0, "vThings": 1})
        if tv_v_things is not None:
            for v_thing in tv_v_things['vThings']:
                if v_thing["id"] == v_thing_id:
                    if len(tv_v_things["vThings"]) == 1:
                        tv_v_things['vThings'] = []
                    else:
                        tv_v_things['vThings'].remove(v_thing)
                    break
            db[thing_visor_collection].update_one({"thingVisorID": tv_id},
                                                  {"$set": {"vThings": tv_v_things['vThings']}})
        else:
            print("ERROR! tv_v_things is None")
        mqttc.message_callback_remove(v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix)
        mqttc.unsubscribe(v_thing_prefix + '/' + v_thing_id + '/' + out_control_suffix)
    except Exception:
        print(traceback.format_exc())


def on_tv_out_control_message(mosq, obj, msg):
    try:
        print("on_tv_out_control_message")
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
        jres = json.loads(payload.replace("\'", "\""))
        command = jres["command"]
        if command == "createVThing":
            on_message_create_vThing(jres)
        elif command == "destroyTVAck":
            on_message_destroy_TV_ack(jres)

    except Exception:
        print(traceback.format_exc())


def on_silo_out_control_message(mosq, obj, msg):
    try:
        print("on_silo_out_control_message")
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
        jres = json.loads(payload.replace("\'", "\""))
        command = jres["command"]
        if command == "destroyVSiloAck":
            on_message_destroy_v_silo_ack(jres)
    except Exception:
        print(traceback.format_exc())


def on_master_controller_in_message(mosq, obj, msg):
    try:
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
        # jres = json.loads(payload.replace("\'", "\""))
        # TODO command type switch case
    except Exception:
        print(traceback.format_exc())


def on_v_thing_out_control_message(mosq, obj, msg):
    try:
        payload = msg.payload.decode("utf-8", "ignore")
        print(msg.topic + " " + str(payload))
        jres = json.loads(payload.replace("\'", "\""))
        command = jres["command"]
        if command == "deleteVThing":
            on_message_delete_vThing(jres)
    except Exception:
        print(traceback.format_exc())


def mqtt_subscriptions_restore():
    try:
        for thing_visor in db[thing_visor_collection].find({}, {"_id": 0, "thingVisorID": 1}):
            tv_id = thing_visor["thingVisorID"]
            # Remove and add mqtt subscription to TV control topics
            mqttc.message_callback_remove(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)
            mqttc.unsubscribe(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)
            time.sleep(0.1)
            mqttc.message_callback_add(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix,
                                       on_tv_out_control_message)
            mqttc.subscribe(thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)
            print("restored sub " + thing_visor_prefix + '/' + tv_id + '/' + out_control_suffix)

            # Remove and add mqtt subscription to virtual Things control topics
            mqttc.message_callback_remove(v_thing_prefix + '/' + tv_id + '/+/' + out_control_suffix)
            mqttc.unsubscribe(v_thing_prefix + '/' + tv_id + '/+/' + out_control_suffix)
            time.sleep(0.1)
            mqttc.message_callback_add(v_thing_prefix + '/' + tv_id + '/+/' + out_control_suffix,
                                       on_v_thing_out_control_message)
            mqttc.subscribe(v_thing_prefix + '/' + tv_id + '/+/' + out_control_suffix)
            print("restored sub " + v_thing_prefix + '/' + tv_id + '/+/' + out_control_suffix)

        for v_silo in db[v_silo_collection].find({}, {"_id": 0, "vSiloID": 1}):
            v_silo_id = v_silo["vSiloID"]
            # Remove and add mqtt subscription to silo control topics
            mqttc.message_callback_remove(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)
            mqttc.unsubscribe(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)
            time.sleep(0.1)
            mqttc.message_callback_add(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix,
                                       on_silo_out_control_message)
            mqttc.subscribe(v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)
            print("restored sub " + v_silo_prefix + '/' + v_silo_id + '/' + out_control_suffix)
        print("subscriptions restored")
    except Exception:
        print(traceback.format_exc())
        return "Error on subscriptions restore"


class mqttThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Thread mqtt started")
        global mqttc

        mqtt_broker_connection()

        mqttc.message_callback_add(master_controller_prefix + "/" + in_control_suffix, on_master_controller_in_message)
        mqttc.subscribe(master_controller_prefix + "/" + in_control_suffix)
        mqtt_subscriptions_restore()
        mqttc.loop_forever()
        print("Thread '" + self.name + " closed")


def dockerImageExist(name):
    if ":" not in name:
        name = name + ":latest"
    try:
        docker_images = docker_client.images.list()
        for image in docker_images:
            al = image.attrs['RepoTags']
            for x in al:
                if x == name:
                    return True
        return False
    except:
        return False


def db_tv_check_on_docker():
    try:
        for thing_visor in db[thing_visor_collection].find({}, {"_id": 0}):
            tv_id = thing_visor["thingVisorID"]
            if "containerID" in thing_visor.keys():
                container_id = thing_visor["containerID"]
            else:
                db[thing_visor_collection].delete_many({"thingVisorID": tv_id})
                continue

            print("tv_id", tv_id)
            # Check if thingVisor's docker container is running
            if docker_client.containers.get(container_id).status != "running":
                db[thing_visor_collection].delete_many({"containerID": container_id})
                print("removed thing Visor with id " + tv_id + " from system database")
    except docker.errors.NotFound:
        db[thing_visor_collection].delete_many({"thingVisorID": tv_id})
        print("removed thing Visor with id " + tv_id + " from system database")
    # except Exception as err:
    #     db[thing_visor_collection].delete_many({"thingVisorID": tv_id})
    #     print("ERROR", err)
    #     print("removed thing Visor with id " + tv_id + " from system database")


def db_tv_check_on_kubernetes():
    api_instance = kubernetes.client.AppsV1Api()
    try:
        for thing_visor in db[thing_visor_collection].find({}, {"_id": 0}):
            tv_id = thing_visor["thingVisorID"]
            deployment_name = thing_visor["deploymentName"]
            api_response = api_instance.read_namespaced_deployment(deployment_name, working_namespace)

            if api_response.status == 404:
                db[thing_visor_collection].delete_many({"thingVisorID": tv_id})
                print("removed thing Visor with id " + tv_id + " from system database")
            else:
                if api_response.status.available_replicas is None or api_response.status.available_replicas < 1:
                    db[thing_visor_collection].delete_many({"thingVisorID": tv_id})
                    print("removed thing Visor with id " + tv_id + " from system database")

    except ApiException as err:
        # print("Exception when calling AppsV1Api->read_namespaced_deployment: %s\n" % e)
        api_response = err
        db[thing_visor_collection].delete_many({"thingVisorID": tv_id})
    except Exception as err:
        print("Error:", err)
        db[thing_visor_collection].delete_many({"thingVisorID": tv_id})


def db_silo_check_on_docker():
    try:
        for silo in db[v_silo_collection].find({}, {"_id": 0}):
            v_silo_id = silo["vSiloID"]
            container_id = silo["containerID"]
            # Check if virtual Silo's docker container is running
            if docker_client.containers.get(container_id).status != "running":
                db[v_silo_collection].delete_many({"containerID": container_id})
                print("removed virtual Silo with id " + v_silo_id + " from system database")
    except docker.errors.NotFound:
        db[v_silo_collection].delete_many({"vSiloID": v_silo_id})
        print("removed virtual Silo with id " + v_silo_id + " from system database")


def db_silo_check_on_kubernetes():
    api_instance = kubernetes.client.AppsV1Api()
    for silo in db[v_silo_collection].find({}, {"_id": 0}):
        v_silo_id = silo["vSiloID"]
        deployment_name = silo["deploymentName"]
        try:
            api_response = api_instance.read_namespaced_deployment(deployment_name, working_namespace)
        except ApiException as err:
            # print("Exception when calling AppsV1Api->read_namespaced_deployment: %s\n" % e)
            api_response = err

        if api_response.status == 404:
            db[v_silo_collection].delete_many({"vSiloID": v_silo_id})
            print("removed virtual Silo with id " + v_silo_id + " from system database")
        else:
            if api_response.status.available_replicas is None or api_response.status.available_replicas < 1:
                db[v_silo_collection].delete_many({"v_silo_id": v_silo_id})
                print("removed virtual Silo with id " + v_silo_id + " from system database")

def db_flavour_check():
    try:
        for flavour in db[flavour_collection].find({}, {"_id": 0}):
            flavour_id = flavour["flavourID"]
            if flavour["status"] == STATUS_ERROR or flavour["status"] == STATUS_PENDING:
                db[flavour_collection].delete_many({"flavourID": flavour_id})
    except Exception as err:
        print("Error", err)
        db[flavour_collection].delete_many({"flavourID": flavour_id})

def database_integrity_check_on_docker():
    db_tv_check_on_docker()
    db_silo_check_on_docker()
    db_flavour_check()


def database_integrity_check_on_kubernetes():
    db_tv_check_on_kubernetes()
    db_silo_check_on_kubernetes()
    db_flavour_check()

def mqtt_broker_connection_on_docker():
    mqttc.connect(MQTT_control_broker_IP, MQTT_control_broker_port, 30)


def mqtt_broker_connection_on_kubernetes():
    if not settings.master_controller_in_container:
        MQTT_control_broker_node_port = k8s.discover_mqtt_nodeport_debug(settings.MQTT_control_broker_svc_name,
                                                                         working_namespace)
        # Impossible to find NodePort of MQTT broker
        if not MQTT_control_broker_node_port:
            print("ERROR: broker MQTT not found in k8s cluster")
            sys.exit(0)

        # Broker mqtt inside the cluster with nodePort (MQTT_control_broker_port_debug)
        mqttc.connect("localhost", MQTT_control_broker_node_port, 30)
    else:
        mqttc.connect(MQTT_control_broker_IP, MQTT_control_broker_port, 30)



if __name__ == '__main__':
    global working_namespace

    if container_manager == "DOCKER":
        create_virtual_silo = create_virtual_silo_on_docker
        destroy_virtual_silo = destroy_virtual_silo_on_docker
        create_thing_visor = create_thing_visor_on_docker
        delete_thing_visor = delete_thing_visor_on_docker
        get_deploy_zone = get_deploy_zone_on_docker
        add_flavour = add_flavour_on_docker
        database_integrity = database_integrity_check_on_docker
        mqtt_broker_connection = mqtt_broker_connection_on_docker
        on_message_destroy_v_silo_ack = on_message_destroy_v_silo_ack_on_docker
        on_message_destroy_TV_ack = on_message_destroy_TV_ack_on_docker


        docker_client = docker.from_env()

        # Database connection
        mongocnt = docker_client.containers.get("mongo-container")
        if mongocnt.status != "running":
            print("ERROR: database is not running... exit")
            sys.exit(0)
        mongo_IP = mongocnt.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
        mongo_client = MongoClient('mongodb://' + mongo_IP + ':' + str(mongo_port) + '/')

    elif container_manager == "KUBERNETES":
        # Set Kubernetes configuration
        if settings.master_controller_in_container:
            config.load_incluster_config()
        else:
            config.load_kube_config()

        working_namespace = settings.working_namespace

        create_virtual_silo = create_virtual_silo_on_kubernetes
        destroy_virtual_silo = destroy_virtual_silo_on_kubernetes
        create_thing_visor = create_thing_visor_on_kubernetes
        delete_thing_visor = delete_thing_visor_on_kubernetes
        get_deploy_zone = get_deploy_zone_on_kubernetes
        add_flavour = add_flavour_on_kubernetes
        database_integrity = database_integrity_check_on_kubernetes
        mqtt_broker_connection = mqtt_broker_connection_on_kubernetes
        on_message_destroy_v_silo_ack = on_message_destroy_v_silo_ack_on_kubernetes
        on_message_destroy_TV_ack = on_message_destroy_TV_ack_on_kubernetes

        configuration = kubernetes.client.Configuration()
        kubernetes_api_client = kubernetes.client.CoreV1Api()


        # Database connection
        if not settings.master_controller_in_container:
            mongo_port_local = k8s.discover_mongodb_nodeport_debug(settings.mongodb_svc_name, working_namespace)
            # if mongo_port_local port is False, I don't discover the DB port
            if not mongo_port_local:
                print("ERROR: database is not running in k8s cluster... exit")
                sys.exit(0)
            mongo_client = MongoClient('mongodb://' + "localhost" + ':' + str(mongo_port_local) + '/')
        else:
            mongo_client = MongoClient('mongodb://' + mongo_IP + ':' + str(mongo_port) + '/')


    else:
        print("Error: Unsupported container manager")
        sys.exit(0)

    db = mongo_client[db_name]

    if not db[user_collection].find().count() > 0:
        print("Inserted DB_setup information")
        db[user_collection].insert(db_setup.mongo_db_setup)

    database_integrity()

    http_thread = httpThread()
    mqtt_thread = mqttThread()

    http_thread.start()
    mqtt_thread.start()
