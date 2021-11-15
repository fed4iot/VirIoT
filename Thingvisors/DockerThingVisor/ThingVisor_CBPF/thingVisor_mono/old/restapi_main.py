'''
RestAPIサービス
author：
datetime：2021.2.20
'''

# !/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shlex
import shutil
# import subprocess
from multiprocessing import Process, Pipe
import glob
from time import sleep

import find_face_recognition, config
import werkzeug
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

api = Flask(__name__)

TOKEN = 'YOUR_TOKEN'

# limit upload file size : 1MB
MAX_JSON_CONTENT_LENGTH = config.MAX_JSON_CONTENT_LENGTH

# upload dir path
UPLOAD_DIR = config.find_img_dir
REMOVE_DIR = config.temp_image_dir
pid = None
receiver, sender = Pipe(duplex=False)
sub_r, sub_s = Pipe(duplex=False)
face_rec_start_flg = False


@api.route('/api/face_rec=<string:active_flg>', methods=['GET'])
def run_recognition(active_flg):
    global pid, receiver, sender, face_rec_start_flg

    if active_flg == '':
        return jsonify({"api result": "active_flg is Nothing"})

    if active_flg == 'start':

        if face_rec_start_flg:
            return jsonify({"api result": "Face recognition is started."})

        key = "pipe10"

        os.chdir(config.root_path)
        face_rec_path = './FaceDetectionAndRecognition/face_rec.sh'
        face_rec_path_py = './FaceDetectionAndRecognition/find_face_recognition.py'
        sh_command = 'sh ' + face_rec_path
        sh_cmd_py = 'python3 ' + face_rec_path_py
        tokens = shlex.split(sh_cmd_py)
        # pid = subprocess.run(tokens, args=(receiver, key))
        # pid = subprocess.Popen(tokens, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pid = Process(target=find_face_recognition.run_ffr, name='run_ffr', args=(receiver, sub_s, key))
        pid.start()
        # pid.join()

        while True:
            if sub_r.poll():
                msg = sub_r.recv()
                print("receive message: ", msg)
                if msg[0] == 'failed':
                    return jsonify({"api result": "ERR: Camera is not connected!"})
                elif msg[0] == 'success':
                    face_rec_start_flg = True
                    return jsonify({"api result": "Face recognition is start!"})
                else:
                    return jsonify({"api result": "Unknown status!"})

    elif active_flg == 'close':
        print('elif active_flg == close')

        if pid is None:
            return jsonify({"api result": "Face recognition is not started!"})
        else:
            msg = 'close'
            sender.send([msg])

            # try:
            #     os.kill(int(pid), signal.SIGKILL) # kill(pid, sig)
            #
            # except OSError as e:
            #     #「No such process」じゃない場合
            #     if e.errno != errno.ESRCH:
            #
            #         return jsonify({"api result": "Exception Error"})
            face_rec_start_flg = False
            return jsonify({"api result": "Face recognition is close!"})

    else:
        return jsonify({"api result": "Unknown flags!"})


# アップロードするファイルの拡張子
ALLOW_EXTENSIONS = ['jpg', 'jpeg', 'png']


def allowed_file(file_name):
    return '.' in file_name and file_name.rsplit('.', 1)[-1] in ALLOW_EXTENSIONS


@api.route('/api/upload', methods=['POST', 'GET'])
def uploads():
    if request.method == 'POST':
        # get POST
        file = request.files['file']

        if file and allowed_file(file.filename):

            # secure_filename
            file_name = secure_filename(file.filename)
            # save image file
            file.save(os.path.join(UPLOAD_DIR, file_name))
            return jsonify({"api result": "File upload success!"})
        else:
            return jsonify({"api result": "File format is not 'jpg', 'jpeg', 'png'"})
    return render_template('index.html')


@api.route('/api/remove_img=<string:img_name>', methods=['GET'])
def remove_img(img_name):
    if img_name is None:
        return jsonify({"api result": "please input img_name to image name! if remove_img=all then remove all images!"})

    if img_name:

        if img_name == 'all':
            file_list = glob.glob(os.path.join(REMOVE_DIR, '*.*'))
            print(file_list)

            for file in file_list:
                os.remove(file)

            return jsonify({"api result": "All image files is removed!"})

        else:
            file_list = glob.glob(os.path.join(REMOVE_DIR, img_name))
            for file in file_list:
                os.remove(file)

            return jsonify({"api result": img_name + " files is removed!"})


@api.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_over_max_file_size(error):
    print('werkzeug.exceptions.RequestEntityTooLarge')
    return 'result : file size is overed.'


if __name__ == '__main__':
    api.run(host='0.0.0.0', port=5000, debug=False)
