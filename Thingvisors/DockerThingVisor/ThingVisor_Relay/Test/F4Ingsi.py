import requests
import json

# Subscribe to an entity changes given the entity id
def subscribe_to_entity(broker_url, entity_id_to_subscribe, entity_type, nuri):
  
  subscriptions_url = broker_url + "/v2/subscriptions/"

  payload = json.dumps({

    "description": "A Relay TV subscription",

    "subject": {
      "entities": [
        {
          "id": entity_id_to_subscribe,
          "type": entity_type
        }
      ],
      "condition": {
        "attrs": []
      }
    },
    "notification": {
      "http": {
        "url": nuri
      },
      "attrs": []
    }
  })

  headers = {
    'Content-Type': "application/json",
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
def delete_subscription_to_entity(broker_url, subscriptionID, entity_id_to_subscribe):

  payload = {}
  headers = {}
  # Lets try to call the Delete: add the identifier to construct the last part of the url
  delete_subscription_url = broker_url + "/v2/subscriptions/" + subscriptionID
  response = requests.request("DELETE", delete_subscription_url, data=payload, headers=headers)

  print("DELETING SUBSCRIPTION to "+entity_id_to_subscribe+ " at "+delete_subscription_url)

  if(response.status_code > 299 and response.status_code != 409): #409 is AlreadyExists 
    print("anomaly response of DELETE_SUBSCRIPTION is "+str(response.status_code))

  return (response.status_code)
