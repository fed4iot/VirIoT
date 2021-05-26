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

app = Eve()


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

    
def on_delete_by_name(self, cmd_name, cmd_info, id_LD):
    try:
        if "cmd-qos" in cmd_info and int(cmd_info['cmd-qos']) == 2:
            publish_actuation_response_message(cmd_name, cmd_info, id_LD, "Error: cmd-qos must be 0 or 1.", "result")
            return
        
        # get the name of the person to delete
        nuri=get_silo_name(cmd_info['cmd-nuri'])
        name=nuri+"_"+cmd_info['cmd-value']['name']

        # check if this name is registered
        if name not in image_count:
            if "cmd-qos" in cmd_info:
                if int(cmd_info['cmd-qos']) > 0:
                    self.publish_actuation_commandResult_message(cmd_name, cmd_info, id_LD, "The name "+name+" doesn't exist.")
            return
        
        # send to the camera system the deletion request
        _camera_ip, _camera_port=get_camera_ip_port()
        res=requests.delete("http://"+_camera_ip+':'+_camera_port+'/people/'+name)

        # check response
        if res.status_code>=400:
            if "cmd-qos" in cmd_info:
                if int(cmd_info['cmd-qos']) > 0:
                    self.publish_actuation_commandResult_message(cmd_name, cmd_info, id_LD, res.status_code)
            return

        # find all ids of images to delete
        temp=[]
        for x in image_to_name_mapping:
            if image_to_name_mapping[x]==name:
                temp.append(x)
        
        # delete images
        with app.app_context():
            with app.test_request_context():
                for x in temp:
                    #deleteitem_internal('faceInput', {"_id": x})
                    del image_to_name_mapping[x]
        del image_count[name]

        print("")
        print("Deleted person "+name)
        print("Current status:")
        print(image_to_name_mapping)
        print(image_count)
        print("")

        if "cmd-qos" in cmd_info:
            if int(cmd_info['cmd-qos']) > 0:
                self.publish_actuation_commandResult_message(cmd_name, cmd_info, id_LD, "OK")
    except:
        traceback.print_exc()



# main
if __name__ == '__main__':
    thingvisor.initialize_thingvisor()
    # create the detector vThing: name, type, description, array of commands
    detector=thingvisor.initialize_vthing("detector","FaceRecognitionEvent","faceRecognition virtual thing",["start","stop","delete-by-name"])
    print("All vthings initialized")  
    print(thingvisor.v_things['detector'])


    if 'upstream_camera_sensor' in thingvisor.params:
        print("parsed upstream_camera_sensor parameter: " + str(thingvisor.params['upstream_camera_sensor']))
    else:
        print("NO UPSTREAM camera sensor where to fetch frams has been configured. Exiting.")
        exit()
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

    # runs eve, and halts the main thread
    app.run(debug=False,host='0.0.0.0',port='5000')
    print("EVE was running. Bye.")
