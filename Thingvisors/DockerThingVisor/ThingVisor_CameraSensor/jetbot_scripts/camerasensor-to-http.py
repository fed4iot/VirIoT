from camera_mod import Camera
import pickle
import requests
import time
import json
import cv2
import numpy as np
import io
import sys


##### globals
fps=1
# in case of error in POST
sleep = 0


# camera
print("Create camera")
camera = Camera(width=600,height=600,fps=fps)


# load camera parameters
calibration_params = pickle.load( open( "calibration.p", "rb" ) )

addr = sys.argv[1]
print("Connecting to "+addr)

# execute function
def callback(change):
    global sleep
    image = change['new'] 
    # undistort
    image = cv2.undistort(image, calibration_params['mtx'], calibration_params['dist'], None)
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    # compress image to jpeg
    is_success, buffer = cv2.imencode(".jpg", small_frame)
    # need a stream to send it via http requests
    io_buf = io.BytesIO(buffer)
    img_str = io_buf.getvalue()
    io_buf.seek(0)
    
    # send image + timestamp to http server
    server_url = addr + '/framesinput'
    payload = {"observedAt": int(time.time())}
    files = {
         'json': ("metadata", json.dumps(payload), 'application/json'),
         'file': ("cameraframe", img_str, 'application/octet-stream')
    }
    try:
        if(sleep == 0):
            r = requests.post(server_url, files=files)
        else:
            print("SLEEPING")
            time.sleep(sleep)
            sleep = 0
    except Exception as e:
        print(e)
        sleep = 1


# on the camera object observe the field named "value"
camera.observe(callback, names='value')


# forever, so that main thread does not exit
while True:
    time.sleep(10)

camera.unobserve(execute, names='value')
