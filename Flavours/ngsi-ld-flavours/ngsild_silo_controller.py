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


# Fed4IoT virtual Silo controller for NGSI-LD brokers

import sys
import os

# lets import the common functionality from the parent (..) or current (.) folder
sys.path.append(os.path.abspath("."))
import common_vsilo_functionality as common

import traceback
import json

import F4Ingsild



############# BEGIN Broker Functions ############

def init_Broker(broker_port):
    # Try to keep confined to the broker-specific module the info to contact the specific broker
    global brokerurl
    BROKER_IP = "127.0.0.1"
    BROKER_PORT = broker_port

    # Broker settings
    ngsildversion = "v1"
    ngsildbase = "ngsi-ld"
    brokerurl = "http://" + BROKER_IP + ":" + str(BROKER_PORT) + "/" + ngsildbase + "/" + ngsildversion
    print("Broker initialized at " + brokerurl)


# This creates an empty vThing given a v_thing_id
def create_vThing_on_Broker(v_thing_id):
    # vThings have no representation as NGSI-LD self-standing entities.
    # We do not create any data structure in the NGSI-LD broker to capture the vThing.
    # For instance in case of oneM2M, this function creates the "mother" ApplicationEntity
    # in the Mobius broker, and creates a default access control policy for it and
    # binds the policy with the new AE
    print("    on Broker vthing CREATE is dummy for vThing ID " + v_thing_id)
    return True


# This removes an empty vThing given a v_thing_id
def remove_vThing_from_Broker(v_thing_id):
    # vThings have no representation as NGSI-LD self-standing entities.
    # We do not create any data structure in the NGSI-LD broker to capture the vThing.
    # For instance in case of oneM2M, this function removes the "mother" ApplicationEntity
    # in the Mobius broker
    print("    on Broker vthing REMOVE is dummy for vThing ID " + v_thing_id)
    return True


# Here we receive a vthing id and the broker-specific hook to
# remove the entity from the broker
def delete_entity_under_vThing_on_Broker(v_thing_id, entity_id):
    # lets now delete the entity from the Broker
    try:
        response = F4Ingsild.delete_entity(brokerurl, entity_id)
        return True
    except Exception:
        traceback.print_exc()
        print("Exception while REST DELETE of Entity " + entity_id + " on vThing " + v_thing_id)
    return False

def batch_entity_delete_under_vThing_on_Broker(v_thing_id, entities_ids):
    # lets now delete the entity from the Broker
    try:
        return F4Ingsild.batch_entity_delete(brokerurl, entities_ids)
    except Exception:
        traceback.print_exc()
        print("Exception while REST BATCH_DELETE of entities on vThing " + v_thing_id)
    return []

# This method allows us to retrieve all the entities under
# a specific vThing by querying them for v_thing_id
def get_all_entities_under_vThing_on_Broker(v_thing_id):
    try:
        data = F4Ingsild.get_entities_by_vThing(brokerurl, v_thing_id)
        print("ENTITIES ", data)
        return data
    except Exception:
        traceback.print_exc()
        print("Exception while REST GET of Entities on vThing " + v_thing_id)
    return []



# Here we receive a data item, which is composed of "data" and "meta" fields
def add_or_modify_entity_under_vThing_on_Broker(v_thing_id, entity):
    # lets add the vThingID as a property into each entity
    entity['generatedByVThing'] = {'type':'Property','value':v_thing_id}

    # Whenever an entity doesn't have a @context field, we provide it as an empty list.
    if '@context' not in entity:
        entity['@context'] = []

    # if the "commands" property exists,
    # foreach command in the array, create 3 additional properties in entity:
    # command, command-status, command-result 
    # then vsilo controller subscribes itself for this entity to the broker,
    # using the F4Ingsild.py subscribe function
    # and using the self nuri = "http://localhost:5555/receive_notification_from_broker"
    if 'commands' in entity:
        for command in entity['commands']['value']:
            #print(command)
            entity[command]={"type": "Property", "value": {}}
            entity[command+"-status"]={"type": "Property", "value": {}}
            entity[command+"-result"]={"type": "Property", "value": {}}

            # subscribe to broker to receive notifications
            print("Subscribing to broker to receive notifications...")
            entity_id_to_subscribe = entity['id']
            entity_type = entity['type']
            entity_context = entity['@context']
            notification_URI = "http://localhost:5555/receive_notification_from_broker/"+command
            try:
                status = F4Ingsild.subscribe_to_entity(brokerurl, entity_id_to_subscribe, entity_type, entity_context, notification_URI, [command])
            except Exception:
                traceback.print_exc()
                print("Exception while subscribing to broker " + entity['id'])


    ### HOPE THE FOLLOWING WILL NOT NEEDED ANYMORE, NGSI-LD HAS BEEN FIXED? ###
    # in order to adapt to a NGSI-LD mis-behaving, we have
    # to change the value of the entity's GeoProperties into a string,
    # hence we need to escape the quote and make it a string
    # for attribute_name, attribute_value in entity.items():
    #   # let's find wether this attribute of the object is a GeoProperty
    #   # by examining its "type", if it has one
    #   if isinstance(attribute_value, dict):
    #     try:
    #       type_of_the_attribute = attribute_value['type']
    #       if type_of_the_attribute == "GeoProperty":
    #         try:
    #           value_of_the_geo_property = attribute_value['value']
    #           value_of_the_geo_property_as_string = json.dumps(value_of_the_geo_property)
    #           value_of_the_geo_property_as_escaped_string = value_of_the_geo_property_as_string.replace('"', '\"').replace('\n', '\\n')
    #           # turn it into a string
    #           attribute_value['value'] = value_of_the_geo_property_as_escaped_string
    #         except Exception:
    #           print("GeoProperty malformed? no value field??: " + entity['id'])
    #     except Exception:
    #       print("entity malformed? no type field??: " + entity['id'])

    # lets now push the entity to the Broker
    try:
        response = F4Ingsild.overwrite_or_append_or_create_entity(brokerurl, entity)
        return True
    except Exception:
        traceback.print_exc()
        print("Exception while REST POST of Entity " + entity['id'])

    return False


