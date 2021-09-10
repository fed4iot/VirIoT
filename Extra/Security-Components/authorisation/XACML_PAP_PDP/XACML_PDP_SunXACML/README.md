# How to PDP SunXACML

 

 1. Generating the .jar file from the Maven structure
 ```
 cd ./sources
 mvn -U clean install
 ```
The objective of this project is to be included as a maven dependency in other projects such as the *XACMLServletPDP*
[XACMLServletPDP link OdinsLab ](http://odinslab.duckdns.org/security_components/XACMLServletPDP)


### How to import the .jar into the local Maven repository to use it in other projects

```
##### In the folder of PDP-SunXACML we run
##### To generate the jar file
 mvn -U clean install # 

##### To incorporate the jar into the local repository
 mvn install:install-file 
	-Dfile=./PDP-SunXACML-0.0.1-SNAPSHOT.jar 
	-DgroupId=PDP-SunXACML 
  	-DartifactId=PDP-SunXACM 
  	-Dversion=0.0.1-SNAPSHOT 
  	-Dpackaging=jar 
 ```
### How to add the dependency into another Maven project

```
<dependencies>
   ...
    <dependency>
	    <groupId>PDP-SunXACML</groupId>
	    <artifactId>PDP-SunXACML</artifactId>
	    <version>0.0.1-SNAPSHOT</version>
    </dependency>
   ...
</dependencies>
```

