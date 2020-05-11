# Docker Deployment  

Images of VirIoT components are available in [DockerHub](https://hub.docker.com/u/fed4iot). 
Optionally, they can be built locally as [follows](Optional%20docker%20build.md).  

## Initial configurations 
In order to use the Docker deployment, it is required to:
* open the range of ports from `32768` to `61000`  
* have `python3` with `flask flask_cors pymongo paho-mqtt docker`, if not present use `pip3 install`  

### Clone Git Repository

```bash  
git clone https://github.com/fed4iot/VirIoT.git
cd VirIoT  
```

### Run mosquitto MQTT server for Internal Information Sharing

```bash  
sudo service mosquitto start
```

### Run MongoDB system-database in a Docker container

```bash  
docker run -d --name mongo-container -p 32768:27017 mongo:3.4.18  
```  
Mongo is reachable through `32768` on public IP.

If already run but stopped, use `docker start mongo-container`.
To reset the DB delete the container and run it again.  
To explore DB use `mongo-compass` and connect to the IP address of the container.


### Run Master-Controller

Configure the right IP addresses and ports editing the settings template file `settings-docker-template.py` with your 
correct configurations and copy it to the `Master-Controller/data` folder.
The default port of Master-Controller is the `8090` where it exposes the VirIoT REST API.

```bash  
cd Master-Controller  
# edit settings-docker-template.py  
vim settings-docker-template.py  
# after the edits copy and rename it to data/settings.py  
cp settings-docker-template.py data/settings.py  
```  

Install all the dependencies required for the Master-Controller to properly work, using `pip3`:  

```bash  
# for install all dependencies use the file requirements.txt in the folder Master-Controller  
pip3 install -r requirements.txt  
```  
 
The file `db_setup.py` is used by `master-controller.py` for setting parameters, such as the password of the 'admin' 
user whose default value is 'passw0rd'. It is not necessary to change it unless to change the password.
   
Run the master controller:  

```bash  
python3 master-controller.py  
```  
  
