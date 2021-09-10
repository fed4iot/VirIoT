# License

PEP-Proxy Project source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# Introduction

This project is a PEP-Proxy which is designed to supports different APIs. When PEP-Proxy receives a request, this component validates and handles the request before send it to the corresponding target (as to a Context Broker API).

This project contains:

- PEP-Proxy source files & folders.

    - PEP-Proxy.py: Run PEP-Proxy component.
    - config.cfg file: Contain the configuration of PEP-Proxy component.
    - UtilsPEP.py: Handle several requests receives by PEP-Proxy sending it to the corresponding API functionality.
    - API folder: Contain one file per specific API. Each one has the functionality to validate and cypher the request body.

- PEP-Proxy folder to ssl.

    - certs folder: Contains the certificates needed to ssl.

- PEP-Proxy files & folder to cypher.
    - conf_files folder: Contain key files.
    - cpabe_cipher.jar file: It is a Java application to cypher text with cp-abe.
    - cpabe_decipher.jar file: It is a Java application to decipher text with cp-abe.

- PEP-Proxy files & folder to validate Capability Token.
    - CapabilityEvaluator.jar: Java aplication (validate Capability Token process). 
    - config folder: Contain the certificate paths.
    - local_dependencies folder: To allow run the java process (CapabilityEvaluator.jar).

- PEP-Proxy files to deploy.

    - Dockerfile file: Contain the actions and commands to create the Docker image needed to run the PEP-Proxy component.
    - requirements.txt: Contain the auxiliar python modules needed by the application. Dockerfile uses it.
    - build.sh file: To create the PEP-Proxy Docker image using Dockerfile.
    - docker-compose.yml file: To deploy PEP-Proxy container.

- PEP-Proxy files to test.

    - test folder: Contain a forder with python client examples to NGSILD. 

# Configuration config.cfg file

Before launching the PEP-Proxy, it's necessary to review the config.cfg file:

```sh
cd projectPath / PEP-Proxy
vi config.cfg
```

- Params to PEP-Proxy's endpoint.

    - pep_host: No change admittable (always 0.0.0.0)
    - pep_port: If change this param, it's necessary to review Dockerfile and docker-compose.yml files. By default 1027.

- Params to the target's endpoint.

    - allApiHeaders: Define the admitted headers to send to target API. If a header of the request receives by PEP-Proxy is not included in this param, the final API request will not consider it. This param store all the headers of each API supported by PEP-Proxy. It's necessary to define an element for each API supported. **IMPORTANT:** It's necessary to use lower case.
    - chunk_size: To read the response received after the API request. Default 1024

- Params to cipher attributes.

    - allSeparatorPathAttributeEncriptation: Specify the separator used by relativePathAttributeEncriptation param to build a relative path into the attributes. This relative path is necessary to determine if an attribute requires cypher or no. Use a pattern never used by attributes or keywords. This param store a separator of each API supported by PEP-Proxy. It's necessary to define an element for each API supported.
    - relativePathAttributeEncriptation: This parameter is a tridimensional array. To understand it, we are going to use the next examples:

        **ONLY ONE CONDITION**. In this case, the system searches into each the attribute first a key named "metadata", and after, into it, a key named "cpabe-policy". If it is successful, the attribute will cypher.

        - Example (NGSIv2).

            ```sh
            relativePathAttributeEncriptation=[[["metadata/cpabe-policy",""]]]
            ```

        **NOTE:** If the second element of the array is defined, the system also will verify if the value is the same as the relative path value. If it is also successful, the attribute will cypher.

        - Example (NGSIv1), the analog of previous NGSIv2 example:

            ```sh
            relativePathAttributeEncriptation=[[["metadatas/name","cpabe-policy"]]]
            ```
            
        **TWO CONDITIONS AND MORE (AND)**. In this case, the second condition must also be satisfied. It is an "and" condition. If both conditions are successful, the attribute will cypher.

        - Example (NGSIv1).

            ```sh
            relativePathAttributeEncriptation=[[["metadatas/name","cpabe-policy"],["metadatas/type","policy"]]]
            ```

        **TWO CONDITIONS AND MORE (OR).**
        In this case, if one of the conditions is successful, the attribute will cypher. It is an "or" condition.

        - Example (NGSIv1):

            ```sh
            relativePathAttributeEncriptation=[[["metadatas/name","cpabe-policy"]],["metadatas/name","other-policy"]]]
            ```     

        **NOTE:** Mixed cases are supported.

        **IMPORTANT:** This param is case sensitive.

        **IMPORTANT:** Before update this param see "Proxy PEP - updating relativePathAttributeEncriptation param" section.

    - noEncryptedKeys: It is a list of first-level attribute keys that never will be cyphered. **IMPORTANT:** It's necessary to use lower case. Default ["id","type","@context"].

