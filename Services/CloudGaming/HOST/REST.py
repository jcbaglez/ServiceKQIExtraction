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

from imageCapture import *
from calibration import *

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
            elif (name == "mouse"):
                try:
                    json_data = request.get_json(force=True)
                    print(json_data)
                    for a in json_data:
                        try:
                            mouse.move(a['pos']['x'], a['pos']['y'],absolute = True)
                        except:
                            print("Msg doesn't match with the pattern")
                            return {'Error info': "Msg doesn't contain position field"}, 300
                        
                        time.sleep(0.5)
                        try:
                            if (a['action'] == "click"):
                                mouse.click()
                            elif (a['action'] == "rightClick"):
                                mouse.right_click()
                            elif (a['action'] == "dobleClick"):
                                mouse.double_click()
                        except:
                            print("Msg doesn't containt action field")
                            return {"Error info": "Msg doesn't containt action field"}, 300
                        
                        pos = a
                except: 
                    print("No JSON data")
                    json_data = dict()
                    jD = False
                    return 300


            elif (name == "launchGameClient"):
                if (not isProcessRunning("LeagueClient")):
                #if True:
                    os.startfile("C:/Riot Games/League of Legends/LeagueClient.exe")
                    time.sleep(1)

                return 200
            elif (name == "configureClient"):
                try:
                    json_data = request.get_json(force=True)
                    print(json_data)
                except:

                    json_data = {'type':'trainingTool'}

                if (not isProcessRunning("LeagueClient")):
                    os.startfile("C:/Riot Games/League of Legends/LeagueClient.exe")
                    time.sleep(15)

                if (not isProcessRunning('League of Legends')):
                    c = getFromConsole("python serverConfigureGame.py " + json_data['type'])

                return 200
            elif (name == "endProcess"):
                try:
                    json_data = request.get_json(force=True)
                    print(json_data)
                    killProcess(json_data['process'])
                    return 200
                except:
                    return 500
            elif (name == "endLoL"):
                c = getFromConsole("python closeLolGame.py")

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

        def hostClicks(self,data,filename,queue = None):
            time.sleep(2)
            mouse.move(935, 490, absolute=True)
            time.sleep(0.5)
            mouse.click()
            time.sleep(1)
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

            try:
                print("Mouse clicks:", mouseClicks)
                np.save(filename +'_mouse',np.asarray(mouseClicks))
            except:
                print("Error saving mouse clicks")
            
            finally:
                if (queue != None):
                    queue.put(np.asarray(mouseClicks))
                return np.asarray(mouseClicks)

        
        def latencyFormatting(self,prefix, data):
            prefix = prefix + "_"
            hLatency = getSummaryLatency(data)
            latencyResults = dict()
            # Change of values to ms
            latencyResults[prefix + 'latencyAvg'] = hLatency['avg'] * 1000
            latencyResults[prefix + 'latencyMax'] = hLatency['max'] * 1000
            latencyResults[prefix + 'latencyMin'] = hLatency['min'] * 1000
            latencyResults[prefix + 'latency25Percent'] = hLatency['percent25']*1000
            latencyResults[prefix + 'latency50Percent'] = hLatency['percent50']*1000
            latencyResults[prefix + 'latency75Percent'] = hLatency['percent75']*1000
            latencyResults[prefix + 'latency'] = (data*1000).tolist()
            return latencyResults

        def hostMeasurement(self,nClicks):
            c = calibration()
            #clicks = c.clickDetection(nClicks)
            q = multiprocessing.Queue()
            qC = multiprocessing.Queue()
            filename = "hostMeas"
            cT = threading.Thread(target=c.clickDetection, args=  (nClicks, qC))
            record = threading.Thread(target=gettingFramesThread2,args=(cT,filename,))
            ping = threading.Thread(target = pingTest, args = ("185.40.67.150","PING_HOST_TO_RIOT",80,10,q,))
            #ping = threading.Thread(target = pingTest("185.40.67.150","PING_HOST_TO_RIOT",80,10,q,))
            cT.start()
            ping.start()
            record.start()

            cT.join()
            record.join()
            

            img = np.load(filename+"_images.npy")
            imgt = np.load(filename + "_timestamp.npy")

            mouse = qC.get()
            # print("Mouse:")
            # print(mouse)
            print("Calculating host responsivity")
           
            
            #ping.start()
            (cLD, efps,monitorFPS) = getResponsivity4(mouse,img, imgt)


            try:
                os.remove(filename+"_images.npy")
                os.remove(filename+"_timestamp.npy")

            except:
                print("files can't be deleted")
            
            res = dict()
            res = self.latencyFormatting("host",cLD)
            #res['latency2'] = latency2.tolist()
            res['host_efps'] = efps
            res['host_monitorFPS'] = monitorFPS
            

            res['host_clickTime'] = mouse
            ping.join()
            pingV = q.get()
            res.update(pingV)
            return json.dumps(res)
            


        def checkMove(self,time):
            f = gettingFrames(int(time), "moveDetection")
            try:
                os.remove("moveDetection_images.npy")
                os.remove("moveDetection_timestamp.npy")
            except:
                print("Files could not be deleted")

            img = np.asarray(f[0])
            imgt = np.asarray(f[1])
            iRes = imgChange2(img,imgt)
            d = dict()
            if (len(iRes[0]) == 1 and iRes[0][0][0] == -1):
                print("Error in client, actions has not been executed")
                d['move'] = 0
            else:
                print("Actions has been executed")
                d['move'] = 1
            return d

        def get(self,name):
            if (name == "checkMovement"):
                parser = reqparse.RequestParser()
                parser.add_argument("t")
                args = parser.parse_args()
                resp = self.checkMove(int(args.t))
                print(resp)
                return resp
            elif (name == "hostMeasurement"):
                parser = reqparse.RequestParser()
                parser.add_argument("nActions")
                args = parser.parse_args()
                resp = self.hostMeasurement(int(args.nActions))
                return resp
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
                q = multiprocessing.Queue()
                q2 = multiprocessing.Queue()
                t = threading.Thread(target=self.hostClicks, args=(json_data,filename,q2,))
                record = threading.Thread(target=gettingFramesThread,args=(t,filename,))
                #ping = threading.Thread(target = pingTest, args=("185.40.67.150","PING_RIOT_SIRIO",80,10,q,))
                #ping.start()
                t.start()
                record.start()

                record.join()
                
                t.join()
                #pingV = q.get()
                # Load data
                # times = np.load(filename+"_mouse.npy")
                # img = np.load(filename+"_images.npy")
                # imgt = np.load(filename+"_timestamp.npy")
                # latency = getResponsivity(times,img,imgt)
                latency = np.load(filename+"_results.npy")
                #latency2 = np.load(filename + "_results2.npy")
                try:
                    os.remove(filename+"_images.npy")
                    os.remove(filename+"_timestamp.npy")
                    os.remove(filename+"_results.npy")
                    os.remove(filename+"_mouse.npy")
                    
                finally:
                    res = dict()
                    res['latency'] = latency.tolist()
                    #res['latency2'] = latency2.tolist()
                    #ping.join()
                    #pingV = q.get()
                    #res['ping'] = pingV
                    return json.loads(json.dumps(res))

            elif(name == "client"):
                parser = reqparse.RequestParser()
                parser.add_argument("t")
                args = parser.parse_args()

                print(args.t)
                   
            elif(name == "info"):
                d = dict()
                d['monitor'] = list(monitorInfo())
                print(d['monitor'])
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
                print(json_data)
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
    #app.run(host='192.168.0.57', port = 5000)
    #app.run(host="192.168.0.101", port = 5000)
    #app.run(host="192.168.192.201", port = 5000)
    #app.run(host="192.168.8.105", port = 5000)
    app.run(host="0.0.0.0", port = 5000)