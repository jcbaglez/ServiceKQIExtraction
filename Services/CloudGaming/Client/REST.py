from flask import Flask, json, request
from flask_restful import Api, Resource, reqparse
import time

import keyboard
import mouse
import time
import os
import json
from utils.utils import *
from pynput.mouse import Button, Controller

import subprocess
import multiprocessing
import threading

from videoCapturing.imageCapture import *


if __name__=='__main__':
    app = Flask(__name__)
    api = Api(app)



    def moveTimestamps(nMovements):
        print("recording")
        return getFromConsole("python recordTimeMove.py "+str(nMovements))

    class action(Resource):
        def post(self,name):
            print(name)
            if (name == "keyboard"):
                jD = True
                try:
                    json_data = request.get_json(force=True)
                    print(json_data)
                except:
                    print("No JSON data")
                    json_data = dict()
                    jD = False

                for a in json_data[0]['action']:
                    keyboard.send(a)
                    time.sleep(1)
                #keyboard.send(json_data[0]['action'])
            elif (name == "configureClient"):
                try:
                    json_data = request.get_json(force=True)
                except:
                    json_data = {'type','trainingTool'}

                if (not isProcessRunning("LeagueClient")):
                    os.startfile("C:/Riot Games/League of Legends/LeagueClient.exe")
                    time.sleep(15)

                if (not isProcessRunning('League of Legends')):
                    c = getFromConsole("python cloudGaming/Moonlight/serverConfigureGame.py " + json_data['type'])
                
                return 200

    class info(Resource):
        def get(self):
            return 200

        def post(self):
            jD = True
            try:
                json_data = request.get_json(force=True)
                print(json_data)
            except:
                print("No JSON data")
                json_data = dict()
                jD = False
                return 500   

            try:
                pr = json_data['process']
                
                data = dict()
                for p in pr:
                    r = getProcess(p).to_dict('records')
                    data[p] = r
                return data,200
            except:
                return 500

    class frame(Resource):

        def hostMeasurement(self,data,filename):
            mouseClicks = []
            for x in data:
                #Get time between actions
                if ("dMove" in x):
                    dMove = x['dMove']
                else: # If this time is not given in the data, it is taken 1 sec
                    dMove = 1
                print("deltaMove:",dMove)
                #Get repetitions
                if ("repetitions" in x):
                    rep = x['repetitions']
                else: # If is not set, it is set to 1
                    rep = 1

                for m in range(0,rep):
                    for action in x['actions']:
                        print(action)
                        mouse.move(action['x'],action['y'],absolute=True)

                        mouse.right_click()
                        mouseClicks.append(time.time())
                        print("Mouse move")
                        time.sleep(dMove)

            print("Mouse clicks:", mouseClicks)
            np.save(filename +'_mouse',np.asarray(mouseClicks))



        def post(self,name):

            if (name == "host"):
                jD = True
                try:
                    json_data = request.get_json(force=True)
                    print(json_data)
                except:
                    print("No JSON data")
                    json_data = dict()
                    jD = False
                filename=str(int(time.time()))
                print(filename)
                t = threading.Thread(target=self.hostMeasurement, args=(json_data,filename,))
                record = threading.Thread(target=gettingFramesThread,args=(t,filename,))
                t.start()
                record.start()


                record.join()

                # Load data
                # times = np.load(filename+"_mouse.npy")
                # img = np.load(filename+"_images.npy")
                # imgt = np.load(filename+"_timestamp.npy")
                # latency = getResponsivity(times,img,imgt)
                latency = np.load(filename+"_results.npy")
                res = dict()
                res['latency'] = latency.tolist()
                return json.loads(json.dumps(res))

            elif(name == "client"):
                parser = reqparse.RequestParser()
                parser.add_argument("t")
                args = parser.parse_args()

                f = gettingFramesFunction(int(args.t))

                # Load data
                #img = np.load('data2.npy')
                #imgt = np.load('time2.npy')
                img = np.asarray(f[0])
                imgt = np.asarray(f[1])
                iRes = imgChange(img,imgt)
                iC = np.asarray(iRes[0]) # Relevant Information
                iCh = np.asarray(iRes[1]) # Number of pixel
                imgGroup = np.asarray(deltaFrame(iC))
                res = []
                names = ['FirstFrame','LastFrame','InitTime','EndTime','Duration']
                for i in imgGroup:
                    res.append(dict(zip(names,i)))
                results = json.dumps(res)
                return json.loads(results)
            elif(name == "info"):
                d = dict()
                d['monitor'] = monitorInfo()
                return d

    class latency(Resource):
        def moveTimestamps(self,nMovements):
            print("recording")
            return getFromConsole("python recordTimeMove.py "+str(nMovements))
        def get(self,name):
            print("hoal")
            return 200
        def post(self,name):
            q = multiprocessing.Queue()
            print("asdf")
            d = multiprocessing.Process(target=self.moveTimestamps,args=(2,q))
            d.start()

            #print(moveTimestamps(2))
            print("Processed")
            return 200


    class crowdcell(Resource):
        def post(self,name):
            parser = reqparse.RequestParser()
            if(name == "configuration"):

                parser.add_argument("parameter")
                parser.add_argument("value")

                args = parser.parse_args()
                print(args)
                c.setParameter(args.parameter, args.value)

                r = c.getParameter(args.parameter)
                print(r)
                return r
            elif(name == "action"):
                parser.add_argument("t")
                args = parser.parse_args()

                if (args.t == "reboot"):
                    print("Rebooting crowdcell...")
                    c.restart()
                    print("end")
                    return 200



    class apS (Resource):
        def post(self, module,msg):
            jD = True
            try:
                json_data = request.get_json(force=True)
                prin(json_data)
            except:
                print("No JSON data")
                json_data = dict()
                jD = False
            print(msg)

            if (module == "mme"):
                server = "127.0.0.1:9000"
            elif (module == "enb"):
                server = "127.0.0.1:9001"

            #at = "\'{\"message\": \"config_get\"}\'"
            json_data['message'] = msg
            at = json.dumps(json_data)

            print(at)
            com = "./ws.js " + server + " " + "\'" + at + "\'"
            print(com)
            res = subprocess.Popen(com, shell = True, stdout = subprocess.PIPE).stdout
            rest = res.read()
            rest = rest.decode()
            msg = rest[rest.find("{"):]
            print (msg)
            js = json.loads(msg)

            return js
    api.add_resource(frame, "/frame/<string:name>")
    api.add_resource(action, "/action/<string:name>")
    api.add_resource(info,'/info')
    app.run(host='192.168.0.57', port = 5000)
    #app.run(host="192.168.0.102", port = 5000)