- Params to log KPIs info

    - logginKPI=Admitted values: "Y","N"

# Configuration docker-compose.yml file

Before launching the PEP-Proxy, it's necessary to review the docker-compose.yml file:

```sh
cd projectPath / PEP-Proxy
vi docker-compose.yml
```
- Params to define PEP-Proxy protocol (optional).

    - pep_protocol: Admitted values: "https","http". Default "https"

- Params to the target's endpoint.

    - target_protocol: Broker protocol. Admitted values: "http","https"
    - target_host: Broker public IP.
    - target_port: Broker port.
    - target_API: Broker API type. Admitted values: "NGSIv1","NGSIv2","NGSILDv1","GenericAPI","Fed4IoTMC"

- Params to the blockchain's endpoint.

    - blockchain_usevalidation=Validate Capability token using blockchain: Admitted values: "0: No use; 1:Use"
    - blockchain_protocol=BlockChain protocol. Admitted values: "http","https"
    - blockchain_host=Blockchain public IP.
    - blockchain_port=Blockchain port.

- Params to the PEP's endpoint in PDP component.

    - PEP_ENDPOINT=PEP-Proxy Public address ex: https://<PEP-IP>:<PEP-PORT>>. HOST NO admitted: 0.0.0.0, localhost, 127.0.0.1

- Params to define Master-Controller endpoint and credentials.

  - fed4iotmc_protocol=http #Fed4IoT Master Controller protocol. Admitted values: "http","https"
  - fed4iotmc_host=... #Fed4IoT Master Controller host.
  - fed4iotmc_port=8090 #Fed4IoT Master Controller Port.
  - fed4iotmc_authz_testpath=/listFlavours # to obtain if it using JWT token has authorisation 
  - fed4iotmc_login_path=/login
  - fed4iotmc_login_userID=... admin user Fed4Iot Master Controller.
  - fed4iotmc_login_password=... admin password Fed4Iot Master Controller.

# Prerequisites

To run this project is neccessary to install the docker-compose tool.

https://docs.docker.com/compose/install/

Launch then next components:

- Capability manager web service running. 

```sh
git clone http://odinslab.duckdns.org/security_components/Py_CapabilityManagerWebService.git
```

- Broker target to access.

- Certificated files must be generated. Copy generated certificates files (fullchain.pem and privkey.pem) to pepproxy certs folder (`./PEP-PROXY/certs/`). You have to respect these file names or update volumes section of pepproxy service in docker-compose file.

# Installation / Execution.

After the review of config.cfg file, we are going to obtain then PEP-Proxy Docker image. To do this, you have to build a local one, thus:

```sh
cd projectPath / PEP-Proxy
./build.sh
```

The build.sh file contains docker build -t fed4iot/pep-proxy ./ command.

Finally, AFTER REVIEW docker-compose.yml file and especially its environment variables, to launch the connector image we use the next command:

```sh
cd projectPath / PEP-Proxy
docker-compose up -d
```

### Troubleshooting

If the certificates were renovated, you need to include them in pepproxy service image. Once certificate files are ubicated at the corresponding folder following prerequisites indications, access to the project directory and run:

```bash  
docker-compose build pepproxy
```
After you can run as you can see below.

# Monitoring.

- To test if the PEP-Proxy container is running:

```sh
docker ps -as
```

The system must return that the status of the PEP-Proxy container is up.

- To show the PEP-Proxy container logs.

```sh
docker-compose logs pepproxy
```

# PEP-Proxy functionality.

When PEP-Proxy receives a request, PEP-Proxy first obtain its action or method to process it with the corresponding functionality. At the moment the actions/methods are supported by PEP-Proxy art.
* GET.
* POST.
* PATCH.
* DELETE.

After, PEP-Proxy recovers the request body, if it exists, and finally cypher it if it is necessary.

PEP-Proxy supports the NGSIv1, NGSIv2 and NGSILD APIs. If it may be necessary to support new APIs, see the "Proxy PEP - supporting new API" section.

PEP-Proxy supports cp-abe cipher method. If it may be necessary to support new cipher methods, see the "Proxy PEP - supporting new cypher" section.

Only NGSIv2 and NGSILD APIs support cp-abe cipher method. 

To increase supported API actions/methods or paths you must review PEP-Proxy files. It's not be a problem if you don't need use cipher methods. If it may be necessary to support new actions/methods or paths that use cipher, see the "Proxy PEP - supporting new actions/path with cypher" section.

