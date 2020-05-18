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



############# BEGIN NGSI-LD Functions ############

def init_Broker():
    # Try to keep confined to the broker-specific module the info to contact the specific broker
    global brokerurl
    NGSILD_IP = "127.0.0.1"
    NGSILD_PORT = 9090
    # NGSI-LD settings
    ngsildversion = "v1"
    ngsildbase = "ngsi-ld"
    brokerurl = "http://" + NGSILD_IP + ":"+str(NGSILD_PORT) + "/" + ngsildbase + "/" + ngsildversion
    print("NGSI-LD Broker initialized at " + brokerurl)


# This creates an empty vThing given a v_thing_id
def create_vThing_on_Broker(v_thing_id):
    # vThings have no representation as NGSI-LD self-standing entities.
    # We do not create any data structure in the NGSI-LD broker to capture the vThing.
    # For instance in case of oneM2M, this function creates the "mother" ApplicationEntity
    # in the Mobius broker, and creates a default access control policy for it and
    # binds the policy with the new AE
    print("    on Broker NGSI-LD vthing CREATE is dummy for vThing ID " + v_thing_id)
    return True


# This removes an empty vThing given a v_thing_id
def remove_vThing_from_Broker(v_thing_id):
    # vThings have no representation as NGSI-LD self-standing entities.
    # We do not create any data structure in the NGSI-LD broker to capture the vThing.
    # For instance in case of oneM2M, this function removes the "mother" ApplicationEntity
    # in the Mobius broker
    print("    on Broker NGSI-LD vthing REMOVE is dummy for vThing ID " + v_thing_id)
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


# Here we receive a data item, which is composed of "data" and "meta" fields
def add_entity_under_vThing_on_Broker(v_thing_id, entity):
    # lets add the vThingID as a property into each entity
    entity['generatedByVThing'] = {'type':'Relationship','object':v_thing_id}
    
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
      response = F4Ingsild.append_or_create_entity(brokerurl, entity)
      return True
    except Exception:
      traceback.print_exc()
      print("Exception while REST POST of Entity " + entity['id'])
    
    return False

############# END NGSI-LD Functions ############


# Lets tell the common module who we are, so that it can import us,
# and programmatically bind the above functions, specifically implemented
# with the same signature by each silo controller.
# Use the following dot notation if we are in a different folder than the common_vsilo_functionality
#common.start_silo_controller("ngsild-flavour.ngsild_silo_controller")
# Otherwise just give our name
common.start_silo_controller("ngsild_silo_controller")


