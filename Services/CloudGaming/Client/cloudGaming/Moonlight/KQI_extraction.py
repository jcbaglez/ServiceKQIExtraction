
import requests
import json
import keyboard
import mouse
import time
import multiprocessing
from cloudGaming.Moonlight.moonlight import *
from cloudGaming.Moonlight.LOL import *
import numpy as np
import mss
import traceback
import cv2
from cloudGaming.Moonlight.metricas_fich import *
import platform
import os
class CG_KQI_extraction():

    def __init__(self, moonlight, remoteLol):


        self.moonlight = moonlight # Object type moonlight
        self.rmLol = remoteLol # Object type remote lol


        # TODO: Raise exception if moonlight conf has not done previously
        self.resolution = remoteLol.resolution
        self.fps = remoteLol.framerate

        self.ip = remoteLol.ip
        self.port = remoteLol.port


    def __monitorInfo(self):
        return np.asarray(mss.mss().monitors)


    def prepareExperiment(self, pos):

        name = str(int(time.time()))
        # Get monitor information from the server
        monitor = self.__monitorInfo()[1]
        # Prepare user actions
        d = dict()
        d['repetitions'] = pos['repetitions']
        d['dMove'] = pos['dMove']
        dx = int(monitor['width'] * pos['coordinates']['x'] + monitor['left'])
        dy = int(monitor['height'] * pos['coordinates']['y'] + monitor['top'])
        d['actions'] = [{'x': dx, 'y': dy}]
        data2send = [d]

        # Start Moonlight
        #moonlight = Moonlight()
        self.moonlight.start_moonlight()
        time.sleep(10)

        #rmLol = remoteLOL(ip=self.ip, port=self.port)
        self.rmLol.sendMouseAction(dx, dy, "click")

        # Show stats in Moonlight
        self.moonlight.show_stats()

        # Click on the screen to ensure that actions will take place
        mouse.move(dx, dy, absolute=True)
        mouse.click()

        # Estimation of the time which will be passed while actions are being doing
        t = pos['dMove'] * d['repetitions'] + 5

        return (name, data2send, t)


    def experiment(self, pos, serverTest = True, pings = []):
        # TODO: Ping format

        movCheck_q = multiprocessing.Queue()
        mouse_q = multiprocessing.Queue()
        q = multiprocessing.Queue()
        name, data2send, t = self.prepareExperiment(pos)


        # Get client latency
        try:
            # Activate flag to test in server


            # Measuring samples
            mouse = multiprocessing.Process(name= "mouse",target = self.mouseMeasurement, args=(data2send,name,mouse_q,))
            mov = multiprocessing.Process(target=self.checkMoveHost, args=(10, movCheck_q,))



            # If some ping object is given as input, prepare Queue and Process
            if (len(pings) > 0):
                (ping_worker, ping_q) = self.pingThread_start(pings)



            mouse.start()
            mov.start()
            #time.sleep(2)

            # User actions

            (img, imgt) = self.gettingFramesThread(thread=mouse)

            r = mouse_q.get()
            # Wait until process have finished
            mov.join()


        except:
            # print("Fail in getting Frames from moonlight")
            traceback.print_exc()

            # If something fails, desactivate server test procedures
            serverTest = False



        # Stop Moonlight
        self.moonlight.stop_moonlight()


        # Reset character position (game)
        self.rmLol.game_restartCharacterPosition()

        # print("Server Test -->",serverTest)


        ping_results = list()

        if (len(pings) > 0):
            ping_results = self.pingThread_get(ping_worker,ping_q)

            # TODO: Rename pings for its differentiation with the previous ones
            for index,ping in enumerate(pings):
                pings[index]["label"] = ping["label"] + "_"
            (ping_worker, ping_q) = self.pingThread_start(pings)

        print("Server test --> " + str(serverTest))
        if (serverTest):

            time.sleep(8) # Wait this time for restarting game's champion position

            # Server test procedure
            server = multiprocessing.Process(target= self.serverExperiment , args=(pos,q,))
            server.start()

            # Get client measures
            try:
                kqi = self.getKQIs(r, img, imgt)
                server.join()
                hostLatency = q.get()
                hostLatency = np.asarray(hostLatency["latency"])
                self.rmLol.game_restartCharacterPosition()
            except:
                traceback.print_exc()
                kqi = dict()
                kqi['filename'] = name

        else:
            kqi = self.getKQIs(mouseTime = r, img=img, imgt = imgt)
            hostLatency = np.asarray([0.08] * 5)

        # Remove files
        try:
            os.remove(name + "_mouse.npy")
        except:
            print("Files can't be removed")


        kqi.update(self.latencyFormatting("host", hostLatency))

        kqi.update(self.moonlight.get_metricsLog())

        try:
            kqi["cg_latency50Percent"] = kqi["client_latency50Percent"] - kqi["host_latency50Percent"]
        except:
            kqi["cg_latency50Percent"] = 0


        if (len(pings) > 0):
            ping_results += self.pingThread_get(ping_worker,ping_q)


        return kqi, ping_results

    def pingThread_start(self, pings):
        # Ping

        ping_q = [multiprocessing.Queue() for ping in pings]


        ping_worker = list()

        # Initializate and start ping processes
        for index, ping in enumerate(pings):
            # TODO: Check ping test function and name of the ping (according to defined nomenclature)
            ping_worker.append(multiprocessing.Process(target=self.ping, args=(ping["ip"], ping["label"], ping["packetSize"], ping["nPackets"], ping_q[index],)))
            ping_worker[-1].start()

        return ping_worker, ping_q

    def pingThread_get(self, ping_worker, ping_q):
        ping_results = list()
        for index,ping in enumerate(ping_worker):
            ping.join()
            # TODO: Check output of ping function (specially its structure)
            ping_results.append(ping_q[index].get())

        return ping_results



    def mouseMeasurement(self,data, filename, q = None):
        mouseClicks = []
        print("Sending actions")
        monitor = self.__monitorInfo()
        for x in data:
            # Get time between actions
            if ("dMove" in x):
                dMove = x['dMove']
            else:  # If this time is not given in the data, it is taken 1 sec
                dMove = 1
                # Get repetitions
            if ("repetitions" in x):
                rep = x['repetitions']
            else:  # If is not set, it is set to 1
                rep = 1

            for m in range(0, rep):
                for action in x['actions']:
                    mouse.move(action['x'], action['y'], absolute=True)
                    # mouseClicks.append(time.time())
                    mouse.right_click()
                    t = time.time()
                    mouseClicks.append(t)
                    time.sleep(dMove)

        # filename = "pruebas"
        np.save(filename + '_mouse', np.asarray(mouseClicks))
        # np.save("mouse",np.asarray(mouseClicks))
        time.sleep(3)
        if q!= None:
            #q.put(np.asarray(mouseClicks))
            q.put(mouseClicks)
        return np.asarray(mouseClicks)

    def serverExperiment(self, pos, q=None):
        # Get host latency
        try:
            dataFromServer = self.serverCapture(pos)
            res = np.asarray(dataFromServer['latency'])
            time.sleep(2)

        except:
            print("Error in server Experient")
            traceback.print_exc()
            dataFromServer = dict()

        if (q != None):
            q.put(dataFromServer)
        return dataFromServer

    def checkMoveHost(self, time, q=None):
        sIP = self.ip
        sPort = self.port
        try:

            base = "http://" + sIP + ":" + str(sPort)
            url = "/frame/checkMovement?t=" + str(time)
            r = requests.get(base + url)
            resp = r.json()
            if (resp["move"] == 1):
                resp = True
            else:
                resp = False
        except:
            traceback.print_exc()
            resp = False

        if (q != None):
            q.put(resp)
        return resp

    def getSummaryLatency(self,data):
        # Delete negative values
        try:
            ndata = data[data > 0]
            avg = np.sum(ndata) / ndata.size
            maxV = np.max(ndata)
            minV = np.min(ndata)
            percent25 = np.percentile(ndata, 25, axis=0)
            percent50 = np.percentile(ndata, 50, axis=0)
            percent75 = np.percentile(ndata, 75, axis=0)

        except:
            minV = 0
            maxV = 0
            avg = 0
            percent25 = 0
            percent75 = 0
            percent50 = 0
        res = {'min': minV, 'max': maxV, 'avg': avg, 'percent25': percent25, 'percent50': percent50,
               'percent75': percent75}
        return res

    def latencyFormatting(self, prefix, data):
        prefix = prefix + "_"
        hLatency = self.getSummaryLatency(data)
        latencyResults = dict()
        # Change of values to ms
        latencyResults[prefix + 'latencyAvg'] = hLatency['avg'] * 1000
        latencyResults[prefix + 'latencyMax'] = hLatency['max'] * 1000
        latencyResults[prefix + 'latencyMin'] = hLatency['min'] * 1000
        latencyResults[prefix + 'latency25Percent'] = hLatency['percent25'] * 1000
        latencyResults[prefix + 'latency50Percent'] = hLatency['percent50'] * 1000
        latencyResults[prefix + 'latency75Percent'] = hLatency['percent75'] * 1000
        latencyResults[prefix + 'latency'] = (data * 1000).tolist()

        return latencyResults


    def serverScreenInfo(self):
        base = "http://"+ self.ip + ":" + str(self.port)
        header = {'content-type': 'application/json'}
        url = "/frame/info"
        d = dict()
        r = requests.post(base + url, data=json.dumps(d), timeout=20, headers=header)
        return r.json()


    def serverCapture(self, pos):
        # Former serverCapture2
        base = "http://"+ self.ip + ":" + str(self.port)
        header = {'content-type': 'application/json'}
        url = "/frame/host"

        monitor = self.serverScreenInfo()['monitor'][0]
        d = dict()
        d['repetitions'] = pos['repetitions']
        d['dMove'] = pos['dMove']
        xd = int(monitor['width'] * pos['coordinates']['x'])
        yd = int(monitor['height'] * pos['coordinates']['y'])
        d['actions'] = [{'x': xd, 'y': yd}]
        data2send = [d]

        r = requests.post(base + url, data=json.dumps(data2send), timeout=300, headers=header)
        return r.json()


    def gettingFrames(self, t, name2Save, sufix=None):

        monitor = self.__monitorInfo()[1]  # Monitor information

        mLeft = int(monitor['width'] * 0.36) + monitor['left']
        mTop = int(monitor['height'] * 0.13) + monitor['top']
        mon = {"top": mTop, "left": mLeft, "width": 400, "height": 400}  # Area of recording

        fps = 0
        sct = mss.mss()
        title = "Move record"
        array = []
        times = []
        initTime = time.time()

        while (initTime + t > time.time()):
            aux = sct.grab(mon)
            img = np.asarray(aux) # Take screenshot
            times.append(time.time())  # Add timestamp to the list
            array.append(np.asarray(aux))  # Add screenshot to the list
            fps += 1
            # if(showImages):
            #     cv2.imshow(title, img) # Show image
            #     if cv2.waitKey(25) & 0xFF == ord("q"):
            #         cv2.destroyAllWindows()
            #         break

        try:
            if (sufix == None):
                # Save list in numpy array form
                np.save(name2Save + '_images', np.asarray(array))
                np.save(name2Save + '_timestamp', np.asarray(times))
            else:
                np.save(name2Save + '_images' + str(sufix), np.asarray(array))
                np.save(name2Save + '_timestamp' + str(sufix), np.asarray(times))
        except:
            print("Fail in getting Frames")
            traceback.print_exc()
        print("Average FPS: ", fps / t)


    # def gettingFramesOnline(self, t, name2Save, sufix=None):
    #   #TODO: For getting metrics on live
    #
    #
    #     monitor = self.__monitorInfo()[1]  # Monitor information
    #
    #     mLeft = int(monitor['width'] * 0.36) + monitor['left']
    #     mTop = int(monitor['height'] * 0.13) + monitor['top']
    #     record_area = {"top": mTop, "left": mLeft, "width": 400, "height": 400}  # Area of recording
    #
    #     fps = 0
    #     sct = mss.mss()
    #     title = "Move record"
    #     array = []
    #     times = []
    #     initTime = time.time()
    #
    #     auxImg = np.asarray(sct.grab(record_area))
    #
    #     th = 0.75*auxImg.size
    #     freezeFrames = 0
    #     times = list()
    #     while (initTime + t > time.time()):
    #
    #         img = np.asarray(sct.grab(record_area))
    #         t = time.time()
    #
    #         dif = np.sum(img == auxImg)
    #
    #         if (dif < th): # It means that there is a huge different with the predecessor --> Movement!
    #             times.append(t)
    #         elif dif == auxImg.size:
    #             freezeFrames += 1
    #
    #         times.append(time.time())  # Add timestamp to the list
    #         array.append(img)  # Add screenshot to the list
    #         fps += 1
    #         # if(showImages):
    #         #     cv2.imshow(title, img) # Show image
    #         #     if cv2.waitKey(25) & 0xFF == ord("q"):
    #         #         cv2.destroyAllWindows()
    #         #         break
    #
    #
    #     print("Average FPS: ", fps / t)
    #
    #     mouse = np.load(name2Save + "_mouse.npy")



    def gettingFramesThread(self,thread):
        monitors = self.__monitorInfo()
        mon = {"top": int(monitors[0]['height'] * 0.31), "left": int(monitors[0]['width'] * 0.41), "width": 400,
               "height": 400} # Coordinates of the monitor part which will be record

        fps = 0
        sct = mss.mss()
        array = []
        times = []
        initTime = time.time()

        while (thread.is_alive()):
            # t = time.time()
            times.append(time.time())  # Add timestamp to the list
            img = np.asarray(sct.grab(mon))  # Take screenshot
            array.append(img)  # Add screenshot to the list
            fps += 1

        print('Avg fps capture', fps / (time.time() - initTime))

        # TODO: Check if it is better return in list mode or numpy array (in terms of size)
        return array, times

    def gettingFramesWindows(self):
        # TODO: Check if condition degrade frame capturing rate. If not, integrate in only one function
        showImages = True
        title = "Test"
        monitors = self.__monitorInfo()
        mon = {"top": int(monitors[0]['height'] * 0.13), "left": int(monitors[0]['width'] * 0.36), "width": 400,
               "height": 400} # Coordinates of the monitor part which will be record

        fps = 0
        sct = mss.mss()
        array = []
        times = []
        initTime = time.time()

        while (True):

            t = time.time()
            times.append(time.time())  # Add timestamp to the list
            img = np.asarray(sct.grab(mon))  # Take screenshot
            array.append(img)  # Add screenshot to the list
            fps += 1

            if(showImages):
                cv2.imshow(title, img) # Show image
                if cv2.waitKey(0) & 0xFF == ord("q"):
                    cv2.destroyAllWindows()
                    break
        print('Avg fps capture', fps / (time.time() - initTime))

        # TODO: Check if it is better return in list mode or numpy array (in terms of size)
        return array, times

    def getKQIs(self,mouseTime, img, imgt):


        results = dict()

        stall_q = multiprocessing.Queue()
        stalls = multiprocessing.Process(target=self.getStalls, args=(img, imgt, 30, stall_q,))

        stalls.start()
        latencyValues, efps = self.getResponsivity(mouseTime, np.asarray(img), np.asarray(imgt))

        results = self.latencyFormatting("client", latencyValues)
        results["efps"] = efps
        stalls.join()
        #np.save(name2Save + "_results", np.asarray(results))

        # Gathering kqi data
        results.update(stall_q.get())

        return results

    def getResponsivity(self,times, img, imgt):
        # Former getResponsitivy4
            try:
                indexs = self.groupFramesbyAction(imgt, times)

                imgGr = []  # Grouped frames by actions
                indexsL = []
                frozenFrames = 0
                for i in range(len(indexs)):
                    fI = indexs[i]
                    if (i == len(indexs) - 1):
                        lI = imgt.size
                    else:
                        lI = indexs[i + 1]

                    indexsL.append([fI, lI])
                    (data, fFrames) = self.imgChange(img[fI:lI], imgt[fI:lI])
                    frozenFrames += fFrames
                    imgGr.append(data)


                latency = []
                fV = self.getFPS(imgt)
                delta = self.getDeltaTime(fV["avgFPS"])
                # Calculate latency
                for x in range(len(times)):
                    latency.append(self.calculateLatency(delta,times[x], imgt[indexsL[x][0]: indexsL[x][1]], imgGr[x], imgt[-1]))


                eFPS = (fV["nFrames"] - frozenFrames)/fV["time"]

            except:
                print("Error in calculating Responsivity")
                traceback.print_exc()
                latency = [0] * len(times)
                eFPS = 0
            return (np.asarray(latency), eFPS)

    def getDeltaTime(self,fps):
        return 1 / fps

    def imgChange(self, img, t, th=None):
        # Former imgChange2
        if (th == None):
            th = 0.75 * img[0].size  # Change threshold to take into account when there is a move
        fI = -1
        fE = -1
        tI = -1
        tE = -1
        data = [] # List of list where information about image changes (i.e., character movement) will be saved
        # Format of data: [number of first frame when the movement is displayed, number of last frame of movement displayed, timestamp of first frame, timestamp of last frame)

        freezeFrames = 0
        for i in range(1, img.shape[0]):
            dif = np.sum(img[i - 1] == img[i])
            if (dif < th):
                if (fI == -1):  # It means that it is the first frame with changes
                    fI = i
                    tI = t[i]

                if (i == img.shape[0]):
                    fE = i
                    tE = t[i]
                    data.append([fI, fE, tI, tE])
            elif (dif == img[0].size):
                freezeFrames += 1
            else:
                if (fI != -1):
                    fE = i
                    tE = t[i]
                    data.append([fI, fE, tI, tE])
                    fI = -1

        if (len(data) == 0): # If lenght of the list is 0 means that no movement is detected. Therefore, list is filled with -1 values
            print("No movement detected")
            data.append([-1, -1, -1, -1])

        return (data, freezeFrames)

    def getFPS(self,t):
        dT = []
        t = np.asarray(t)
        #for x in range (1,t.size):
        for x in range(1,t.size-1):
            dT.append(t[x]-t[x-1])

        dT2 = np.asarray(dT)
        res = dict()
        res['avgFPS'] = round(t.size/(t[t.size-1]-t[0]))
        res['avgDeltaFrame'] = np.sum(dT2)/dT2.size
        res['time'] = t[t.size-1] - t[0]
        res['nFrames'] = t.size
        return res


    def calculateLatency(self, delta, t0, imgt, imgGr, tE):
        try:
            index = imgGr[0][0]  # Index
            if (index != -1):
                t1 = imgt[0] - t0
                deltas = np.asarray(self.getDeltas(imgt))
                diff = deltas[:index] - delta
                latency = (imgGr[0][2] - t0) - diff.sum()

            else:
                latency = tE - t0
        except:
            latency = 0
        return latency

    def getDeltas(self,imgt):
        deltas = []
        imgt = np.asarray(imgt)
        for x in range(1, imgt.size):
            deltas.append((imgt[x] - imgt[x - 1]))
        return deltas

    def getStalls(self, img, imgt, fps, q=None):
        # Load data
        info = self.getFPS(imgt) # Get frame rate information related with captured images from user's screen

        # If captu
        if (info['avgFPS'] > fps):
            (img, imgt) = self.diemadoFPS(img,imgt, fps) # Fiting frames with configured session frame rate

        iRes = self.imgFreeze(img, imgt)
        del img

        iC = np.asarray(iRes)  # Relevant Information
        info = self.getFPS(imgt)
        # print(iC)
        res = dict()
        res['numberStalls'] = iC.shape[0]
        res['numberTotalFrames'] = imgt.size
        try:
            res['stallDuration'] = (iC[:, 3] - iC[:, 2]).tolist() # Duration of the stall
            res['stallNFrames'] = ((iC[:, 1] - iC[:, 0]).astype('int32')).tolist() # Amount of frozen frames
            res['stallIFrame'] = (iC[:, 0].astype('int32')).tolist() # Index of the first frozen frame
            res['stallLFrame'] = (iC[:, 1].astype('int32')).tolist() # Index of the last frozen frame
            res['stallInit'] = iC[:, 2].tolist()
            res['stallTotalTime'] = np.sum(iC[:, 3] - iC[:, 2])
            res['freezePercent'] = res['stallTotalTime'] / info['time']
        except:
            # This exception arises if arrays are empty, which means that no freeze has occured during the session
            print("No freeze has occured")
            res.update({key:[] for key in ["stallDuration", "stallNFrames", "stallIFrame", "stallLFrame", "stallInit"]}) # Fill dict fields with empty lists
            res.update({key:0 for key in ["stallTotalTime", "freezePercent"]}) # Since no stall is detected, this values must be 0

        del iC
        if (q != None):
            q.put(res)
        return res

    def groupFramesbyAction(self,imgt, tim):
        i = 0
        inde = []
        for t in tim:
            found = False
            while (not found):
                try:
                    if (t < imgt[i]):
                        found = True
                        inde.append(i)
                    i += 1
                except:
                    print("Index out of range --> imgGroup")
                    print("size -->", imgt.size)
                    print("Index -->", i)
                    break

        return inde

    def diemadoFPS(self,img, imgt, targetFPS):

        info = self.getFPS(imgt)
        duration = info['time']

        targetNumberFrames = round(duration * targetFPS)
        im = np.asarray(imgt)

        deltas = np.asarray(self.getDeltas(imgt))

        pFrames = targetNumberFrames / info["nFrames"] * 100
        percent = 100 - pFrames

        th = np.percentile(deltas, percent)
        imgt = np.asarray(imgt)
        index2del = []
        for x in range(1, imgt.size):
            dif = imgt[x] - imgt[x - 1]
            if (dif < th):
                index2del.append(x)

            # print(index2del)
        img2 = np.delete(img, index2del, 0)
        imgt2 = np.delete(imgt, index2del)

        return (img2, imgt2)

    def imgFreeze(self,img, t):
        th = img[0].size  # Change threshold to take into account when there is a move
        fI = -1
        fE = -1
        tI = -1
        tE = -1
        data = []
        thF = 3
        for i in range(1, img.shape[0]):
            eq = np.sum(img[i - 1] == img[i])
            if (eq >= th):
                if (fI == -1):  # It means that it is the first freeze frame
                    fI = i
                    tI = t[i]

                if (i == img.shape[0] - 1):  # It means that it is the last element
                    fE = i
                    tE = t[i]
                    data.append([fI, fE, tI, tE])
            else:
                if (fI != -1):
                    if (i - fI > thF):  # It is considered freeze when more than thF consecutive frames are equals
                        fE = i
                        tE = t[i]
                        data.append([fI, fE, tI, tE])
                    fI = -1
        return data

    def pingTest(self,ip, name, size, num, queue=None):
        # TODO: Migrate to ping class
        plat = platform.system()
        vD = dict()
        try:
            if (plat == "Windows"):
                out = os.popen("ping -l " + str(size) + " -n " + str(num) + " " + ip).read()

                #print(out)

            vD[name + "_IP"] = ip
            # Get packet lenght
            index = out.find("with")
            l = len("with")
            if (index == -1):  # If not found, try with Spanish
                index = out.find("con")
                l = len("con")

            aux = out[index + l:out.find(":")]
            aux = aux[:aux.find("bytes") - 1]

            try:
                vD[name + '_packetLength'] = int(aux)  # Bytes
            # vD['PING_packetLength'] = int(aux) #Bytes
            except:
                vD[name + '_packetLength'] = int(aux)  # Bytes
            # vD['PING_packetLength'] = None

            # Get statistics
            index = out.find("Packets")
            index2 = out.find("Approximate")
            if (index == -1):
                index = out.find("Paquetes")
                index2 = out.find("aproximados")

            aux = out[index:index2]
            index = aux.find(":") + 1
            aux = aux[index:-3]
            index = aux.find("(")
            aux2 = aux[index:]
            aux = aux[:index]

            values = aux.split(",")

            for i in values:
                index = i.find("=") + 1
                aux = i[index + 1:]
                key = i[:index - 2]
                aux = aux[:index]
                # vD["PING_"+key.strip()] = int(aux)

                if (aux.find("\r") != -1):
                    aux = aux[:aux.find("\r")]
                # print(key.strip())
                # while(aux.find('') != -1):
                # 	print("hi")
                # 	aux = aux[aux.find(''):]

                vD[name + "_" + key.strip()] = int(aux.strip())
            aux2 = aux2[1:aux2.find("%")]
            vD[name + '_LossPercentage'] = int(aux2)
            # vD['PING_LossPercentage'] = int(aux2)

            # Get RTT
            index = out.find("Minimum")
            if (index == -1):
                index = out.find("Mnimo")
            aux = out[index:-1]
            values = aux.split(",")
            for i in values:
                index = i.find("=") + 1
                aux = i[index + 1:]
                key = i[:index - 2]
                index = aux.find("m")
                aux = aux[:index]
                vD[name + "_" + key.strip()] = int(aux)
        except:
            vD = dict()
            traceback.print_exc()
        # if queue is not None:
        if queue != None:
            queue.put(vD)
        return vD

    def getStatsFromPing(self, data):
        # Find line with statistics
        results = data.split("\n")
        index = 0
        res = dict()
        RTT_values = []
        for l in range(len(results)):
            if results[l].find("PING") != -1:
                data = results[l][results[l].find("PING") + len("PING"): results[l].find(")")].strip()
                res["ping_dest"] = data[:data.find("(")]
                res["ping_dest_ip"] = data[data.find("(") + 1:]
            elif results[l].find("time=") != -1:
                rtt_value_str = results[l][results[l].find("time=") + len("time="):results[l].find(" ms")]
                RTT_values.append(float(rtt_value_str))
            elif results[l].find("statistics") != -1:
                # print(l)
                # print(results[l])
                index = l
        index = index + 1
        # print(RTT_values)
        try:
            stats = results[index].split(",")

            res["packetTransmited"] = int(stats[0].split(" ")[0])

            res["packetReceived"] = int(stats[1].split(" ")[1])

            res["packetLoss"] = stats[2].split(" ")[1]

            # The next line provides RTT metrics
            index = index + 1
            # print(results[index])
            stats = results[index].split("=")
            # print(stats)
            desc = stats[0].split(" ")[1].split("/")
            val = stats[1].split(" ")[1].split("/")
            # val = stats[1].split("/")

            for key in range(len(desc)):
                res["RTT_" + desc[key]] = float(val[key])
            res["RTT_values"] = RTT_values
            # There will be connectivity if at least one packet is received
            res["connectivity"] = res["packetReceived"] > 0
        except:
            res["connectivity"] = False
        return res

    def getStatsPing_windows(self,data):
        # TODO: surrond each element with a exception
        # Find line with statistics
        results = data.split("\n")
        index = 0
        res = dict()
        RTT_values = []

        for l in range(len(results)):
            if results[l].find("Haciendo ping") != -1:

                data = results[l].split(" ")
                res["ping_dest"] = data[3].strip()

                if data[4].find("[") != -1:
                    res["ping_dest_ip"] = data[4][1:-1].strip()
                else:
                    res["ping_dest_ip"] = data[3].strip()

            elif results[l].find("tiempo=") != -1:
                rtt_value_str = results[l][results[l].find("tiempo=") + len("tiempo="):results[l].find("ms")]
                RTT_values.append(float(rtt_value_str))
            elif results[l].find("Estad") != -1:
                # print(l)
                # print(results[l])
                index = l
        index = index + 1
        # print(RTT_values)
        try:
            keys = ["Transmited", "Received", "Loss"]
            stats = results[index].split(",")
            for ind, k in enumerate(keys):
                try:
                    res["packet" + k] = int(stats[ind].split("=")[1])
                except:
                    res["packet" + k] = stats[ind].split("=")[1].strip()

            index += 1
            res["packetLoss_percentage"] = int(results[index][results[index].find("(") + 1:results[index].find("%")])
            # The next line provides RTT metrics
            index += 2
            # print(results[index])

            stats = results[index].split(",")
            # print(stats)
            desc = ["min", "avg", "max"]

            for ind, key in enumerate(desc):
                ax = stats[ind].split("=")
                res["RTT_" + key] = float(ax[1][:-2])
            res["RTT_values"] = RTT_values
            # There will be connectivity if at least one packet is received
            res["connectivity"] = res["packetReceived"] > 0
        except:
            res["connectivity"] = False
        return res

    def ping(self, ip, name, size, nPackets, q=None):
        res = dict()
        # cmdB = "ping " +

        cmd = "ping " + ip

        # Regarding the platform, the flag of number of packets is different
        if platform.platform().find("linux") != -1:  # Linux
            cmd += " -c " + str(nPackets)
            t_init = time.time()
            x = os.popen(cmd).read()
            t_end = time.time()
            res = self.getStatsFromPing(x)

        elif platform.system().find("Windows") != -1:  # Windows
            cmd += " -n " + str(nPackets) + " -l " + str(size)
            t_init = time.time()
            x = os.popen(cmd).read()
            t_end = time.time()
            res = self.getStatsPing_windows(x)

        res["t_init"] = t_init
        res["t_end"] = t_end

        if q != None:
            q.put(res)

        return res