# Proxy PEP - supporting new API.

To support new APIs, follow the next steps:

1. Add API to config.cfg file.
    - APIVersion: Define a value to the new API and include it also into the param comments.
    - allApiHeaders: Define a new element for the API with the possible headers.
    - allSeparatorPathAttributeEncriptation: Define a new element for the API with the value.
    - relativePathAttributeEncriptation: TODO
    - noEncryptedKeys: TODO

2. Add a new file into API folder named "Utils{APIVersion}.py" using for it another existing file (copy).

3. Update UtilsPEP.py to import the new file and add a new case in each if statement.

4. Update API/"Utils{APIVersion}.py" file to add the corresponding functionality for the API.

5. Review/update al coments included in previous 4 points and update the README.md file


# Proxy PEP - supporting new cypher.

To support new cypher, follow the next steps:

1. Add attribute cypher condition to relativePathAttributeEncriptation param (config.cfg file).

2. Update all files of API folder to support the cypher. Exactly you need to review the "cipherBodyAttributes" function and add a new else: if(condition): statement into the for. The condition must validate the corresponding condition established in relativePathAttributeEncriptation param. Finally, include into the if block the code to cypher.


# Proxy PEP - updating relativePathAttributeEncriptation param (config.cfg).

The conditions established in this param determinate if an attribute must be cyphered. The cypher process validates the same conditions before to cypher the attribute. For this reason, if we update relativePathAttributeEncriptation param we must update the code, exactly, the "cipherBodyAttributes" functions into the API folder files.


# Proxy PEP - supporting new actions/path with cypher.

To support it you must review:

1. Edit UtilsPEP.py file and update the encryptProcess function.

2. Edit the file into API folder corresponding with the API and update/review processBody function.

**IMPORTANT:** If request body hasn't the same format as (processCypher example comments), you need build new functions because you can't use processCypher functionality.


# PEP-Proxy and CP-ABE cipher method:

At the moment, NGSIv2 and NGSILD APIs support cp-abe cipher method. 

Example CPABE cipher:

```sh
java -jar cpabe_cipher.jar "att1 att2 2of2" "hello"
```

We are going to see and example of each supported API to explain this:

