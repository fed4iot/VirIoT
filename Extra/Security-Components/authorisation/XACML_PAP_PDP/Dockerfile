FROM tomcat

COPY ./XACML_PAP/PAPConfigData /usr/local/tomcat/PAPConfigData

RUN apt update
RUN apt install -y maven

WORKDIR /root
RUN  mkdir projects
WORKDIR /root/projects

### XACML

COPY XACMLServletPDP ./XACMLServletPDP
COPY XACML_PDP_SunXACML ./XACML_PDP_SunXACML
COPY XACML_PAP ./XACML_PAP

WORKDIR /root/projects/XACML_PDP_SunXACML
RUN mvn -U clean install

WORKDIR /root/projects/XACML_PDP_SunXACML/
RUN mvn install:install-file -Dfile=./target/PDP-SunXACML-0.0.1-SNAPSHOT.jar  -Dversion=0.0.1-SNAPSHOT   -DgroupId=PDP-SunXACML -DartifactId=PDP-SunXACM -Dpackaging=jar

WORKDIR /root/projects/XACMLServletPDP
RUN mvn -U clean install
RUN mv target/XACMLServletPDP-0.0.1-SNAPSHOT.war /usr/local/tomcat/webapps/XACMLServletPDP.war

WORKDIR /root/projects/XACML_PAP/sources/
RUN mvn -U clean install
RUN mv target/XACML-WebPAP-2.war /usr/local/tomcat/webapps/

WORKDIR /root/
RUN rm -rf projects

