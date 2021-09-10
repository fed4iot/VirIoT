# How to XACML PAP

 

 1. Generating the .war file from the Maven structure
 ```
 cd ./sources
 mvn -U clean install
 ```
 2. Testing the project in standalone mode with Docker
 ```
 cd ./deployment
 ```
```
docker build --tag xacml .
docker run --privileged -p 8080:8080 xacml
```

### To access the service to verify that is running

#### PAP service
```
http://localhost:8080/XACML-WebPAP-2
```

You will see the main webpage of the PAP service

### Importing the project into Eclipse
	 3.1 Create new workspace 
	 3.2 Import Existing Maven Project
	 3.3 Add server (Tomcat 9.0)
	 3.5 Click on XACML-WebPAP project > Run As > Run on Server
	 
1. To run the project in Eclipse instead of Docker (for development purposes) 
	1.1 Change the content of /WEB-INF/config.xml to the real path where *PAPConfigData/Connectors/diskConnectorConfig.xml* and *PAPConfigData/Connectors/existConnectorConfig.xml* are.
	1.2 Change the content of *diskConnectorConfig.xml* file to point to where the correct files are.

