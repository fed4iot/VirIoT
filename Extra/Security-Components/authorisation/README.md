# License

Authorization source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# Introduction

This project consists of 3 developments:


1) XACML_PAP_PDP. Offers a web environment to manage subjects, actions and resources and policies (PAP) and an endpoint to verify if a subject can perform an action over a specific resource through the policies (PDP).

2) Py_CapabilityManagerWebService (Capability Manager). Offers an endpoint to obtain the capability token to a specific subject, action and resource.

3) Py_PEP-Proxy. Offers an endpoint to access to the resource.

Each development corresponds with a subfolder.

# Deploying authorization components (docker-compose)

## Configure docker-compose environment variables

Access to the project directory and edit docker-compose to verify environment variables.

### XACML_PAP_PDP

If you don't need blockchain integration you can remove the "environment" section or define `BlockChain_integration=0`.

If you need blockchain integration (`BlockChain_integration=1`), you have two ways to configure the integration:

- Using a configuration file (./PAP/ConfigData/blockchain.conf) : `BlockChain_configuration=0`

- Using the environment variables of docker-compose.yml file : `BlockChain_configuration=1` 				
	
	- BlockChain_protocol=http # Optional: Default value : http
	- BlockChain_domain=testdomain # Required 
	- BlockChain_IP=#<specify Blockchain endpoint IP address> # Required
	- BlockChain_port=8000 # Optional Default value : 8000
	- BlockChain_get_resource=/policy/testdomain # Optional : Default value : /policy/<BlockChain_domain>
 	- BlockChain_post_resource=/policy/register # Optional : Default value : /policy/register
	- BlockChain_update_resource=/policy/update # Optional : Default value : /policy/update

### Capability Manager

You must define the endpoint of IDM-Keyrock

  - keyrock_protocol=https
  - keyrock_host=... #<specify IdM Public IP address>
  - keyrock_port=...
  - keyrock_admin_email=keyrock admin email.
  - keyrock_admin_pass=keyrock admin password.

Params to the blockchain's endpoint.

  - blockchain_usevalidation=Register Capability token identifier within blockchain: Admitted values: "0: No use; 1:Use"
  - blockchain_protocol=BlockChain protocol. Admitted values: "http","https"
  - blockchain_host=Blockchain public IP.
  - blockchain_port=Blockchain port.

and endpoint of PDP where validate if subject, action and resource is allowed 

- PDP_URL=http://...:8080/XACMLServletPDP/ #<specify XACML-PDP Public address (including service)>

### PEP-Proxy 

Params to define PEP-Proxy protocol (optional).

  - pep_protocol: Admitted values: "https","http". Default "https"

You must define the broker you must forwarding the request, once capability token is validated.
        
  - target_protocol=http #Broker protocol. Admitted values: "http","https"
  - target_host=... #Broker host. <specify Broker Public IP address>
  - target_port=8090
  - target_API=Fed4IoTMC

You can decide if considered  blockchain integration or not

  #Validate Capability token using blockchain: Admitted values: "0: No use; 1:Use"
  - blockchain_usevalidation=0

  #BlockChain protocol. Admitted values: "http","https"
  - blockchain_protocol=http 
  #BlockChain host.
  - blockchain_host=... #<specify BlockChain Public IP address>
  - blockchain_port=8000

You must define the endpoint of PEP-Proxy
  - PEP_ENDPOINT=https://...:1040 #<specify PEP-Proxy Public address ex: https://<PEP-IP>:<PEP-PORT>>

Finally you must define Master-Controller endpoint and credentials.

  - fed4iotmc_protocol=http #Fed4IoT Master Controller protocol. Admitted values: "http","https"
  - fed4iotmc_host=... #Fed4IoT Master Controller host.
  - fed4iotmc_port=8090 #Fed4IoT Master Controller Port.
  - fed4iotmc_authz_testpath=/listFlavours # to obtain if it using JWT token has authorisation 
  - fed4iotmc_login_path=/login
  - fed4iotmc_login_userID=... admin user Fed4Iot Master Controller.
  - fed4iotmc_login_password=... admin password Fed4Iot Master Controller.
## Build the proyect images and run:

To build the proyect images and once docker-compose file is reviewed, access to the project directory and run:

```bash  
./build-main.sh
```

When the image was created run it using:

```bash  
docker-compose up -d
```


# Testing XACML_PAP_PDP

## Testing PAP

Access through a web explorer to `http://<XACML-PublicIP>:8080/XACML-WebPAP-2`. You will see the main webpage of the PAP service. Push `Manage Policies` button and once the page is loaded push `Apply` button, no error has ocurrs.

## Testing PDP

- To test PDP is running you can run:

```bash
curl --location --request GET 'http://<XACML-PublicIP>:8080/XACMLServletPDP'
```

you must obtain a response like this (status=200):

```bash
You have to send a POST message with the XACML Request
```

- To test a PDP request (policies) you can run:

```bash
curl --location --request POST 'http://<XACML-PublicIP>:8080/XACMLServletPDP/' \
--header 'Content-Type: text/plain' \
--data-raw '<Request xmlns="urn:oasis:names:tc:xacml:2.0:context:schema:os">
   <Subject SubjectCategory="urn:oasis:names:tc:xacml:1.0:subject-category:access-subject">
       <Attribute AttributeId="urn:oasis:names:tc:xacml:2.0:subject:role" DataType="http://www.w3.org/2001/XMLSchema#string">
           <AttributeValue>Pedro</AttributeValue>
       </Attribute>  
   </Subject>
   
   <Resource>
       <Attribute AttributeId="urn:oasis:names:tc:xacml:1.0:resource:resource-id" DataType="http://www.w3.org/2001/XMLSchema#string">
           <AttributeValue>https://....:1040/ngsi-ld/v1/entities?type=http://www.w3.org/ns/sosa/Sensor;idPattern=urn:ngsi-ld:Sensor:parking.*</AttributeValue>
       </Attribute>
   </Resource> 

   <Action>
       <Attribute AttributeId="urn:oasis:names:tc:xacml:1.0:action:action-id" DataType="http://www.w3.org/2001/XMLSchema#string">
           <AttributeValue>GET</AttributeValue>
       </Attribute>  
   </Action>

   <Environment/>
</Request>'

```

you must obtain a response like this (status=200):

```bash
<Response>
  <Result ResourceID="https://...:1040/ngsi-ld/v1/entities?type=http://www.w3.org/ns/sosa/Sensor;idPattern=urn:ngsi-ld:Sensor:parking.*">
    <Decision>Permit</Decision>
    <Status>
      <StatusCode Value="urn:oasis:names:tc:xacml:1.0:status:ok"/>
    </Status>
  </Result>
</Response>
```

## Testing Capability Manager

- To test Capability Manager is running you can run:

```bash
curl --location --request GET 'https://<CapabilityManager-PublicIP>:3040'
```

you must obtain a response with status=200.


## Testing PEP-Proxy

- To test PEP-Proxy is running you can run:

```bash
curl --location --request GET 'https://<PEP-Proxy-PublicIP>:1040'
```

you must obtain a response with status=200.
