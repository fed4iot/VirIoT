# To run the XACML components

```
docker build --tag xacml .
docker run --privileged -p 8080:8080 xacml
```

# To access the service to verify that is running

#### PAP service
```
http://localhost:8080/XACML-WebPAP-2
```

You will see the main webpage of the PAP service

