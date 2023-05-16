from flask import Flask, json, request
from flask_restful import Api, Resource, reqparse
import time

import keyboard
import mouse
import time
import os
import json
from utils import *
from pynput.mouse import Button, Controller

import subprocess
import multiprocessing
import threading
import platform


def getFromConsole(cmd):
    plat = platform.system()

    if (plat == "Linux"):
        args = [cmd, "/etc/services"]
    elif (plat == "Windows"):
        args = ["powershell.exe", cmd]

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    # print(out)
    return out


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)


    def getFromConsole(cmd):
        plat = platform.system()

        if (plat == "Linux"):
            args = [cmd, "/etc/services"]
        elif (plat == "Windows"):
            args = ["powershell.exe", cmd]

        proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        print(out)
        return out


    class testbed(Resource):
        def post(self):
            try:
                jd = request.get_json(force=True)
                print(jd)

            except:
                return 500


            if (jd['network'] not in ["Ethernet", "WiFi", "CrowdCell", "CPE"]):
                return "Network parameter is not valid",300
            elif (jd['resolution'] not in ["720p", "1080p", "1440p", "4K"]):
                return "Resolution is not valid", 300
            elif (jd['framerate'] not in ["30", "60", "120","all"]):
                return "Frame rate is not valid", 300

            cmd = "python cloudGamingTestbed.py -r " + jd['resolution'] + " -f " + jd['framerate'] + " -n " + jd['network']
            q = multiprocessing.Queue()
            if("directory" in jd):
                cmd += " -d " + jd["directory"]
            else:
                jd['directory'] = "/results/"

            print(cmd)
            cgScript = multiprocessing.Process(target = getFromConsole, args=(cmd,))
            cgScript.start()
            #getFromConsole(cmd)
            return "Results will be saved in " + jd["directory"], 200




    api.add_resource(testbed, "/testbed/")

    app.run(host='0.0.0.0', port=6000)
    # app.run(host="192.168.0.100", port = 5000)
