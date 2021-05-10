from camera_mod import Camera
import pickle
import requests
import time
import json
import cv2
import numpy as np
import io


##### globals
fps=1


# camera
print("Create camera")
camera = Camera(width=600,height=600,fps=fps)


# load camera parameters
calibration_params = pickle.load( open( "calibration.p", "rb" ) )


# execute function
def callback(change):
    image = change['new']
    
    # undistort
    image = cv2.undistort(image, calibration_params['mtx'], calibration_params['dist'], None)
    
    # Resize frame of video to 1/4 size for faster face recognition processing
    #small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    small_frame = image

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # compress image to jpeg
    is_success, buffer = cv2.imencode(".jpg", image)
    # need a stream to send it via http requests
    io_buf = io.BytesIO(buffer)
    img_str = io_buf.getvalue()
    io_buf.seek(0)
    
    # send image + timestamp to http server
    addr = 'http://13.80.153.4:32173'
    server_url = addr + '/framesinput'
    payload = {"observedAt": int(time.time())}
    files = {
         'json': ("metadata", json.dumps(payload), 'application/json'),
         'file': ("cameraframe", img_str, 'application/octet-stream')
    }
    r = requests.post(server_url, files=files)
    print(r.content)

# on the camera object observe the field named "value"
camera.observe(callback, names='value')


# forever
while True:
    time.sleep(0.1)

camera.unobserve(execute, names='value')