* NGSIv2.

    - Default config.cfg configuration.
        
        ```sh
        ...
        APIVersion=NGSIv2
        ...
        relativePathAttributeEncriptation=[[["metadata/encrypt_cpabe/type","policy"]]]
        noEncryptedKeys=["id","type","@context"]
        ```


    - Format to detect an attribute must be cyphered.
        ```sh
        "attrName": {
            "value": attrValue,
            "type": attrType,
            "metadata": {
            "encrypt_cpabe":{
                "type":"policy",
                "value":"policyValue"
            }
            }
        }
        ```

    - How cypher an attribute with an example. 
        - Before cypher process.

            ```sh
            "temperature": {
                "type": "Float",
                "value": 23,
                "metadata": {
                "encrypt_cpabe":{
                    "type":"policy",
                    "value":"att1 att2 2of2"
                }
                }
            }
            ```

        - Cypher operations. 

            ```sh
            temperature["type"]: "cyphertext"

            temperature["value"]: java -jar cpabe_cipher.jar "att1 att2 2of2" "23"

            temperature["metadata"]["encrypt_cpabe"]["value"]: java -jar cpabe_cipher.jar "att1 att2 2of2" "Float"
            ```

        - After cypher process. 
        
            ```sh
            "temperature": {
                "type": "cyphertext",
                "value": "eyJ2YTAvZ3NWMHV2SktLUi9UeFk4Mk13PT0iOiJBQUFBZ0NxK2MycjhMUjMzM1d4SEZwdWVlWGQ5dDdURUdZUXJLUVJuWUFvR2dDQ2NyU09oeXlDdzN0M2kydXo1QlhFcmFWK0Q2T3V0NHFqVVdRcnhabC9pRy94U1VjMldQN3lCSm0weHdPNzk4Y3VjTkJhUGZxeWd1bXlreFJRN254ZWRpaGxPUGphTE85cXZKVzJRRGhYMTdXVXZqT2IxZ0VRRjJ3WGNNMDdlZnhBY0FBQUFnSW80b3hhNEs1WVdGOVk4emQ5Wkg1ZmVUY25JR1l0QmphKysvUnZZVG96ZmFSVHFlQlBMbDdvZVlneGJtd3VpWjVabEZ6WXlkWEdkWkRtb0xjdDIvT1NkSFhiK0hoZzVJMW1pc1Z5UkdaRVlIc3FtcXhLVVlBVmg3aUlvS3lhcXBKYVB3MVR4QWdXMkYwdHBxbWYwSEx5L0dzU3hrU1VuQWFvVmhzRUY2ckRHQUFBQUFnQUFBQUlBQUFBQkFBQUFBQUFBQUFSaGRIUXhBQUFBZ0tZc280aHkxcDhsRlArNGNXUEVrTFRRUERVblhHZVR4OTB5VkhtSmZtQTRoWlJaWlJwZXIzNzYyOUU4Zy8zVkFLZTI3TmxkOTAzdGIyOGp3cXg5SCtDaDJibmNEQTh2T3JEYnlzaEJVcEVJVHZvZGIxa1pFSjdJOE5rUWxUZ1c3c1BIRjhPVTUvVjVyTDRrMXdVQSttSVhHbXhQUFpQQW5KMnVDckpXSFB0eEFBQUFnRGhRVGQ4ZlA0SnJCdldvS1dBc1BXUWZsUVNPZlNYQmZWS2RrR1dNeVlONkFnby9BK1VPT1dIb29lSnFuZDVtMC94bDNGYTdtSGVqWEw1SnlRM0hXbWxzQVV4dlZyczBrT1ZwR2NDSGd3WGF4ODNVOU9qaVFjdTVoamJmVjRGak84Yy9nWlV4U0xKNTBOUzF1U2dzeFZFaXhTcFYxWkRhZkNNZXBwY3lWelVGQUFBQUFRQUFBQUFBQUFBRVlYUjBNZ0FBQUlCOTlJQ1Z5eWFrSldTaW9TN0VHMHpNUTZ0QzlUYll1c0FjMlIxT0VGQktyeUtHZWNicUNyRnRUKzhENXpEeE0zV3dYMlV2TE5qOTB5Zk9qZzFGakljRE1yUlllcU4xS2pQU3RBZEhpeFFHMEdNaEcyYVZwbjgvYzJpUUhqS1JuR0h4ZXFTaCtKUjZSOGVmWXhaOHhNay8rMDdpSDhRVWdkbnRwalNGTE13TURBQUFBSUFCVHUyU1NGLzI2VWxuSzRnbGE3SEZwdUFkQ0UzS0VQSmtBRCs0SjQwbWlXK2hCT2xGazdUQ2pnSDhGVHY3Vkl2WHlNMFgvRE9pc3J5cVN2UFhXZ3hGRHVNZTVVaWdCN29xQkdtcG9pdFlQZmhLQkRyeWN1SGVwYm4xZXhaRjlnb2M3cTQ2REdtOUVHUlIzcWZSYmFKcGlLK2ZEazNUekRsUEFXK21FOWpGZnc9PSJ9",
                "metadata": {
                    "encrypt_cpabe": {
                        "type": "policy",
                        "value": "eyJPWjNBWC9HRU8yTGtZZ0NBU0EvM3lRPT0iOiJBQUFBZ0lVbTRLRlpDakNZSWpmL2kySVpDdUx2WENkdkhxcG1lNGpPeHQwRFlmSnB0cGl4SWRaTGJ5Q2ozQzdtZjl0Z2FERm92TnJmcmFYSzhOeThDWUVCbzh0NHBXT3R6N0R4ZUZkd2RpSkVkTGdOdkxEbzhKMDhRZ3JMM1lxSEcySUJuQjhDNU11eDdiZzEwTkhJU3R6WCtIaHFGV0dNb25xVHpZTThnakU5R3R3ZEFBQUFnSVk0NGo3ZHZaNkFOSWhJTGdMelZ2bE5iQ3FSbk9PVlJhR2tVdmlEVlA0cVNDeWE5V1ZBbEhsbm1XSmgwbm5hUndUODFvQndiRUR1SkNpbko4NDBnajJDQm5vSktwK3U2NjF4MjVEL0c3TzNPN0Q3UkRTS1FmTjRhTWVOOWc3a1k0NmFCY3pNd29kZnY2b2FmOS9SOXkrWjZSa3IzNzFVK2dhSUFSMVFaUVBTQUFBQUFnQUFBQUlBQUFBQkFBQUFBQUFBQUFSaGRIUXhBQUFBZ0J4QjFjWktWSURzRFZqOExmRnEwazNMcXVXcS9IV1daWFBDK1d3UE04cjRGemtMNVNNVWhFTWROZ1AwQm5FTnhCcllvbHlBMnVmWG9EbGJHK3RxL0J3Q05lNUpSWkQybTVGaDd6aFhONTNrT3pyUXpLaERTR1BNZXp3bDhNZENOcmtyU1FxUmxkdFJlVkFpNXVoN0tMK3VkTUxaUmJEeHQzUjFTNmQrRnRaNkFBQUFnQjU2YXRQclU3SjV6WVJoNUYvVWNPSkg4TDJUcExndnhCa1IxTmlhVUo4ajBjVTBGQ09EaVEvYlo4VzFMbldKck5TMEFPL3pHN0c1RjlJM1c2YktQYWhRYWRwbGFyTkcxZmgzMTVmeDRlZTZaRitxUTBQd0l2cUM5K2VrQTRPN3JNR2Fyb2NHaHQxNXdEUUI4QmkzSHRXZ2k2SERhd2NLUmhQQ004S1dZeW16QUFBQUFRQUFBQUFBQUFBRVlYUjBNZ0FBQUlBL05kOXgwQVNCbXBOTk8yaFZITkdrV3hLWU9YN2dkT3l6T0xNY1lBRXUweUZFTUgrbldqSTVFQWZQT0F1bjNLWDhOVERQMG9ua2tuYytGakFudHRraUkrYXlkUURncWRkMFR0TnFyV29MNjlSVEhLV3kya0RTR1JvajJmVmIxcDYrcUVaYzliWXRsVGdaaXY2eVpaZXJhTGxVNURtNlN1YzVaczZkR0dzNnJnQUFBSUJiR2Zrc1ZyTE0vZHBzWkJIZXJ3VFhZd1RwdG1FdE16bzIzZ2tGYXcrczNoejJiN2E1TGg5UWlMaGpLSDVOUUY4ZWZVdTdMbDJBdmdNOGd2YmhWWmluWDRYdlVrbk5LSXpnbFdpZ2lKZEJVUWp0NjJ3Z3poVDluOVlXcnhGd0tydHRvUXJCakZvQXNhZlMwV2dDZzJrYTltc0psbVlXNW9HRU9DV1ZHb09POUE9PSJ9"
                    }
                }
            }
            ```

