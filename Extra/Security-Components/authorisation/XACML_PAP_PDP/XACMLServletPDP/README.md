# How to ServletXACMLPDP

 
0. Adding the dependencies of the SunXACML_PDP
[Instructions of the README to import the .jar in Maven](http://odinslab.duckdns.org/security_components/XACML_PDP_SunXACML/raw/master/README.md)

 1. Generating the .war file from the Maven structure
 ```
 mvn -U clean install
 ```

1. Add the .war in the target folder to the Dockerized tomcat environment with the XACML_WebPAP-2 project.

2. Test the service with the HTTP PDP client project.
[Link to the HTTP PDP project](http://odinslab.duckdns.org/security_components/XACML_HTTPClient)

