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
from threading import Timer, Lock
from eve import Eve
from eve.methods.post import post_internal
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
# The vthing supports the following commands: ["startjob","deletejob"].
# Users interact with the vthing by actuating it, i.e. sending commands.
# A target face to be recognized cannot be embedded into a command, but a dedicated HTTP endpoint
# is offered by this TV, so that users can PUT/POST to it to accumulate target pictures
# This endpoint is named targetfaces/

# The CameraSensor TV (hosting the sensor vthing) needs a sidecar-tv so that downstream
# clients can ask for TV_IP:TV_PORT_80/sensor/currentframe/xxx
# The FaceRecognition TV needs a sidecar-flavour so that the above TV_IP:TV_PORT_80/sensor/currentframe/xxx is
# proxied everywhere in the platform


# to actuate this detector, use your Broker to channge the "startjob" Property, as follows:
# startjob : {
#   type : Property
#   value : {
#     cmd-value : {"job":"dsfsdfdsf234"}
#     cmd-qos : 2
#   }
# }
def process_job_command(cmd_name, cmd_info, id_LD, jobtype):
    # the important information is within "cmd-value" of cmd_info
    if "cmd-value" in cmd_info:
        if "job" in cmd_info["cmd-value"]:
            job = cmd_info["cmd-value"]["job"]
            # protect the pending_commands from other threads using it
            # while we insert/delete a new job
            known_encodings_lock.acquire()
            if jobtype == "START":
                pending_commands[job] = {'cmd_name':cmd_name,'cmd_info':cmd_info,'id_LD':id_LD}
            else if jobtype == "DELETE":
                pending_commands.pop(job, "NOT FOUND")
                #TODO
                #TODO REMOVE PICTURES OF THE JOB------------------------------
                #TODO
            else:
                print("unrecognized jobtype"+jobtype
            print(jobtype+" command for job " + job + " so we have " + str(len(pending_commands))+ " jobs")
            # un protect the pending_commands from other threads using it
            # while we insert/delete a new job
            known_encodings_lock.release()
            # give status update that we have started/deleted
            if jobtype == "START" or jobtype == "DELETE":
                if "cmd-qos" in cmd_info:
                    if int(cmd_info['cmd-qos']) > 0:
                        thingvisor.publish_actuation_response_message(cmd_name, cmd_info, id_LD, "Just received "+jobtype+" job: "+job, "status")
        else:
            print("no job in command "+jobtype)
    else:
        print("no cmd-value for command "+jobtype)


def on_startjob(cmd_name, cmd_info, id_LD):
    process_job_command(cmd_name, cmd_info, id_LD, "START")


def on_deletejob(cmd_name, cmd_info, id_LD):
    process_job_command(cmd_name, cmd_info, id_LD, "DELETE")


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
                # protect the arrays from other threads inserting or deleting faces
                # while we run the recognition for the current frame
                known_encodings_lock.acquire()
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_encodings, principal_encoding)
                print("MATCH: "+str(matches))
                matching_responses = []
                # go through metadata and consider only those in active jobs (that have matched!)
                for index, metadata in enumerate(known_metadata):
                    if matches[index]: #if the element at position 'index' in 'matches' array is True
                        print("M"+str(index)+" "+metadata["job"]+" "+str(len(pending_commands)))
                        # if pending_commands contains a key for the string representing
                        # the "job" field of the current metadata of the loop
                        if metadata["job"] in pending_commands.keys():
                            #TODO accumulate metainfo for every match into an array so that
                            # when i exit the loop i can send them
                            # via a future executor.submit that takes whatever time it needs
                            # I (deep)copy them because when i exit the lock somebody can remove them
                            # (also strings, i am not sure they are strings; in any case it does not harm)
                            matching_responses.append({
                                "job":metadata["job"].deepcopy(),
                                "name":metadata["name"].deepcopy(),
                                "cmd_name":pending_commands[job]["cmd_name"].deepcopy(),
                                "cmd_info":pending_commands[job]["cmd_info"].deepcopy(),
                                "id_LD":pending_commands[job]["id_LD"].deepcopy(),
                                "payload":metadata.deepcopy()
                            })
                            print("CHECK YOUR BROKER: " + str(payload))
                # un protect the arrays from other threads inserting or deleting faces
                # while we run the recognition for the current frame
                known_encodings_lock.release()
                thingvisor.executor.submit(insert_matching_face_and_send_responses, image_bytes, matching_responses)
        else:
            print("i got error " + str(r.status_code) + " when going to " + url)
    Timer(1/thingvisor.params['fps'], periodically_every_fps).start()


def insert_matching_face_and_send_responses(image_bytes, matching_responses):
    # store the face that matches into the local storage
    with app.app_context():
        with app.test_request_context():
            post_internal('recognizedfaces', {"_id": id})
    for matching_response in matching_responses:
        #TODO BLA
        thingvisor.publish_actuation_response_message(cmd_name, cmd_info, id_LD, payload, type_of_message)


def encode_target_face_callback(request, response):
    thingvisor.executor.submit(encode_target_face_processor, response)
def encode_target_face_process(request, response):
    data = json.loads(response.get_data())
    if '_id' in data:
        stringid = data["_id"]
        print("Image POSTed on " + stringid)
        # get image record from the collection. collection name is the EVE DOMAIN variable in settings.py
        targetface_collection = app.data.driver.db['targetfacesAPI']
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
        # protect the known_encodings and _metadata arrays from the recognition
        # thread running in parallel while we modify them , because recognition
        # could fail simply because the _encodings and _metadata got out of sync
        # in terms of indexes not being aligned anymore
        known_encodings_lock.acquire()
        for face_encoding in face_encodings:
            known_encodings.append(face_encoding)
            # for "original_pic" i convert the mongo objectid of the media pic to a string
            known_metadata.append({"job":job, "name":name, "original_pic":"/media/"+str(targetface_record['pic'])})
        # un protect the known_encodings and _metadata arrays from the recognition
        # thread running in parallel while we modify them
        known_encodings_lock.release()
    else:
        print("The POST of the target picture went wrong")


# main
#if __name__ == '__main__':
thingvisor.initialize_thingvisor("thingVisor_facerecognition")

# global variables
pending_commands = dict()
known_encodings = []
known_metadata = []
# the three arrays above must be protecterd by a guard lock because
# they have to stay in sync
known_encodings_lock = Lock()
# EVE is used to store and fetch images in a mongo DB
app = Eve()
app.on_post_POST_targetfacesAPI += encode_target_face_process
proxies = { "http": "http://viriot-nginx.default.svc.cluster.local",}
# create the detector vThing: name, type, description, array of commands
thingvisor.initialize_vthing("detector","FaceRecognitionEvent","faceRecognition virtual thing",["startjob","deletejob"])
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
