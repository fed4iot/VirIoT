
# Introduction

This project consists of 3 developments:


1) XACML_PAP. Offers a web environment to manage subjects, actions and resources and policies.

2) XAML_ServletPDP. Offers an endpoint to verify if a subject can perform an action over a specific resource through the policies.

3) XACML_PDP_SunXACML. Contains dependencies needed by XAML_ServletPDP.

Each development corresponds with a subfolder.


# Deploying XACML_PAP_PDP (docker-compose)

## Configure docker-compose environment variables

Access to `XACML_PAP_PDP` directory and edit docker-compose to verify environment variables.

- If you don't need blockchain integration you can remove the "environment" section or define `BlockChain_integration=0`.

- If you need blockchain integration (`BlockChain_integration=1`), you have two ways to configure the integration:

	- Using a configuration file (./PAP/ConfigData/blockchain.conf) : `BlockChain_configuration=0`

	- Using the environment variables of docker-compose.yml file : `BlockChain_configuration=1`. 				
	
		- BlockChain_protocol=http # Optional: Default value : http
        - BlockChain_domain=testdomain # Required 
        - BlockChain_IP=#<specify Blockchain endpoint IP address> # Required
        - BlockChain_port=8000 # Optional Default value : 8000
        - BlockChain_get_resource=/policy/testdomain # Optional : Default value : /policy/<BlockChain_domain>
        - BlockChain_post_resource=/policy/register # Optional : Default value : /policy/register
        - BlockChain_update_resource=/policy/update # Optional : Default value : /policy/update

## Build the proyect image and run

To build the proyect image and once docker-compose file is reviewed, access to `XACML_PAP_PDP` directory and run:

```bash  
./build.sh
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
           <AttributeValue>https://...:1040/ngsi-ld/v1/entities?type=http://www.w3.org/ns/sosa/Sensor;idPattern=urn:ngsi-ld:Sensor:parking.*</AttributeValue>
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
