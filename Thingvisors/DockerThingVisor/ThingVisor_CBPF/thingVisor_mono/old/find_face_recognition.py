'''
顔認証メイン処理
author：
datetime：2021.2.20
'''
# !/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from open_the_camera import open_camera as op_cam
from face_detction import face_detection_api as face_rec
import cv2
import config
import datetime
from sub_main_multithreading import run_face_find_pana, close_thread
from time import sleep


def run_ffr(r, sub_s, key):
    print("Start find_face_recognition.")
    # reciver, sender = mp.Pipe(duplex=False)
    
    pana_cam = True
    # pana_cam = False

    if pana_cam:
        web_cam = op_cam.PanaCamera()
        result, capture = web_cam.open_camera()
    else:
        web_cam = op_cam.WebCamera()
        result, capture = web_cam.open_camera()
    print("web cam result: ", result)

    if not result:
        msg = 'failed'
        sub_s.send([msg])
        return
    else:
        msg = 'success'
        sub_s.send([msg])
    
    sleep(1)

    # Run Azure Recognition thread and run MQTT context broker thread
    # t_azure, t_mqtt = run_face_find_pana()
    t_azure = run_face_find_pana()
    
    active_flg = True
    while True:
        if r.poll():
            msg = r.recv()
            print("main send close msg {}".format(msg))
            if msg[0] == 'close':
                active_flg = False

        if not active_flg:
            # rest api から　終了フラグを受けたらループを抜ける
            break

        ret, img = capture.read()
        if ret:
            img, len_face_rec = face_rec.facial_detection(img)

            if len_face_rec > 0 and t_azure.implement_flg is False:
                print('顔認識開始')
                # カメラからキャプチャを取ったイメージをキャッシュに保存
                cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                img_name = 'img' + cur_time + '.jpg'
                img_path = config.cache_dir + img_name
                cv2.imwrite(img_path, img, [cv2.IMWRITE_JPEG_QUALITY, 75])
                t_azure.implement_flg = True
                t_azure.cache_img_path = img_path

                print('t_azure.get_value()', t_azure.get_value())
                if t_azure.get_value():
                    # クライアントからパブリッシュしない、サーバーのメッセージを受けたらJSONファイルをサーバーにアップする
                    t_mqtt.publish_order = True
                    # t_mqtt.on_message_flg = True
                    t_mqtt.image_name = img_name

        #cv2.imshow('capture', img)

        #key = cv2.waitKey(30) & 0xff
        #if key == 27:
        #    break

    close_thread(t_azure, t_mqtt)
    #cv2.destroyAllWindows()


if __name__ == '__main__':
    args = sys.argv
    r = args[0]
    sub_s = args[1]
    key = args[2]
    run_ffr(r, sub_s, key)