* NGSILD.

    - Default config.cfg configuration.
        
        ```sh
        ...
        APIVersion=NGSILDv1
        ...
        relativePathAttributeEncriptation=[[["encrypt_cpabe/type","Property"]]]
        noEncryptedKeys=["id","type","@context"]
        ```

    - Format to detect an attribute must be cyphered.

        ```sh
        "attrName":{
            "type":"Property",
            "value":"attrValue",
            "encrypt_cpabe":{
                "type":"Property",
                "value":"policyValue"
            }
        }
        ```

    - How cypher an attribute with an example. 
        - Before cypher process.

            ```sh
            "brandName":{
                "type":"Property",
                "value":"Mercedes",
                "encrypt_cpabe":{
                    "type":"Property",
                    "value":"att1 att2 2of2"
                }
            }
            ```
        - Cypher operations.         

            ```sh
            brandName["value"]: java -jar cpabe_cipher.jar "att1 att2 2of2" "Mercedes"
            2. brandName["encrypt_cpabe"]["value"]: "encrypt_cpabe"
            ```

        - After cypher process. 
            
            ```sh
            "brandName":{
                "type":"Property",
                "value":                  "eyJTd3FRZVFnYmN1SUhjMmlwWW5ud3BBPT0iOiJBQUFBZ0tScCtFREZSdi9HeStKaE1KU0JaeldJc3BNNDdXRnl6OEFYdjdGQWdIVmdLdXNlbW9qSExJVWx6ZFpDQXVtTktrV2QxMlhYWW93Mk1PeEtNeEZLemQxcG54ZFR1QStMSzkvdS8yUGNrdG1vOFkvOUZZcSsyMUx2S3hidEo3R2ZHVkpXbE9KL2FMeWhEZmpjYWNvTG9yMHF0MU9pNjBEeWFYYWtKeWcwb3JQM0FBQUFnSjBtKzNuWVVIenhVRE1kcndYSWIwZUdrR0tyeTFOYjh1cmVBc2ZyUnY3ODFoQ0dET3B1WHpUdUdWMGNXcHhoL3o2YWIwQXBTTFNyWS9jb2U1bWdKWjRsUGljKzlNa1Fwc0VYYW1FMnk0VkZCZ1BWOFE2eXJ6QUhlR1RnSXpWSWppb0FhcGxlS3k2WTNLNG94NGtLbm5UUkRFYlVGaVhhSjI4b21MaEJqbmVTQUFBQUFnQUFBQUlBQUFBQkFBQUFBQUFBQUFSaGRIUXhBQUFBZ0lBUHY1N0tNMXhGeXB0S2VUZFM0Y1BNTlg3Nk9saEVJVjFwOVZSUk5VemhYNXhUVVRGTkpEOUFlM3FHYVNQZDA3UzAybjh2bEhKdXM3Q0Yxcm50eU9BWCsrdUU3Z3NuNk5rbm0rM3BiQVZrd01GQlVoRmVwbVBxMGJZZm9XRHkycDlGM2dzUGx2eTFWaVZ0VXM0N0FJVjg1YXNrMXRCOUpnS2hVYVhLekJON0FBQUFnR2hUd1NJVFBNV1ZHMFFXbVpGNysrdHVnNXlBZkNlaExSSFhiTzk0QzRkU0RkTS82T2lCL09IRmFqVnVQd3NoUDQ4ckdYMzNLRVhySXdDeGl3aHYrWTQzWXhadFRMZ2dBK3ZiQS9xa3RnMThpVjl2NFhWR0JKZEVlbHpLRG5yYzNKdjVhSTRZVFE5UnZ3L1p0aFZ1ekkzcnE0Vnl2VGhGbXRrbVFsUnN1VFdpQUFBQUFRQUFBQUFBQUFBRVlYUjBNZ0FBQUlCeFUrVHIwT0J0QXBUelJvYzExWlZ4eGFmNVBFRzlTN09kSmNETDlMb0REUWdtTmRyOU02MFZyTUVJeWZ4RXhLR2RsbEJDc2ROZ0Z0RUQrL283SjFIR25KNk8yQjdVMTcrcmxoZTg2bDFGMGtxem5aTEY4eGw0RGdmYUxoR0RtdmJNdmVNTnlGRUtTK0gvcEdpUWZFMzBaNlJab0xvdnBXTnBoOWUyUk9FVVBRQUFBSUNmamRmNzFmV3E1MzVtZEIwOG9wNmlNeTArWnA1YVUvWGIwRnMyanFKYUZkZFpiV3R4WHpycHlDb1U4RmxpaGxhTVFzRWJJdUt0WWlQQVUzcnNrSjBsaElzSlN3L05UODhUOERSNmhZZ3B5c21DcUFiSWhmWDZubGRPdjN5RldJTmdsL0NscVVUMGxBUzB6bVoweHZMYnhpUG9GNFF0M2laYXVabzR1dDJ2elE9PSJ9",
                "encrypt_cpabe":{
                    "type":"Property",
                    "value":"encrypt_cpabe"
                }
            }
            ```



