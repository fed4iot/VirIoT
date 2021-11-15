'''
Azure顔認証、MQTTサービスサブスレッド
author：
datetime：2021.2.20
'''
# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import logging
import threading
import glob
from time import sleep
from face_recognition_azure import face_recognition_for_azure as face_rec
from context_broker import mqtt_client, create_json

import config

logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')


class AzureRecognitionThread(threading.Thread):

    def __init__(self, implement_flg, cache_img_path):
        threading.Thread.__init__(self)
        self.implement_flg = implement_flg
        self.cache_img_path = cache_img_path
        self.return_value = False
        # The other variables are defined here

    def run(self):

        logging.debug('azure face recognition thread start!')

        while True:

            if self.implement_flg:
                logging.info('cache_img_path:{} '.format(self.cache_img_path))
                # print('implement_flg :', self.implement_flg)
                files = glob.glob(config.find_img_dir + '*')
                if not files:
                    logging.debug('Directory image/fine_image not file!')
                    self.implement_flg = False
                    # キャッシュのイメージフィアルを削除
                    img_name = os.path.basename(self.cache_img_path)
                    logging.info('Delete cache image : %s', img_name)
                    os.remove(self.cache_img_path)
                    continue

                find_flg = False
                for file in files:
                    logging.info('file: %s', file)
                    result = face_rec.find_face(file, self.cache_img_path)
                    if not result:
                        pass

                    else:
                        find_flg = True
                # 探したい顔を見つけた場合、画像をtemp_imageに移動する
                if find_flg:

                    ### added by Kenji
                    img_name = os.path.basename(self.cache_img_path)
                    create_json.save_json_file(img_name)

                    # キャッシュのイメージファイルをimage/temp_imageに移動
                    shutil.move(self.cache_img_path, config.temp_image_dir)

                # 探したい顔を見つけなかった場合、キャッシュの画像を削除する
                else:
                    # キャッシュのイメージフィアルを削除
                    img_name = os.path.basename(self.cache_img_path)
                    logging.info('Delete cache image : %s', img_name)
                    os.remove(self.cache_img_path)

                sleep(10)
                self.return_value = True
                self.implement_flg = False

        logging.debug('azure face recognition thread end!')

    def get_value(self):
        return self.return_value

    def set_value(self, implement_flg, cache_img_path):
        self.implement_flg = implement_flg
        self.cache_img_path = cache_img_path


class MqttConnectThread(threading.Thread):

    def __init__(self, publish_order, on_message_flg, image_name):
        threading.Thread.__init__(self)
        self.publish_order = publish_order
        self.on_message_flg = on_message_flg
        self.image_name = image_name

    def run(self):

        logging.debug('mqtt context broker thread start!')

        # ここにコンテクストブローカーをスタートする
        # mqtt_client.start_mqtt_broker(self.publish_order, self.image_name)

        # mqtt_client.client = mqtt_client.mqtt.Client()
        mqtt_client.client.on_connect = mqtt_client.on_connect
        mqtt_client.client.on_disconnect = mqtt_client.on_disconnect
        mqtt_client.client.on_publish = mqtt_client.on_publish
        mqtt_client.client.on_message = mqtt_client.on_message
        mqtt_client.client.on_subscribe = mqtt_client.on_subscribe
        mqtt_client.client.on_log = mqtt_client.on_log

        # IDとPWの設定（必要の場合）
        # client.username_pw_set(username, password=password)

        mqtt_client.client.connect(config.Host, config.Port, 60)
        mqtt_client.client.subscribe(config.topic, 0)

        mqtt_client.client.loop_start()

        while not mqtt_client.connected:
            print('client is not connected.')
            sleep(0.2)

        while mqtt_client.connected:

            # print('glb_publish_flg: ', glb_publish_flg)
            # publish_order, image_name = self.get_value()
            print("mqtt connected. publish order is ", self.publish_order)
            # if glb_publish_flg:
            if self.publish_order:
                # json_data = create_json.get_json_data(self.image_name)
                create_json.save_json_file(self.image_name)
                # print(json_data)
                # mqtt_client.client.publish(config.topic, json_data)

                self.publish_order = False
                self.image_name = ''
                # glb_publish_flg = False

            message_signal = mqtt_client.get_message_signal()
            print("message_signal ", message_signal)
            if message_signal:
                print("send json file")
                # json_file = create_json.get_json_file()
                mqtt_client.send_json_file()

                mqtt_client.set_message_signal(False)
            sleep(3)

        logging.debug('mqtt context broker thread end!')

    def set_value(self, publish_order, image_name):
        self.publish_order = publish_order
        self.image_name = image_name

    def get_value(self):
        return self.publish_order, self.image_name


def run_face_find_pana():
    # Run Azure thread
    t_azure = AzureRecognitionThread(implement_flg=False, cache_img_path='')
    t_azure.setDaemon(True)
    t_azure.start()

    t_mqtt = ""
    ### commented out by Kenji
    # Run Mqtt thread
    #t_mqtt = MqttConnectThread(publish_order=False, on_message_flg=False, image_name='')
    #t_mqtt.setDaemon(True)
    #t_mqtt.start()

    print('run face find pana returned')

    return t_azure, t_mqtt


def close_thread(t_azure, t_mqtt):
    pass
