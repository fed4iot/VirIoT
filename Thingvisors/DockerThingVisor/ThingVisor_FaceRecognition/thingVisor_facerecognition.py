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
import json
import traceback
from threading import Timer
from eve import Eve
from flask import request, Response
from bson.objectid import ObjectId
import face_recognition
import cv2
import numpy as np

# -*- coding: utf-8 -*-


# This TV creates just one vthing hardcoded name "detector". If the TV is named "facerec-tv", then:
# the vthing ID is: facerec-tv/detector, and the vthing produces a stream of one NGSI-LD entity,
# which has NGSI-LD identifier: urn:ngsi-ld:facerec-tv:detector, and the NGSI-LD type of the
# produced entity is hardcoded to: FaceDetector
# The vthing supports the following commands: ["start","stop","delete-by-name"].
# Users interact with the vthing by actuating it, i.e. sending commands.
# A target face to be recognized cannot be embedded into a command, but a dedicated HTTP endpoint
# is offered by this TV, so that users can PUT/POST to it to accumulate target pictures
# This endpoint is named facesinput/

# The CameraSensor TV (hosting the sensor vthing) needs a sidecar-tv so that downstream
# clients can ask for TV_IP:TV_PORT_80/sensor/currentframe/xxx
# The FaceRecognition TV needs a sidecar-flavour so that the above TV_IP:TV_PORT_80/sensor/currentframe/xxx is
# proxied everywhere in the platform


# to actuate this detector, use your Broker to channge the "start" Property, as follows:
# start : {
#   type : Property
#   value : {
#     cmd-value : {"job":"dsfsdfdsf234"}
#     cmd-qos : 2
#   }
# }
def on_start(cmd_name, cmd_info, id_LD):
    # the important information is within "cmd-value" of cmd_info
    if "cmd-value" in cmd_info:
        if "job" in cmd_info["cmd-value"]:
            job = cmd_info["cmd-value"]["job"]
            pending_commands[job] = {'cmd_name':cmd_name,'cmd_info':cmd_info,'id_LD':id_LD}
            print("added command for job " + job)
            # give status uodate that we have started
            if "cmd-qos" in cmd_info:
                if int(cmd_info['cmd-qos']) > 0:
                    thingvisor.publish_actuation_response_message(cmd_name, cmd_info, id_LD, "STARTING job: "+job, "status")
        else:
            print("no job in START command")
    else:
        print("no cmd-value for START command")




def periodically_every_fps():
    # use current frame name to GET it from upstream camera sensor
    # See if we have a new frame in upstream TV that sends
    # neutral format as follows:
# {
#    id : urn:ngsi-ld:camerasensor-tv:sensor
#    type : NewFrameEvent
#    frameIdentifier : {
#        type : Property
#        value : "djvn5jntvG"
#    }
# }
    if len(thingvisor.upstream_entities) != 0:
        upstream_vthing = thingvisor.params['upstream_vthingid'].split('/',1)[1] # second element of the split
        id = thingvisor.upstream_entities[0]["frameIdentifier"]["value"]
        # we construct the URL THINGVISOR/sensor/currentframe/djvn5jntvG
        frame_url = "/" + upstream_vthing + "/currentframe/" + id
        url = "http://" + thingvisor.upstream_tv_http_service + frame_url
        r = requests.get(url, proxies=proxies)
        if r.status_code == 200:
            image_bytes=r.content
            decoded_image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_frame = decoded_image[:, :, ::-1]
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_frame)
            if len(face_locations) > 0:
                print("A face appeared")
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                principal_encoding = face_encodings[0]
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_encodings, principal_encoding)
                print(str(matches))

        else:
            print("i got error " + str(r.status_code) + " when going to " + url)
    Timer(1/thingvisor.params['fps'], periodically_every_fps).start()


def encode_target_face_callback(request, response):
    thingvisor.executor.submit(encode_target_face_processor, response)
def encode_target_face_process(request, response):
    data = json.loads(response.get_data())
    if '_id' in data:
        stringid = data["_id"]
        print("Image POSTed on " + stringid)
        # get image record from the collection. collection name is the EVE DOMAIN variable in settings.py
        targetface_collection = app.data.driver.db['faceinputAPI']
        print(str(targetface_collection))
        # need to convert to ObjectId, string not possible directly
        targetface_record = targetface_collection.find_one({'_id':ObjectId(stringid)})
        print(str(targetface_record))
        job = targetface_record["job"]
        name = targetface_record["name"]
        print("JOB " + job + "NAME " + name)
        image_bytes = app.media.get(targetface_record['pic']).read()
        decoded_image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(decoded_image)
        face_encodings = face_recognition.face_encodings(decoded_image, face_locations)
        for face_encoding in face_encodings:
            known_encodings.append(face_encoding)
            known_metadata.append({"face_encoding":face_encoding, "job":job, "name":name})
    else:
        print("The POST of the target picture went wrong")


# globally
pending_commands = dict()
proxies = { "http": "http://viriot-nginx.default.svc.cluster.local",}
known_encodings = []
known_metadata = []
app = Eve()

# main
if __name__ == '__main__':
    app.on_post_POST_faceinputAPI += encode_target_face_process

    thingvisor.initialize_thingvisor("thingVisor_facerecognition")
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

    # enters the main timer thread that obtains the new video frame every fps
    periodically_every_fps()

    # runs eve, and halts the main thread
    app.run(debug=False,host='0.0.0.0',port='5000')
    print("EVE was running. Bye.")
