'''
カメラ映像から人の顔を検出
author：
datetime：2021.2.20
'''
#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import config

Color = (255, 255, 255)


def facial_detection(image):

    # gray scale
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # getting feature values in cascade classifiers
    cascade = cv2.CascadeClassifier(config.cascade_frontal_face_alt)

    # facial recognition
    # facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=1, minSize=(1, 1))
    # facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.2, minNeighbors=5, minSize=(20, 20))
    facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.2, minNeighbors=3, minSize=(10, 10))

    if len(facerect) > 0:

        for rect in facerect:

            cv2.rectangle(image, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), Color, thickness=2)

        for (x, y, w, h) in facerect:
            cv2.rectangle(image_gray, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = image_gray[y:y + h, x:x + w]
            roi_color = image[y:y + h, x:x + w]

    return image, len(facerect)
