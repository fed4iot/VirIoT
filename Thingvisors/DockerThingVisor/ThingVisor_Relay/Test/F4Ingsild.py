import requests
import json

# Append (and overwrite existing) attributes of and entity.
# Create the NGSI-LD Entity, if it does not exist
def append_or_create_entity(url, entity):
    entities_end_point = "/entities/"
    entities_url = url + entities_end_point

    # extract the identifier to construct the last part of the url
    eid = entity['id']
    payload = json.dumps(entity)
    headers = {
      'Content-Type': "application/ld+json",
      'Accept': "application/json"
    }
    # Lets try to call the Append Attributes endpoint, with overwrite enabled (default)
    change_attributes_url = entities_url + eid + "/attrs"
    response = requests.request("POST", change_attributes_url, data=payload, headers=headers)

    print("POSTING to "+change_attributes_url)

    if (response.status_code == 404):
      # Lets try to call the Create Entity endpoint
      print("- entity was not there:" + eid)
      response = requests.request("POST", entities_url, data=payload, headers=headers)
      print("EPOSTING to "+entities_url)
      print("EPOSTING data "+payload)
      print("EPOSTING response "+str(response.status_code))
    if(response.status_code > 299 and response.status_code != 409): #409 is AlreadyExists 
      print("anaomaly response of APPEND_OR_CREATE_ENTITY is "+str(response.status_code))
      print("ATTR POSTING to "+change_attributes_url)
      print("DATA "+payload)
    return (response.status_code)


# Delete entity.
def delete_entity(url, entityid):
    entities_end_point = "/entities/"
    entities_url = url + entities_end_point

    payload = {}
    headers = {}
    # Lets try to call the Delete: add the identifier to construct the last part of the url
    delete_entity_url = entities_url + entityid
    response = requests.request("DELETE", delete_entity_url, data=payload, headers=headers)

    print("DELETING to "+delete_entity_url)

    if(response.status_code > 299 and response.status_code != 409): #409 is AlreadyExists 
      print("anomaly response of DELETE_ENTITY is "+str(response.status_code))

    return (response.status_code)


# Subscribe to an entity changes given the entity id
def subscribe_to_entity(broker_url, entity_id_to_subscribe, entity_type, nuri):
  subscriptions_end_point = "/subscriptions/"
  subscriptions_url = broker_url + subscriptions_end_point
  subscription_id = entity_id_to_subscribe + ":subscription"

  payload = json.dumps({
    "id":subscription_id,
    "type":"Subscription",
    "entities": [
      { "id": entity_id_to_subscribe,
        "type": entity_type
      }
    ],
    "notification": {
      "endpoint": {
        "uri": nuri,
        "accept": "application/json"
      }
    },
    "@context": [
          "http://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
    ]
  })
  headers = {
    'Content-Type': "application/ld+json",
    'Accept': "application/json"
  }
  post_subscription_url = subscriptions_url
  response = requests.request("POST", post_subscription_url, data=payload, headers=headers)

  print("SUBSCRIBING to "+entity_id_to_subscribe+ " at "+post_subscription_url)

  if(response.status_code > 299 and response.status_code != 409): #409 is AlreadyExists 
    print("anaomaly response of SUBSCRIBE_TO_ENTITY is "+str(response.status_code))
    print("DATA "+payload)
  return (response.status_code)


# Delete an existing subscription
def delete_subscription_to_entity(broker_url, entity_id_to_subscribe, nuri):
  subscriptions_end_point = "/subscriptions/"
  subscriptions_url = broker_url + subscriptions_end_point
  subscription_id = entity_id_to_subscribe + ":subscription"

  payload = {}
  headers = {}
  # Lets try to call the Delete: add the identifier to construct the last part of the url
  delete_subscription_url = subscriptions_url + subscription_id
  response = requests.request("DELETE", delete_subscription_url, data=payload, headers=headers)

  print("DELETING SUBSCRIPTION to "+entity_id_to_subscribe+ " at "+delete_subscription_url)

  if(response.status_code > 299 and response.status_code != 409): #409 is AlreadyExists 
    print("anomaly response of DELETE_SUBSCRIPTION is "+str(response.status_code))

  return (response.status_code)
