# !/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import paho.mqtt.client as mqtt
import paho.mqtt.client as mqtt2
import os
import numpy as np
import datetime
import time
from subprocess import run

# Host = "test.mosquitto.org"
Host = "192.168.11.101"
Port = 1883
Keepalive = 60
MovinWaitSec = 0.01

T_Face = "web_camera_c/facial_recognition/"
T_Move = "web_camera_c/moving_object/"

FACE_PANA = 'FACE_PANA'
MOVE_PANA = 'MOVE_PANA'

# Srctopic = 'web_camera/cam_1'
Srctopic = 'Pana/+'
Color = (255, 255, 255)
Timestamp = "20000101"
Command = "mosquitto_pub -h "
Topicopt = " -t "
Fileopt = " -f "
Fileext = ".jpg"
Facerec = "_facecut_"
Dummyfile = "Dummyfile"

Filename_Moving = "_moving_objct"
Filename_Image = "_image"

cam_no = "pana_1/"

url = 'http://fed4iot:Fed4IoT-JP$@192.168.11.160:65535/nphMotionJpeg?Resolution=640x360&Quality=Standar'

FileDir = "./json-dl/"
cascade_path = "haarcascades/haarcascade_frontalface_alt.xml"


# capture = cv2.VideoCapture(url)

def on_connect(client, userdata, flags, respons_code):
    print("status {0}".format(respons_code))
    client.subscribe(Srctopic)


def on_message(client, userdata, msg):
    print(msg.topic, str(msg.payload, encoding='utf-8'))

    if str(msg.payload, encoding='utf-8') == FACE_PANA:

        print("Do Facial regognition")

        result = facial_recognition()

        print(msg.topic + " " + str(result) + " " + str(msg.payload))

        if result > 0:
            for count in range(result):
                # run(command, shell=True)
                dummy = run(Command + Host + Topicopt + T_Face + cam_no + Timestamp + Facerec + str(
                    count) + Fileopt + FileDir + Timestamp + Facerec + str(count) + Fileext, shell=True)

                print(Command + Host + Topicopt + T_Face + cam_no + Timestamp + Facerec + str(
                    count) + Fileopt + FileDir + Timestamp + Facerec + str(count) + Fileext)
        else:
            # client.publish(dsttopic, str(now))

            dummy = run(Command + Host + Topicopt + T_Face + cam_no + Dummyfile + Fileopt + Dummyfile, shell=True)
            print(Command + Host + Topicopt + T_Face + cam_no + Dummyfile + Fileopt + Dummyfile)

    elif str(msg.payload, encoding='utf-8') == MOVE_PANA:

        print("Do Moving Objects")

        result = moving_object_detection()

        print(msg.topic + " " + str(result) + " " + str(msg.payload, encoding='utf-8'))

        if result > 0:

            # dummy = os.system(Command + Host + Topicopt + T_Move + Timestamp + Filename_Moving + Fileopt + FileDir + Timestamp + Filename_Moving + Fileext)
            dummy = run(
                Command + Host + Topicopt + T_Move + cam_no + Timestamp + Filename_Moving + Fileopt + FileDir + Timestamp + Filename_Moving + Fileext,
                shell=True)
            print(
                Command + Host + Topicopt + T_Move + Timestamp + Filename_Moving + Fileopt + FileDir + Timestamp + Filename_Moving + Fileext)

        else:

            # dummy = os.system(Command + Host + Topicopt + T_Move + Dummyfile + Fileopt + Dummyfile)
            dummy = run(Command + Host + Topicopt + T_Move + cam_no + Dummyfile + Fileopt + Dummyfile, shell=True)
            print(Command + Host + Topicopt + T_Face + Dummyfile + Fileopt + Dummyfile)

        # dummy = os.system(Command + Host + Topicopt + T_Move + Timestamp + Filename_Image + Fileopt + FileDir + Timestamp + Filename_Image + Fileext)
        dummy = run(
            Command + Host + Topicopt + T_Move + cam_no + Timestamp + Filename_Image + Fileopt + FileDir + Timestamp + Filename_Image + Fileext,
            shell=True)
        print(
            Command + Host + Topicopt + T_Move + cam_no + Timestamp + Filename_Image + Fileopt + FileDir + Timestamp + Filename_Image + Fileext)
        print("end.")

    else:

        print("Do nothing")

        # image_capture_moving();

        # dummy = os.system(Command + Host + Topicopt + T_Move_Jetson_1 + Timestamp + "_1st" + Fileopt + FileDir + Timestamp + "_1st" + Fileext)
        # print(Command + Host + Topicopt + T_Move_Jetson_1 + Timestamp + "_1st" + Fileopt + FileDir + Timestamp + "_1st" + Fileext)

        # dummy = os.system(Command + Host + Topicopt + T_Move_Jetson_1 + Timestamp + "_2nd" + Fileopt + FileDir + Timestamp + "_2nd" + Fileext)
        # print(Command + Host + Topicopt + T_Move_Jetson_1 + Timestamp + "_2nd" + Fileopt + FileDir + Timestamp + "_2nd" + Fileext)