# PEP-Proxy and CP-ABE decipher method:

Example CPABE decipher:

```sh
java -jar cpabe_decipher.jar "eyJ4azZSeUVIazVMZG4yL2E1ZnA0SGt3PT0iOiJBQUFBZ0gwMXR5dXpMYVZmNGJKV0llQlNpNDlTUnhsMjVOU3RtSGpEUVVxQThJdzVhSm9remxVdk5Rc080dVRZMnd0NkpRZVdiVFhLY3lTREZzU245MXV6NTZSNk9ncWF2eDNYQ0NnazRkRVNOTlhOaFJsWjFpVWJuVWRyaGQvZURHNTJ3WXhVdVBDc1hCZStvM2dGVXpKL2ZmbVY0TXVUTk5vNmNMNHF4MTBvOC91TkFBQUFnR05YV3ljanAwMktscmh4eUZ4TTRxaGs5UFJjRkppVHI1RU4yQjEreDN2TGhwTnhKZGwxWFJlbHYzcldtTTVYTXdnOUh1ZGRBWmR2RTRVWVh4T3dLS0FySzFSVzZJWndTeGc0THN3dmI5UllrZ25wUWNsWFg1UjRQRDEzZXFOblZOVHBwYjFXZ0hkNk9rcG9EMGNRL2xQajYzYTdwekF5a05lYU5FZEUyeHRhQUFBQUFnQUFBQUlBQUFBQkFBQUFBQUFBQUFSaGRIUXhBQUFBZ0JqZndsRzhMMGMvb1pXNVJJaDhVUk54TWFNNE1wMGZkc2hET3lxaGZTWjVaM1NjWTdFekdqNm9NZFFNQkdPb0hWSm1tcVRTcDNicExGM0VEK3pOa2N1WFpJSElSS2d3WGRpbElDNDVoSjNFNmE2Q3Q5SWlzV2ZRSHVhMFREVlFSYlN1ODlZSnQ5T3IybXQ0L3NmcUJjeUdLZ0dLNzVUNnJQcWpBNEpHcnBjNUFBQUFnQW5lbVVRQXJzam5lM293RjJvZE4wb1dTdW1HeFlaemVmSWtIMTRoKy9XalkybFptWVMycmhlRmhmNktORmxmTEpYMUdrTTJWS05QNElrMVlTNEZsbHRiaDgrQmhoa2MwN05qYSsxU0U1Q3VZUFQvMVRZYlp4SWc0ZmM3Q0xiY1pnYUtuQk5ZYVhHd09nY1FSZU1nclpFVnpGZkdvckdhK1MwdVYwY3hGNUZiQUFBQUFRQUFBQUFBQUFBRVlYUjBNZ0FBQUlCNUhybnJTcmRlNWlNTXhVUk55a3VsWXFBbTBVSit6eFJ2LzhYazNOSU96d2ptdHlLaElzdjlDZTJicnZYdnNBenpzbHdURHZYbitKZEJEdFdMSXpuT1NGa2ZKQ1I1WjRxZWI0UW9DQVBBdEpObEYyYy9NRk1BbDhmY0tlaTZ0Z29Fb1UzSnF4T1lkWkp0VllEMVF2UUxObW1xM1kxS1dZQkp2MVp6N1I3R3BRQUFBSUJDbVBONXl0QXZZN2t1NE5UUzVVaXJVWi9HeE5tSGVFLzNMbnpqYkRYTDhoKythN0pwYmNEZTRyM1U2dGZSZ2JNOWdIWVpKZ3htQXE4eFdpOXhlSTdtVGZROUozMW90d1dnaE1nZzFBbngySWxvVG9pcHhRWkoxVlVrbXQxOUhWek1qOUtNbG1iaDV6U0ErVGFwdmd6bWUvVjZBdEdhbFZWVERMeWVUTHJ0Q2c9PSJ9"
```