# Here we receive a group of data items, which are composed of "data" and "meta" fields
def batch_add_or_modify_entity_under_vThing_on_Broker(v_thing_id, entities):
    for entity in entities:
        # lets add the vThingID as a property into each entity
        entity['generatedByVThing'] = {'type':'Property','value':v_thing_id}

        # Whenever an entity doesn't have a @context field, we provide it as an empty list.
        if '@context' not in entity:
            entity['@context'] = []

        # if the "commands" property exists,
        # foreach command in the array, create 3 additional properties in entity:
        # command, command-status, command-result 
        # then vsilo controller subscribes itself for this entity to the broker,
        # using the F4Ingsild.py subscribe function
        # and using the self nuri = "http://localhost:5555/receive_notification_from_broker"
        if 'commands' in entity:
            for command in entity['commands']['value']:
                #print(command)
                entity[command]={"type": "Property", "value": {}}
                entity[command+"-status"]={"type": "Property", "value": {}}
                entity[command+"-result"]={"type": "Property", "value": {}}

                # subscribe to broker to receive notifications
                print("Subscribing to broker to receive notifications...")
                try:
                    entity_id_to_subscribe = entity['id']
                    entity_type = entity['type']
                    # Exctract the @context from the entity to put it in the subscription.
                    entity_context = entity['@context']
                    notification_URI = "http://localhost:5555/receive_notification_from_broker/"+command
                    status = F4Ingsild.subscribe_to_entity(brokerurl, entity_id_to_subscribe, entity_type, entity_context, notification_URI, [command])
                except Exception:
                    traceback.print_exc()
                    print("Exception while subscribing to broker " + entity['id'])

    ### HOPE THE FOLLOWING WILL NOT NEEDED ANYMORE, NGSI-LD HAS BEEN FIXED? ###
    # in order to adapt to a NGSI-LD mis-behaving, we have
    # to change the value of the entity's GeoProperties into a string,
    # hence we need to escape the quote and make it a string
    # for attribute_name, attribute_value in entity.items():
    #   # let's find wether this attribute of the object is a GeoProperty
    #   # by examining its "type", if it has one
    #   if isinstance(attribute_value, dict):
    #     try:
    #       type_of_the_attribute = attribute_value['type']
    #       if type_of_the_attribute == "GeoProperty":
    #         try:
    #           value_of_the_geo_property = attribute_value['value']
    #           value_of_the_geo_property_as_string = json.dumps(value_of_the_geo_property)
    #           value_of_the_geo_property_as_escaped_string = value_of_the_geo_property_as_string.replace('"', '\"').replace('\n', '\\n')
    #           # turn it into a string
    #           attribute_value['value'] = value_of_the_geo_property_as_escaped_string
    #         except Exception:
    #           print("GeoProperty malformed? no value field??: " + entity['id'])
    #     except Exception:
    #       print("entity malformed? no type field??: " + entity['id'])

    # lets now push the entity to the Broker
    try:
        return F4Ingsild.batch_entity_upsert(brokerurl, entities)
    except Exception:
        traceback.print_exc()
        print("Exception while REST POST of Entity " + entity['id'])

    return []

############# END Broker Functions ############


# Lets tell the common module who we are, so that it can import us,
# and programmatically bind the above functions, specifically implemented
# with the same signature by each silo controller.
# Use the following dot notation if we are in a different folder than the common_vsilo_functionality
#common.start_silo_controller("scorpio-flavour.ngsild_silo_controller")
# Otherwise just give our name
common.start_silo_controller("ngsild_silo_controller")