def image_capture():
    global Timestamp

    # image = cv2.imread('image.jpg')
    # for i in range (6) :
    #    ret, image = capture.read()
    ret, image = capture.read()

    dt_now = datetime.datetime.now()
    Timestamp = dt_now.strftime("%Y%m%d_%H%M%S")

    print("capture");

    cv2.imwrite(FileDir + Timestamp + ".jpg", image)
    cv2.imshow('frame', image)

    print("write");


def image_capture_moving():
    global Timestamp

    # image = cv2.imread('image.jpg')
    for i in range(6):
        ret, image = capture.read()

    time.sleep(MovinWaitSec)

    ret, image2 = capture.read()

    dt_now = datetime.datetime.now()
    Timestamp = dt_now.strftime("%Y%m%d_%H%M%S")

    print("capture");

    cv2.imwrite(FileDir + Timestamp + "_1st.jpg", image)
    cv2.imwrite(FileDir + Timestamp + "_2nd.jpg", image2)

    print("write");


def facial_recognition():
    global Timestamp

    # image = cv2.imread('face0.jpg')
    # for i in range (6) :
    ret, image = capture.read()

    dt_now = datetime.datetime.now()
    Timestamp = dt_now.strftime("%Y%m%d_%H%M%S")

    print("capture")

    # gray scale
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    print("gray scale");

    # getting feature values in cascade classifiers
    cascade = cv2.CascadeClassifier(cascade_path)

    print("cascade");

    # facial recognition
    facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=1, minSize=(1, 1))

    print("facial action");

    if len(facerect) > 0:

        print("hit");

        for rect in facerect:
            cv2.rectangle(image, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), Color, thickness=2)
            print("rectangle");

        count = 0
        for x, y, w, h in facerect:
            facecut = image[y:y + h, x:x + w]
            print("face cut");
            cv2.imwrite(FileDir + Timestamp + Facerec + str(count) + ".jpg", facecut)
            count = count + 1

    cv2.imwrite(FileDir + Timestamp + ".jpg", image)
    # cv2.imshow('frame',image)

    print("facial end");

    return len(facerect)


def moving_object_detection():
    global Timestamp
    average = None

    for timer in range(2):

        # image = cv2.imread('image.jpg')
        for i in range(6):
            ret, image = capture.read()

        dt_now = datetime.datetime.now()
        Timestamp = dt_now.strftime("%Y%m%d_%H%M%S")

        print("capture");

        # gray scale
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        print("gray scale");

        if average is None:
            average = image_gray.copy().astype("float")
            print("continue")
            time.sleep(MovinWaitSec)
            continue

        cv2.accumulateWeighted(image_gray, average, 0.5)
        print("accumulate")

        delta = cv2.absdiff(image_gray, cv2.convertScaleAbs(average))
        print("delta")

        threshold = cv2.threshold(delta, 3, 255, cv2.THRESH_BINARY)[1]
        print("threshold")

        threshold = cv2.medianBlur(threshold, 7)

        countours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print("count")

        # image_count = cv2.drawContours(image, countours, 0, (0,255,0), 3)

        cv2.imwrite(FileDir + Timestamp + Filename_Image + Fileext, image)
        print("gray")
        cv2.imwrite(FileDir + Timestamp + Filename_Moving + Fileext, threshold)
        print("thres")
        # cv2.imwrite(Timestamp + "_image.jpg", image_count)
        # print("image")

    print("moving end");

    return len(countours)


if __name__ == '__main__':
    #capture = cv2.VideoCapture(url)
    capture = cv2.VideoCapture()
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(Host, Port, Keepalive)
    client.loop_forever()
'''
    #image_capture()
    facial_recognition()
    #image_capture_moving()
    #moving_object_detection()

    cv2.waitKey(0)
    capture.release()
    cv2.destroyAllWindows()
'''