If we decipher the previous example, only the policy value can't recovered from the original body.

# Resume and other considerations and limitations in PEP-Proxy.

- Supported APIs: NGSIv1, NGSIv2, NGSILD

- Cipher:
    - Supported cipher method: cp-abe
    - Supported APIs uses cipher method (cp-abe): NGSIv2, NGSILDv1
    - No supported cipher for "id", "type" or "@context" first-level keys.

- If update relativePathAttributeEncriptation param, PEP-Proxy code must be update, see "Proxy PEP - updating relativePathAttributeEncriptation param" section

- To cypher all entity attributes we can do it if defining one condition that all attributes satisfy, for example, all attributes include a key named "type" or "value", before do it see also "Proxy PEP - updating relativePathAttributeEncriptation param" section: 

    ```sh
    relativePathAttributeEncriptation=[[["type",""]]]
    ```

- No supported:
    - POST /v2/op/update doesn't support cyphered.
    - PUT methods doesn't support cyphered.

- PEP-Proxy errors or validations return a simulated fixed response from API. At the moment some headers are missed comparing with the original API response (Connection, Content-Length), because they create errors.


# PEP-Proxy examples request.

Once we obtain the capability token from Capability manager web service, we can send NGSI request adding the "x-auth-token" header to it.

* NGSIv2 example.

    ```sh
    curl -X POST \
    https://<pep_host>:<pep_port>/v2/entities \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -H 'Fiware-Service: room' \
    -H 'Fiware-ServicePath: /pruebaroom' \
    -H 'x-auth-token: {   "del": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvGZqLGhCbTcdBFlTAMZiAvbshtG4DZMC5A0DJ3SNjulniMXBWQMAJm/J3P98T2nE+k/m7n6aJJSdLO+hq1/EICB+kCRDxRbxRhvMh4g+/C2hKiDiDvXNUJTfie4otEbWJYIEW0C1gqxhnw16y63zhh+gJ7WGxQLuSRBmZBA8tmRqQH2L7tZPYZ2CzTqJsE9PZyXTPJVye8LglGOM71/BLvz6Vdjcmu9efPnCm9yXksba7zfSASnCDQf4uBYnC2KXb/LYZedGMcWw0BdEK84Ep8d1rccvzQ7nfxGviYG6M0r/cKLHb58kSxVhwpTNoPg3LCo/2fp0fFb5xvY3n7bR5wIDAQAB",   "id": "knf3jrn1bi6ftt8pf0676ehm4a",   "ii": 1568197484,   "is": "capabilitymanager@um.es",   "su": "joseluis",   "de": "*",   "si": "HdncBHHoNQszE/qK4FzO6+D3s+9KbAnqWUO3xjRzgdRhm9IhcxAfi+6hlx/qZWfufqjKf66KwWV/et5QUe3wWM9kkwk0Nfb1fdG2kyoYM3YHHQZ8k3xeEwoWsR7+MfLtns3BWncHAxtiNSzSupDdpxzijsHBPDx0XUEd+TCpa3KR17WBHSfVHwc1jYPllvcSZfwSlZXbTFmYbpR+P4CNTnfwNr9rnnIB2msK3m7QQQBq5RkutTkeLkP7f8YERyax4n1JFDrQQ9ytMcp/+nZjjrkfOOhZPA1aYkf7f88+qZiKCSNhisxS32NzVuzWtQFhaciYwo1K6R+a9fZyJpeoOQ==",   "ar": [     {       "ac": "*",       "re": "*"     }   ],   "nb": 1568197484,   "na": 1568201084 }' \
    -d '{
        "id": "Room2",
        "type": "Room",
        "temperature": {
            "value": 23,
            "type": "Float",
            "metadata": {
                "encrypt_cpabe":{
                    "type":"policy",
                    "value":"att1 att2 2of2"
                }
            }
        },
        "pressure": {
            "value": 720,
            "type": "Integer",
            "metadata": {
                "encrypt_cpabe2":{
                    "type":"Text",
                    "value":"admin"
                }
            }
        },
        "color": {
            "value": "Red",
            "type": "Text",
            "metadata": {
                "encrypt_cpabe":{
                    "type":"Text",
                    "value":"att4 att5 2of2"
                }
            }
        }
    }
    '
    ```
    
