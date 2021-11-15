"""
MQTT Client
author：
datetime：2021.2.20
"""
# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import config
from subprocess import run
from time import sleep
import shutil


try:
    # import paho.mqtt.client as mqtt
    import paho.mqtt.client as _mqtt
except ImportError:
    print("MQTT client not find. Please install as follow!")
    print("git clone http://git.eclipse.org/gitroot/paho/org.eclipse.paho.mqtt.python.git")
    print("cd org.eclipse.paho.mqtt.python")
    print("sudo python setup.py install")

client = _mqtt.Client()

# User name
user_name = 'root'
# Password
password = 'password'

connected = False
message_received = False
on_message_signal = False
JSON_FILE_PATH = config.json_file_dir + config.json_name
SEND_JSON_FILE = config.json_file_dir + config.send_json_file


# ブローカーに接続できたときの処理
def on_connect(client, userdata, flags, respons_code):
    global connected
    if respons_code == 0:
        print('client is connected.')

        connected = True
    else:
        print('client is not connected.')
    client.subscribe(config.Srctopic)


# ブローカーが切断したときの処理
def on_disconnect(client, userdata, flags, respons_code):
    if respons_code != 0:
        print('Unexpected disconnection.')


# publishが完了したときの処理
def on_publish(client, userdata, mid):
    print('OnPublish, mid: ', str(mid))


def on_subscribe(client, userdata, mid, granted_qos):
    print('Subscribed: ', str(mid), ' ', str(granted_qos))


def on_log(client, userdata, level, string):
    print('Log: ', string)


# メッセージが届いたときの処理
def on_message(client, userdata, msg):
    global on_message_signal

    print(msg.topic, str(msg.payload, encoding='utf-8'))

    if str(msg.payload, encoding='utf-8'):
        data = msg.payload
        d_data = data.decode("utf-8")
        img_path = config.img_file_dir + d_data
        print('Delete image : %s', str(msg.payload, encoding='utf-8'))
        # os.remove(img_path)

    result = 0
    if str(msg.payload, encoding='utf-8') == config.FACE_PANA:

        print("Do Facial regognition")

        on_message_signal = True

        # result = facial_recognition()

        # print(msg.topic + " " + str(result) + " " + str(msg.payload))

        if result > 0:
            for count in range(result):
                # run(command, shell=True)
                dummy = run(config.Command + config.Host + config.Topicopt + config.T_Face + config.pana_cam_no +
                            config.Timestamp + config.Facerec + str(count) + config.Fileopt + config.img_file_dir +
                            config.Timestamp + config.Facerec + str(count) + config.Fileext, shell=True)

                print(config.Command + config.Host + config.Topicopt + config.T_Face + config.pana_cam_no +
                      config.Timestamp + config.Facerec + str(count) + config.Fileopt + config.img_file_dir +
                      config.Timestamp + config.Facerec + str(count) + config.Fileext)
        else:
            # client.publish(dsttopic, str(now))

            dummy = run(config.Command + config.Host + config.Topicopt + config.T_Face + config.pana_cam_no +
                        config.Dummyfile + config.Fileopt + config.Dummyfile, shell=True)
            # print(config.Command + config.Host + config.Topicopt + config.T_Face + config.pana_cam_no +
            #       config.Dummyfile + config.Fileopt + config.Dummyfile)

    elif str(msg.payload, encoding='utf-8') == config.MOVE_PANA:

        print("Do Moving Objects")

        # result = moving_object_detection()

        print(msg.topic + " " + str(result) + " " + str(msg.payload, encoding='utf-8'))

        if result > 0:

            # dummy = os.system(Command + Host + Topicopt + T_Move + Timestamp + Filename_Moving + Fileopt + FileDir + Timestamp + Filename_Moving + Fileext)
            dummy = run(config.Command + config.Host + config.Topicopt + config.T_Move + config.pana_cam_no +
                        config.Timestamp + config.Filename_Moving + config.Fileopt + config.img_file_dir + config.Timestamp +
                        config.Filename_Moving + config.Fileext, shell=True)
            print(config.Command + config.Host + config.Topicopt + config.T_Move + config.pana_cam_no +
                  config.Timestamp + config.Filename_Moving + config.Fileopt + config.img_file_dir + config.Timestamp +
                  config.Filename_Moving + config.Fileext)

        else:

            # dummy = os.system(Command + Host + Topicopt + T_Move + Dummyfile + Fileopt + Dummyfile)
            dummy = run(
                config.Command + config.Host + config.Topicopt + config.T_Move + config.pana_cam_no + config.Dummyfile +
                config.Fileopt + config.Dummyfile, shell=True)
            print(
                config.Command + config.Host + config.Topicopt + config.T_Move + config.pana_cam_no + config.Dummyfile +
                config.Fileopt + config.Dummyfile)

        # dummy = os.system(Command + Host + Topicopt + T_Move + Timestamp + Filename_Image + Fileopt + FileDir + Timestamp + Filename_Image + Fileext)
        dummy = run(
            config.Command + config.Host + config.Topicopt + config.T_Move + config.pana_cam_no + config.Timestamp +
            config.Filename_Image + config.Fileopt + config.img_file_dir + config.Timestamp + config.Filename_Image +
            config.Fileext, shell=True)
        print(
            config.Command + config.Host + config.Topicopt + config.T_Move + config.pana_cam_no + config.Timestamp +
            config.Filename_Image + config.Fileopt + config.img_file_dir + config.Timestamp + config.Filename_Image +
            config.Fileext)
        print("end.")

    else:

        print("Do nothing")

        # image_capture_moving();

        # dummy = os.system(Command + Host + Topicopt + T_Move_Jetson_1 + Timestamp + "_1st" + Fileopt + FileDir + Timestamp + "_1st" + Fileext)
        # print(Command + Host + Topicopt + T_Move_Jetson_1 + Timestamp + "_1st" + Fileopt + FileDir + Timestamp + "_1st" + Fileext)

        # dummy = os.system(Command + Host + Topicopt + T_Move_Jetson_1 + Timestamp + "_2nd" + Fileopt + FileDir + Timestamp + "_2nd" + Fileext)
        # print(Command + Host + Topicopt + T_Move_Jetson_1 + Timestamp + "_2nd" + Fileopt + FileDir + Timestamp + "_2nd" + Fileext)


def on_exec(strcmd):
    print('Exec: ', strcmd)


def get_message_signal():
    global on_message_signal

    return on_message_signal


def set_message_signal(bool_value):
    global on_message_signal

    on_message_signal = bool_value


def send_json_file():
    shutil.copy(JSON_FILE_PATH, SEND_JSON_FILE, follow_symlinks=True)

    run(config.Command + config.Host + config.Topicopt + config.Pana_topic + config.Fileopt + SEND_JSON_FILE, shell=True)

    print(config.Command + config.Host + config.Topicopt + config.Pana_topic + config.Fileopt + SEND_JSON_FILE)


def start_mqtt_broker():
    '''
    サブスレッドで起動させるため
    sub_main_multithreading.py に組込み

    '''
    # client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_log = on_log

    # IDとPWの設定（必要の場合）
    # client.username_pw_set(username, password=password)

    client.connect(config.Host, config.Port, 60)
    client.subscribe(config.topic, 0)

    client.loop_start()

    while not connected:
        print('client is not connected.')
        sleep(0.2)

    while connected:
        # ここにpublishロジックを追加
        # ただ、スレッド間変数設定のため、sub_main_multithreading.pyにロジックを組込んだ
        sleep(3)
