'''
OpenCV　カメラの画像を読み込む
author：
datetime：2021.2.20
'''
# !/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import config


class WebCamera:

    def __init__(self):

        self.camera_id = config.webcam_id
        self.capture = cv2.VideoCapture(self.camera_id)
        self.result = True

    def open_camera(self):

        if self.capture.isOpened():

            camera_width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            camera_height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            camera_fps = self.capture.get(cv2.CAP_PROP_FPS)
            print("camera width = {0}, height = {1}, fps = {2}".format(camera_width, camera_height, camera_fps))
            self.result = True
            return self.result, self.capture
        else:

            print('Failed to open camera')
            self.result = False
            return self.result, None

    def __del__(self):

        self.capture.release()


class PanaCamera:

    def __init__(self):

        self.camera_id = config.pana_cam_no
        self.capture = cv2.VideoCapture(config.pana_cam_url)
        self.result = True

    def open_camera(self):

        if self.capture.isOpened():

            camera_width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            camera_height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            camera_fps = self.capture.get(cv2.CAP_PROP_FPS)
            print("camera width = {0}, height = {1}, fps = {2}".format(camera_width, camera_height, camera_fps))
            self.result = True
            return self.result, self.capture
        else:

            print('Failed to open camera')
            self.result = False
            return self.result, None

    def __del__(self):

        self.capture.release()
