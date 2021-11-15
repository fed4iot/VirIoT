import requests
import json

# GET all the stored entities of a specific vThing
def get_entities_by_vThing(brokerurl, v_thing_id):
  entities_end_point = '/entities?q=generatedByVThing=="{}"'.format(v_thing_id)
  headers = {
    'Content-Type': "application/ld+json",
    'Accept': "application/json"
  }
  retrieve_all_url = brokerurl + entities_end_point
  response = requests.request("GET", retrieve_all_url, headers=headers)
  return response.json()

# Append (and overwrite existing) attributes of and entity.
# Create the NGSI-LD Entity, if it does not exist
def overwrite_or_append_or_create_entity(url, entity):
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
    print("anomaly response of OVERWRITE_OR_APPEND_OR_CREATE_ENTITY is "+str(response.status_code))
    print("ATTR POSTING to "+change_attributes_url)
    print("DATA "+payload)
  return (response.status_code)

# Batch Upsert. Append (and overwrite existing) attributes of different entities.
# Create any the NGSI-LD Entity, if they do not exist
def batch_entity_upsert(url, entities):
  #print(entities)
  entities_end_point = "/entityOperations/upsert?options=update"
  entities_url = url + entities_end_point

  # setting up the data for the request
  payload = json.dumps(entities)
  headers = {
    'Content-Type': "application/ld+json",
    'Accept': "application/json"
  }
  # Lets try to call the Append Attributes endpoint, with overwrite enabled (default)
  response = requests.request("POST", entities_url, data=payload, headers=headers)

  print("POSTING to ", entities_url)
  print("PAYLOAD: ", response)


  # returning the ids of entities succesfully updated/inserted
  batch_upsert_success = []

  #
  # This following code can't be used until all the NGSI-LD context brokers
  # will follow the specifications about NGSI-LD v.1.3.1
  #
  #if response.status_code == 201 or response.status_code == 204:
  #  batch_upsert_success = [entity['id'] for entity in entities]
  #  print("BATCH_UPSERT_ENTITY OK")
  #elif response.status_code == 207:
  #  batch_upsert_success = response.json()['success']
  #  print("BATCH_UPSERT_ENTITY MULTI-STATUS:",str(response.json()['errors']))
  #elif response.status_code == 400:
  #  batch_upsert_success = []
  #  print("BATCH_UPSERT_ENTITY ERROR:",str(response.text))

    # Instead we have to use the following code

  if response.status_code == 400:    
    batch_upsert_success = []
    print("BATCH_UPSERT_ENTITY ERROR:",str(response.text))
  elif len(response.text) > 0 and 'success' in response.json():
    batch_upsert_success = response.json()['success']
    print("BATCH_UPSERT_ENTITY MULTI-STATUS:",str(response.json()['errors']))
  else:
    batch_upsert_success = [entity['id'] for entity in entities]
    print("BATCH_UPSERT_ENTITY OK")

  return batch_upsert_success

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


# Delete a group of entities.
# It asks for a list of strings (entities' ids)
# Content-Type should be application/ld+json
def batch_entity_delete(url, entities_ids):
  entities_end_point = "/entityOperations/delete/"
  entities_url = url + entities_end_point

  payload = entities_ids
  headers = {
    'Content-Type': "application/ld+json",
    'Accept': "application/json"
  }
  # Lets try to call the Delete: add the identifier to construct the last part of the url
  delete_entity_url = entities_url
  response = requests.request("POST", delete_entity_url, json=payload, headers=headers)

  print("DELETING to "+delete_entity_url)

  # returning the ids of entities succesfully deleted
  batch_delete_success = []

  #
  # This following code can't be used until all the NGSI-LD context brokers
  # will follow the specifications about NGSI-LD v.1.3.1
  #
  #if response.status_code == 201 or response.status_code == 204:
  #  batch_delete_success = entities_ids
  #  print("BATCH_DELETE_ENTITY OK")
  #elif response.status_code == 207:
  #  batch_delete_success = response.json()['success']
  #  print("BATCH_DELETE_ENTITY MULTI-STATUS:",str(response.json()['errors']))
  #elif response.status_code == 400:
  #  batch_delete_success = []
  #  print("BATCH_DELETE_ENTITY ERROR:",str(response.text))

  # Instead we have to use the following code

  print("RESPONSE BATCH_DELETE: ", response)

  if response.status_code == 400:    
    batch_delete_success = []
    print("BATCH_DELETE_ENTITY ERROR:",str(response.text))
  elif len(response.text) > 0 and 'success' in response.json():
    batch_delete_success = response.json()['success']
    print("BATCH_DELETE_ENTITY MULTI-STATUS:",str(response.json()['errors']))
  else:
    batch_delete_success = entities_ids
    print("BATCH_DELETE_ENTITY OK")

  return batch_delete_success

# Subscribe to an entity changes given the entity id
def subscribe_to_entity(broker_url, entity_id_to_subscribe, entity_type, entity_context, nuri, watchedAttributes=None):
  # When a parameter has a list or a dict, it is treated as a static list/dict.
  # We don't want that.
  if watchedAttributes is None:
    watchedAttributes = []

  subscriptions_end_point = "/subscriptions/"
  subscriptions_url = broker_url + subscriptions_end_point
  subscription_id = entity_id_to_subscribe + ":subscription"

  if len(watchedAttributes)>0:
    for attr in watchedAttributes:
      subscription_id+="_"+attr

  dic={
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
        "accept": "application/ld+json"
      }
    },
    "@context": entity_context
  }

  # if we have attributes to watch, then define them into the subscription (watchedAttributes field)
  # and also inform the broker that we want all other (non-watched) attributes
  # be not present in the notification we will receive, except the generatedByVThing,
  # by setting "attributes" to just the watched ones, plus generatedByVThing
  if len(watchedAttributes)>0:
    dic['watchedAttributes']=watchedAttributes.copy()
    dic['notification']['attributes']=watchedAttributes.copy()
    dic['notification']['attributes'].append("generatedByVThing")
  payload = json.dumps(dic)

  headers = {
    'Content-Type': "application/ld+json",
    'Accept': "application/json"
  }
  post_subscription_url = subscriptions_url
  response = requests.request("POST", post_subscription_url, data=payload, headers=headers)

  print("SUBSCRIBING to "+entity_id_to_subscribe+ " at "+post_subscription_url)
  print("PAYLOAD: "+payload)

  if(response.status_code > 299 and response.status_code != 409): #409 is AlreadyExists 
    print("anomaly response of SUBSCRIBE_TO_ENTITY is "+str(response.status_code))
    print("RESPONSE TEXT: ", response.text)
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
