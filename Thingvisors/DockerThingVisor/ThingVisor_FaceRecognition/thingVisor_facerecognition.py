# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This is a Fed4IoT ThingVisor for Face Recognition

import thingVisor_generic_module as thingvisor

import requests
from threading import Timer
from eve import Eve
from flask import request, Response


# -*- coding: utf-8 -*-


# This TV creates just one vthing hardcoded name "detector". If the TV is named "facerec-tv", then:
# the vthing ID is: facerec-tv/detector, and the vthing produces a stream of one NGSI-LD entity,
# which has NGSI-LD identifier: urn:ngsi-ld:facerec-tv:detector, and the NGSI-LD type of the
# produced entity is hardcoded to: FaceDetector
# The vthing supports the following commands: ["start","stop","set-face-feature","delete-by-name"].
# Users interact with the vthing by actuating it, i.e. sending commands.
# A target face to be recognized cannot be embedded into a command, but a dedicated HTTP endpoint
# is offered by this TV, so that users can PUT/POST to it to accumulate target pictures

# The CameraSensor TV (hosting the sensor vthing) needs a sidecar-tv so that downstream
# clients can ask for TV_IP:TV_PORT_80/sensor/currentframe/xxx
# The FaceRecognition TV needs a sidecar-flavour so that the above TV_IP:TV_PORT_80/sensor/currentframe/xxx is
# proxied everywhere in the platfors as 

app = Eve()
proxies = { "http": "http://viriot-nginx.default.svc.cluster.local",}

def on_post_PATCH_faceInput(request,lookup):
    try:
        data=json.loads(lookup.get_data())

        if '_id' in data:
            id=data['_id']
            name=image_to_name_mapping[id]

            print("")
            print("Image patched on "+id)
            print("")

            # get image
            faceInput = app.data.driver.db['faceInput']
            a = faceInput.find_one({'_id':id})
            image=app.media.get(a['image'])

            # send all data to the camera system
            _camera_ip, _camera_port=get_camera_ip_port()
            payload = {'name':name,'id':id}
            files={'image':image}
            res=requests.post("http://"+_camera_ip+':'+_camera_port+'/images', data=payload, files=files)

            # check response
            if res.status_code>=400:
                print("Error when posting to the camera system: "+str(res.status_code))
                return 
    except:
        traceback.print_exc()


def on_post_POST_faceOutput(request,lookup):
    try:
        data=json.loads(lookup.get_data())

        if '_id' in data:
            id=request.form['id']
            name=image_to_name_mapping[id]

            print("")
            print("Status changed for person "+name)
            print("New status: "+str(request.form['result']))
            print("")

            # send new command status
            # to inform that the person status has changed
            payload={
                "status": request.form['result'],
                "name": name,
                "count": image_count[name],
                "timestamp": request.form['timestamp'],
                "link_to_base_image": "/faceInput/"+id+"/image",
                "link_to_current_image": "/faceOutput/"+data['_id']+"/image"
            }

            mqtt_data_thread.publish_actuation_response_message(
                command_data[id]['cmd_name'],
                command_data[id]['cmd_info'],
                command_data[id]['id_LD'],
                payload,
                "status"
            )
    except:
        traceback.print_exc()

    
def on_start(self, cmd_name, cmd_info, id_LD, actuatorThread):
    print("Sending start command to camera system")

    _camera_ip, _camera_port=get_camera_ip_port()
    res=requests.get("http://"+_camera_ip+':'+_camera_port+'/start')

    # publish command result
    if "cmd-qos" in cmd_info:
        if int(cmd_info['cmd-qos']) > 0:
            self.send_commandResult(cmd_name, cmd_info, id_LD, res.status_code)


def periodically_every_fps():
    # use current frame name to GET it from upstream camera sensor
    # see if we have a new frame
    if len(thingvisor.upstream_entities) != 0:
        upstream_vthing = thingvisor.params['upstream_vthingid'].split('/',1)[1] # second element of the split
        id = thingvisor.upstream_entities[0]["frameIdentifier"]["value"]
        frame_url = "/" + upstream_vthing + "/currentframe/" + id
        url = "http://" + thingvisor.upstream_tv_http_service + frame_url
        r = requests.get(url, proxies=proxies)
        if r.status_code == 200:
            print("i got " + id + + " from " + url)
        else:
            print("i got error " + str(r.status_code) + " when going to " + url)
    Timer(1/thingvisor.params['fps'], periodically_every_fps).start()


# main
if __name__ == '__main__':
    thingvisor.initialize_thingvisor()
    # create the detector vThing: name, type, description, array of commands
    thingvisor.initialize_vthing("detector","FaceRecognitionEvent","faceRecognition virtual thing",["start","stop","delete-by-name"])
    print("All vthings initialized")  
    print(thingvisor.v_things['detector'])

    if not 'upstream_vthingid' in thingvisor.params:
        print("NO UPSTREAM camera sensor where to fetch frames has been configured. Waiting for it.")
    if 'fps' in thingvisor.params:
        print("parsed fps parameter: " + str(thingvisor.params['fps']))
    else:
        thingvisor.params['fps'] = 2
        print("defaulting fps parameter: " + str(thingvisor.params['fps']))

    # Map images to names
    image_to_name_mapping={}
    # store image count for every name
    image_count={}

    # set eve callbacks
    app.on_post_PATCH_faceInput += on_post_PATCH_faceInput
    app.on_post_POST_faceOutput += on_post_POST_faceOutput

    # enters the main timer thread that obtains the new video frame every fps
    periodically_every_fps()

    # runs eve, and halts the main thread
    app.run(debug=False,host='0.0.0.0',port='5000')
    print("EVE was running. Bye.")
