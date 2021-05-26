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

# This is a Fed4IoT ThingVisor for sharing one stream of pictures to multiple
# downstream ThingVisors


import thingVisor_generic_module as thingvisor


import redis
rdis = redis.Redis(unix_socket_path="/app/redis/redis.sock")
buffername = "bufferofframes"

from flask import Flask, request, Response
app=Flask(__name__)


@app.route('/currentframe/<randomid>')
def GET_current_frame_by_id(randomid):
    ### i could offer the img_str buffer via HTTP at this point
    headers={"Content-disposition": "attachment"}
    headers["Cache-Control"]="no-cache"
    print("GET ", randomid)

    try:
        # get from the redis stream named "buffername" just 1 item (from randomid to randomid)
        list_of_matching_results = rdis.xrange(buffername,randomid,randomid)
        # we get back a list of results (with only 1 result). we pick it
        first_result = list_of_matching_results[0]
        # each result is a tuple where first element [0] is the id (key),
        # second element [1] is the dict (value) holding the frame information
        frame_information = first_result[1]
        data = frame_information[b"data"]
        observedAt = frame_information[b"observedAt"]
    except:
        data = ""

    return Response(data, mimetype='image/jpeg', headers=headers)


@app.route('/framesinput',methods=['POST'])            
def POST_frames():
    print(request.files)
    print(type(request.files))
    print(len(request.files))
    for keys,values in request.files.items():
        print(keys)
        print(values)
    uploaded_cameraframe = request.files.get("file")
    metadata = json.load(request.files.get("json"))
    data = uploaded_cameraframe.read()
    # Redis client instances can safely be shared between threads.
    # Internally, connection instances are only retrieved from the connection
    # pool during command execution, and returned to the pool directly after.
    # Command execution never modifies state on the client instance.
    # We keep at most BUFFERSIZE images in the buffer
    id = rdis.xadd(buffername, {"data":data, "observedAt":metadata["observedAt"]}, maxlen=thingvisor.params['buffersize'], approximate=True)

    print("Pushed to redis ", id)
    return 'success'

# main
if __name__ == '__main__':
    thingvisor.initialize_thingvisor()
    # create the detector vThing: name, type, description, array of commands
    detector=thingvisor.initialize_vthing("sensor","NewFrameEvent","camera sensor to distribute frames",[])
    print("All vthings initialized")

    if thingvisor.params:
        if 'buffersize' in thingvisor.params:
            print("parsed buffersize parameter: " + str(thingvisor.params['buffersize']))
    
    # starting flask
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)