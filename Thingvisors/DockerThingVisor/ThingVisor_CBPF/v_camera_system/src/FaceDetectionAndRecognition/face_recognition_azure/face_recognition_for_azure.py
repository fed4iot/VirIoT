'''
Azure API 顔認証
author：
datetime：2021.2.20
'''
# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import uuid
from PIL import Image, ImageDraw
from time import sleep
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
from face_recognition_azure.create_face_client import face_client

# <snippet_persongroupvars>
# Used in the Person Group Operations and Delete Person Group examples.
# You can call list_person_groups to print a list of preexisting PersonGroups.
# SOURCE_PERSON_GROUP_ID should be all lowercase and alphanumeric. For example, 'mygroupname' (dashes are OK).
PERSON_GROUP_ID = str(uuid.uuid4())  # assign a random ID (or name it anything)

# Used for the Delete Person Group example.
TARGET_PERSON_GROUP_ID = str(uuid.uuid4())  # assign a random ID (or name it anything)

'''
Detect faces in two images (get ID), draw rectangle around a third image.
'''


def single_face_detect(image_path):
    '''

    :param image_path:
    :return:
    '''

    # Detect a face in an image that contains a single face
    single_face_image_path = image_path
    # single_image_name = os.path.basename(single_face_image_path)
    # print('single_face_image_path: ', single_face_image_path)
    # We use detection model 3 to get better performance.
    find_image = open(single_face_image_path, 'rb')
    try:
        detected_faces = ''
        detected_faces = face_client.face.detect_with_stream(image=find_image, detection_model='detection_03')
    except Exception as e:
        print(e)
        sleep(5)

    if not detected_faces:
        # raise Exception('No face detected from image {}'.format(single_image_name))
        return None

    # Display the detected face ID in the first single-face image.
    # Face IDs are used for comparison to faces (their IDs) detected in other images.
    # print('Detected face ID from', single_image_name, ':')
    for face in detected_faces:
        # print(face.face_id)
        continue
    # Save this ID for use in Find Similar
    first_image_face_ID = detected_faces[0].face_id

    return first_image_face_ID


def multi_face_detect(image_path=None, image=None):
    '''
    :param image_path: 探したい人の画像の保存パス　image/find_image/
    :param image: カメラのフィルムイメージ
    :return: 顔識別結果、イメージファイルの名前
    '''
    # Each detected face gets assigned a new ID

    if image_path is None and image is None:
        # raise Exception('No face detected from image.')
        return None, None
    if image is None:
        multi_face_image_path = image_path
        multi_image_name = os.path.basename(multi_face_image_path)
        detect_image = open(multi_face_image_path, 'rb')
        detect_show_image = Image.open(multi_face_image_path, 'r')

    else:
        detect_image = image
        detect_show_image = image
    # We use detection model 3 to get better performance.

    try:
        multi_detected_faces = ''
        multi_detected_faces = face_client.face.detect_with_stream(image=detect_image, detection_model='detection_03')
    except Exception as e:
        print(e)
        sleep(5)

    # print('Detected face IDs from', multi_image_name, ':')
    if not multi_detected_faces:
        # raise Exception('No face detected from image {}.'.format(multi_image_name))
        return None, None
    else:
        for d_face in multi_detected_faces:
            print(d_face.face_id)
            continue
        print_image_draw_rect(detect_show_image, multi_detected_faces)

    return multi_detected_faces, multi_image_name


# Convert width height to a point in a rectangle
def getRectangle(faceDictionary):
    '''

    :param faceDictionary: 顔のデーター
    :return: 顔枠の位置
    '''
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    right = left + rect.width
    bottom = top + rect.height

    return ((left, top), (right, bottom))


def print_image_draw_rect(image, detected_faces):
    '''
    Print image and draw rectangles around faces
    :param image:
    :param detected_faces:
    :return:
    '''

    # For each face returned use the face rectangle and draw a red box.
    # print('Drawing rectangle around face... see popup for results.')
    draw = ImageDraw.Draw(image)
    for d_face in detected_faces:
        draw.rectangle(getRectangle(d_face), outline='red')

    # Display the image in the users default image browser.
    # image.show()


def find_similar_face(find_face_id, detected_faces, multi_image_name):
    '''
    Find a similar face
    This example uses detected faces in a group photo to find a similar face using a single-faced image as query.
    :param find_face_id:
    :param detected_faces:
    :param multi_image_name:
    :return:
    '''

    # Search through faces detected in group image for the single face from first image.
    # First, create a list of the face IDs found in the second image.
    second_image_face_IDs = list(map(lambda x: x.face_id, detected_faces))
    # Next, find similar face IDs like the one detected in the first image.
    similar_faces = face_client.face.find_similar(face_id=find_face_id, face_ids=second_image_face_IDs)
    if not similar_faces:
        print('No similar faces found in', multi_image_name, '.')
        return False
    # Print the details of the similar faces detected
    else:
        # print('Similar faces found in', multi_image_name)
        for face in similar_faces:
            first_image_face_ID = face.face_id
            # The similar face IDs of the single face image and the group image do not need to match,
            # they are only used for identification purposes in each image.
            # The similar faces are matched using the Cognitive Services algorithm in find_similar().
            face_info = next(x for x in detected_faces if x.face_id == first_image_face_ID)
            if face_info:
                print('  Face ID: ', first_image_face_ID)
                print('  Face rectangle:')
                print('    Left: ', str(face_info.face_rectangle.left))
                print('    Top: ', str(face_info.face_rectangle.top))
                print('    Width: ', str(face_info.face_rectangle.width))
                print('    Height: ', str(face_info.face_rectangle.height))
        return True


def find_face(find_img_path, detected_img_path=None, detected_img=None):
    if find_img_path:
        image_face_id = single_face_detect(find_img_path)
        if image_face_id is None:
            return False
        detected_faces, multi_image_name = multi_face_detect(detected_img_path, detected_img)
        if detected_faces is None or multi_image_name is None:
            return False
        result = find_similar_face(image_face_id, detected_faces, multi_image_name)
        return result
    else:
        return False
