FROM python:3

### eve backend implementing a simple NGSI-LD REST API

RUN pip3 install eve

COPY settings.py /
COPY eve_backend.py /

CMD [ "python", "./eve_backend.py" ]
