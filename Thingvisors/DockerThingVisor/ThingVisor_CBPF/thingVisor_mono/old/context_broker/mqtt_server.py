'''
MQTT Subscribe
Topic 受け取る場合に使用
author：
datetime：2021.2.20
'''
#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import datetime
import socket
import paho.mqtt.publish as publish
import json

import paho.mqtt.client as mqtt  # MQTTのライブラリをインポート


# ブローカーに接続できたときの処理
def on_connect(client, userdata, flag, rc):
    print("Connected with result code " + str(rc))  # 接続できた旨表示
    client.subscribe("topic")  # subするトピックを設定


# ブローカーが切断したときの処理
def on_disconnect(client, userdata, flag, rc):
    if rc != 0:
        print("Unexpected disconnection.")


# publishが完了したときの処理
def on_publish(client, userdata, mid):
    print('OnPublish, mid: ', str(mid))


def on_subscribe(client, userdata, mid, granted_qos):
    print('Subscribed: ', str(mid), ' ', str(granted_qos))


# メッセージが届いたときの処理
def on_message(client, userdata, msg):
    # msg.topicにトピック名が，msg.payloadに届いたデータ本体が入っている
    print("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))

    try:
        data = msg.payload
        d_data = data.decode("utf-8")
        print(d_data)
        json_dict = json.loads(d_data)
    except Exception as e:
        print(e)

    img_name = json_dict['img_name']
    # img_name = os.path.basename(img_path)
    # client.publish("Pana/+", img_name)


# MQTTの接続設定
client = mqtt.Client()  # クラスのインスタンス(実体)の作成
client.on_connect = on_connect  # 接続時のコールバック関数を登録
client.on_disconnect = on_disconnect  # 切断時のコールバックを登録
client.on_message = on_message  # メッセージ到着時のコールバック
client.on_publish = on_publish
client.on_subscribe = on_subscribe

client.connect("localhost", 1883, 60)  # 接続先は自分自身

client.loop_forever()  # 永久ループして待ち続ける

