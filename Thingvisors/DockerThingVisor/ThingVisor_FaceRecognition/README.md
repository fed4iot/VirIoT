# Build docker image

docker build -t facerecognition-tv .

# Local Docker deployment

python3 f4i.py add-thingvisor -i facerecognition-tv:latest -n faceRecognition -d "faceRecognition thingVisor"

# Kubernetes deployment

python3 f4i.py add-thingvisor -c http://$(minikube ip):30133 -n faceRecognitionTV -d "faceRecognition thingVisor" -y "../yaml/thingVisor-faceRecognition.yaml"

python3 f4i.py del-thingvisor -c http://$(minikube ip):30133 -n faceRecognitionTV