* NGSILDv1 example.    

    ```sh
    curl -X POST \
        https://<pep_host>:<pep_port>/ngsi-ld/v1/entities \
        -H 'Accept: application/ld+json' \
        -H 'Content-Type: application/ld+json' \
        -H 'x-auth-token: {   "del": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvGZqLGhCbTcdBFlTAMZiAvbshtG4DZMC5A0DJ3SNjulniMXBWQMAJm/J3P98T2nE+k/m7n6aJJSdLO+hq1/EICB+kCRDxRbxRhvMh4g+/C2hKiDiDvXNUJTfie4otEbWJYIEW0C1gqxhnw16y63zhh+gJ7WGxQLuSRBmZBA8tmRqQH2L7tZPYZ2CzTqJsE9PZyXTPJVye8LglGOM71/BLvz6Vdjcmu9efPnCm9yXksba7zfSASnCDQf4uBYnC2KXb/LYZedGMcWw0BdEK84Ep8d1rccvzQ7nfxGviYG6M0r/cKLHb58kSxVhwpTNoPg3LCo/2fp0fFb5xvY3n7bR5wIDAQAB",   "id": "knf3jrn1bi6ftt8pf0676ehm4a",   "ii": 1568197484,   "is": "capabilitymanager@um.es",   "su": "joseluis",   "de": "*",   "si": "HdncBHHoNQszE/qK4FzO6+D3s+9KbAnqWUO3xjRzgdRhm9IhcxAfi+6hlx/qZWfufqjKf66KwWV/et5QUe3wWM9kkwk0Nfb1fdG2kyoYM3YHHQZ8k3xeEwoWsR7+MfLtns3BWncHAxtiNSzSupDdpxzijsHBPDx0XUEd+TCpa3KR17WBHSfVHwc1jYPllvcSZfwSlZXbTFmYbpR+P4CNTnfwNr9rnnIB2msK3m7QQQBq5RkutTkeLkP7f8YERyax4n1JFDrQQ9ytMcp/+nZjjrkfOOhZPA1aYkf7f88+qZiKCSNhisxS32NzVuzWtQFhaciYwo1K6R+a9fZyJpeoOQ==",   "ar": [     {       "ac": "*",       "re": "*"     }   ],   "nb": 1568197484,   "na": 1568201084 }' \
        -d '{
        "@context":[
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                {
                    "Vehicle": "http://example.org/vehicle/Vehicle",
                    "brandName": "http://example.org/vehicle/brandName",
                    "speed": "http://example.org/vehicle/speed",
                    "color": "http://example.org/vehicle/color"
                }
        ],
        "id":"urn:ngsi-ld:Vehicle:99",
        "type":"Vehicle",
        "brandName":{
            "type":"Property",
            "value":"Mercedes",
            "encrypt_cpabe":{
            "type":"Property",
            "value":"att1 att2 2of2"
            }
        },
        "speed":{
            "type":"Property",
            "value":80,
            "encrypt_cpabe2":{
            "type":"Property",
            "value":"admin"
            }
        },
        "color":{
            "type":"Property",
            "value":"Red"
        }  
        }'
    ```
