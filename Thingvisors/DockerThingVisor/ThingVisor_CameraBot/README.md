# How it works
Please refer to section 3.3.12 of [Deliverable D3.2](../../../Doc/Fed4IoT-Deliverable-D3.2.pdf) document.

# Build docker image

docker build -t camerabot-tv .

# Local Docker deployment

python3 f4i.py add-thingvisor -i camerabot-tv:latest -n cameraBot -d "cameraBot thingVisor"

# Kubernetes deployment

python3 f4i.py add-thingvisor -c http://$(minikube ip):30133 -n cameraBotTV -d "cameraBot thingVisor" -y "../yaml/thingVisor-cameraBot.yaml"

python3 f4i.py del-thingvisor -c http://$(minikube ip):30133 -n cameraBotTV
