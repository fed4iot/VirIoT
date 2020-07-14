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


# Fed4IoT virtual Silo controller for NGSI-LD brokers (specifically Stellio Broker from EGM)

import sys
import os

# lets import the common functionality from the parent (..) or current (.) folder
sys.path.append(os.path.abspath("."))
import common_vsilo_functionality as common

import traceback
import json

import F4Ingsild



############# BEGIN Stellio Functions ############

def init_Broker():
    # Try to keep confined to the broker-specific module the info to contact the specific broker
    global brokerurl
    STELLIO_IP = "127.0.0.1"
    STELLIO_PORT = 8080
    # Stellio settings
    ngsildversion = "v1"
    ngsildbase = "ngsi-ld"
    brokerurl = "http://" + STELLIO_IP + ":" + str(STELLIO_PORT) + "/" + ngsildbase + "/" + ngsildversion
    print("Stellio Broker initialized at " + brokerurl)


# This creates an empty vThing given a v_thing_id
def create_vThing_on_Broker(v_thing_id):
    # vThings have no representation as NGSI-LD self-standing entities.
    # We do not create any data structure in the NGSI-LD broker to capture the vThing.
    # For instance in case of oneM2M, this function creates the "mother" ApplicationEntity
    # in the Mobius broker, and creates a default access control policy for it and
    # binds the policy with the new AE
    print("    on Broker Stellio vthing CREATE is dummy for vThing ID " + v_thing_id)
    return True


# This removes an empty vThing given a v_thing_id
def remove_vThing_from_Broker(v_thing_id):
    # vThings have no representation as NGSI-LD self-standing entities.
    # We do not create any data structure in the NGSI-LD broker to capture the vThing.
    # For instance in case of oneM2M, this function removes the "mother" ApplicationEntity
    # in the Mobius broker
    print("    on Broker Stellio vthing REMOVE is dummy for vThing ID " + v_thing_id)
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
    entity['generatedByVThing'] = {'type':'Relationship','object':v_thing_id.replace("/", ":")}

    # lets now push the entity to the Broker
    try:
      response = F4Ingsild.append_or_create_entity(brokerurl, entity)
      return True
    except Exception:
      traceback.print_exc()
      print("Exception while REST POST of Entity " + entity['id'])

    return False

############# END Stellio Functions ############


# Lets tell the common module who we are, so that it can import us,
# and programmatically bind the above functions, specifically implemented
# with the same signature by each silo controller.
# Use the following dot notation if we are in a different folder than the common_vsilo_functionality
#common.start_silo_controller("stellio-flavour.stellio_silo_controller")
# Otherwise just give our name
common.start_silo_controller("stellio_silo_controller")
