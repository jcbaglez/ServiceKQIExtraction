import numpy as np
import mss
from PIL import Image
import time
import cv2
import requests
import json
import traceback
import mouse
import matplotlib.pyplot as plt
import multiprocessing
############################################################################
# This functions capture the area of the monitor and saves the images, as well as
# their timestamp in a .npy file (whose name is given as a input). This function
# will be recording meanwhile the thread given as input stays alive
############################################################################
def gettingFramesThread2(thread,name2Save,showImages=False):
    mon = {"top":250, "left":700, "width": 400, "height":400} # Coordinates of the monitor part which will be record
    monitors = monitorInfo()
    mon = {"top":int(monitors[0]['height']*0.13), "left":int(monitors[0]['width']*0.36), "width": 400, "height":400}
    #mon = {"top":int(monitors[0]['height']*0.13), "left":int(monitors[0]['width']*0.36), "width": 50, "height":50}
    fps = 0
    sct = mss.mss()
    title = "Move record"
    array = []
    times=[]
    initTime = time.time()
    while(thread.isAlive()):
        #print(1)
        #t = time.time()
        times.append(time.time())
        img = np.asarray(sct.grab(mon)) # Take screenshot

        #times.append(time.time()) # Add timestamp to the list
        array.append(img) # Add screenshot to the list
        fps +=1
        if(showImages):
            cv2.imshow(title, img) # Show image
            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break

    print('Avg fps capture',fps/(time.time()-initTime))
    try:
        np.save(name2Save +'_images',np.asarray(array))
        np.save(name2Save +'_timestamp',np.asarray(times))
    except:
        print("Error in save captured frames")
        traceback.print_exc()
def gettingFramesThread(thread,name2Save,showImages=False):
    mon = {"top":250, "left":700, "width": 400, "height":400} # Coordinates of the monitor part which will be record
    monitors = monitorInfo()
    mon = {"top":int(monitors[0]['height']*0.13), "left":int(monitors[0]['width']*0.36), "width": 400, "height":400}
    #mon = {"top":int(monitors[0]['height']*0.13), "left":int(monitors[0]['width']*0.36), "width": 50, "height":50}
    fps = 0
    sct = mss.mss()
    title = "Move record"
    array = []
    times=[]
    initTime = time.time()
    while(thread.is_alive()):
        #t = time.time()con
        times.append(time.time())
        img = np.asarray(sct.grab(mon)) # Take screenshot

        #times.append(time.time()) # Add timestamp to the list
        array.append(img) # Add screenshot to the list
        fps +=1
        if(showImages):
            cv2.imshow(title, img) # Show image
            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break

    print('Avg fps capture',fps/(time.time()-initTime))
   
    # Save list in numpy array form
    try:
        np.save(name2Save +'_images',np.asarray(array))
        np.save(name2Save +'_timestamp',np.asarray(times))
    except:
        print(np.asarray(array).shape)
        np.save(name2Save +'_images',np.asarray(array))
        np.save(name2Save +'_timestamp',np.asarray(times))
    mouse = np.load(name2Save + "_mouse.npy")
    #results = getResponsivity(mouse,np.asarray(array),np.asarray(times))
    results = getResponsivity3(mouse,np.asarray(array), np.asarray(times))
    print(results)
    #results2 = getResponsivity2(mouse,np.asarray(array), np.asarray(times))
    #print(results2)

    np.save(name2Save + "_results",np.asarray(results))
    print("AS")

############################################################################
# This functions capture the area of the monitor and saves the images, as well as
# their timestamp in a .npy file (whose name is given as a input). This function
# will be recording for 't' seconds
############################################################################
def gettingFrames(t,name2Save,sufix = None):
    monitor = monitorInfo()[1] #Monitor information
    mLeft = int(monitor['width']*0.36) + monitor['left']
    mTop = int(monitor['height']*0.13) + monitor['top']
    mon = {"top":mTop,"left":mLeft, "width": 400, "height":400} # Area of recording
    fps = 0
    sct = mss.mss()
    title = "Move record"
    array = []
    times=[]
    initTime = time.time()
    while(initTime + t > time.time() ):
        aux = sct.grab(mon)
        img = np.asarray(aux)
        #img = np.asarray(sct.grab(mon)) # Take screenshot
        times.append(time.time()) # Add timestamp to the list
        array.append(np.asarray(aux)) # Add screenshot to the list
        fps +=1
        # if(showImages): 
        #     cv2.imshow(title, img) # Show image
        #     if cv2.waitKey(25) & 0xFF == ord("q"):
        #         cv2.destroyAllWindows()
        #         break

    
    if (sufix == None):
        # Save list in numpy array form
        np.save(name2Save +'_images',np.asarray(array))
        np.save(name2Save +'_timestamp',np.asarray(times))
    else:
        np.save(name2Save +'_images'+str(sufix),np.asarray(array))
        np.save(name2Save +'_timestamp'+str(sufix),np.asarray(times))
    print("Average FPS: ", fps/t)
    return (array,times)

def gettingFramesMultiThreads(t,name2Save,nThreads = 3):
    pool = []
    for x in range(nThreads):
        pool.append(multiprocessing.Process(target= gettingFrames, args=(t,name2Save,x,)))

    for x in range(nThreads):
        pool[x].start()
        
    #time.sleep(2)

    # r = mouseMeasurement(data2send,name)

    for x in range(nThreads):
        pool[x].join()

    img, imgt = gatherData(name2Save,nThreads)

    np.save(name2Save +"_images_All",img)
    np.save(name2Save +"_timestamp_All",imgt)


def gatherData(name2Save,nThreads):
    images = []
    times = []
    indexs = []
    length = []
    allImages = []
    allTimes = []
    for x in range(nThreads):
        images.append(np.load(name2Save+"_images"+str(x)+".npy"))
        times.append(np.load(name2Save+"_timestamp"+str(x) + ".npy"))
        indexs.append(0)
        length.append(times[len(times)-1].size)
    
    end = False
    threadIndex = 0
    threadFinish = 0
    while not end:
        elemIter = -1 
        for thread in range(nThreads):
            if(indexs[thread] < length[thread]): # If true, it means that there are data available to take from this buffer
                if(elemIter == -1 or elemIter >times[thread][indexs[thread]]): # If it is the first iteration or the timestamp set as lowest as this thread sample, this is set as the lowest one
                    elemIter = times[thread][indexs[thread]]
                    threadIndex = thread
                

        allImages.append(images[threadIndex][indexs[threadIndex]])
        allTimes.append(times[threadIndex][indexs[threadIndex]])
        indexs[threadIndex] +=1

        if (indexs[threadIndex] == length[threadIndex]): # Check if there still are data available in this buffer
            threadFinish += 1 # Update threadFinish counter
        
        if (threadFinish == nThreads): # If data of all buffer has been taken
            end = True
        
    
    return (np.asarray(allImages), np.asarray(allTimes))

def gettingFramesDemo(t):
    monitor = monitorInfo()[1]
    mLeft = int(monitor['width']*0.45) + monitor['left']
    mTop = int(monitor['height']*0.2) + monitor['top']
    mon = {"top":mTop,"left":mLeft, "width": 400, "height":400}
    fps = 0
    sct = mss.mss()
    title = "Move record"
    array = []
    times=[]
    initTime = time.time()
    auxImg = np.asarray(sct.grab(mon))
    th = 0.4*auxImg.size # Change threshold to take into account when there is a movement
    print(th)
    while(initTime + t > time.time() ):
        img = np.asarray(sct.grab(mon)) # Take screenshot
        times.append(time.time()) # Add timestamp to the list
        array.append(img) # Add screenshot to the list
        fps +=1

        cv2.imshow(title, img) # Show image
        dif = np.sum(img == auxImg)
        #print(dif)
        if(dif < th):
            print("[Frame ",str(fps),"] Character is moving")

        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

        auxImg = img

    print("Average FPS: ", fps/t)



############################################################################
# This function groups all the consecutive screenshots which are different.
#  Thus, it returns a tuple with 2 lists: The first one 
# corresponds to the useful data such as the number of the frame, timestamp...
# The second one corresponds with the number of pixels which are equal between
# two consecutive images 
############################################################################
def imgChange(img,t, coef = 0.75):
    th = coef*img[0].size # Change threshold to take into account when there is a move
    fI = -1
    fE = -1
    tI = -1
    tE = -1
    imgDif = []
    data = []
    #for i in range (1,img.shape[0]):
    for i in range (1,t.size):
        dif = np.sum(img[i-1] == img[i])
        imgDif.append(dif)
        if(dif<th):
            if(fI == -1): # It means that it is the first frame which changes
                fI = i
                tI = t[i]

            if (i == img.shape[0]):
                fE = i
                tE = t[i]
                data.append([fI,fE,tI,tE])
        else:
            if(fI != -1):
                fE = i
                tE = t[i]
                data.append([fI,fE,tI,tE])
                fI = -1

    return (data,imgDif)

def imgChange2(img,t,th = None):
    if (th == None):
        th = 0.75*img[0].size # Change threshold to take into account when there is a move
    fI = -1
    fE = -1
    tI = -1
    tE = -1
    imgDif = []
    data = []
    info = getFPS(t)
    contFrames = info['nFrames']
    for i in range (1,img.shape[0]):
        dif = np.sum(img[i-1] == img[i])
        #imgDif.append(dif)
        if(dif<th):
            if(fI == -1): # It means that it is the first frame which changes
                fI = i
                tI = t[i]

            if (i == img.shape[0]):
                fE = i
                tE = t[i]
                data.append([fI,fE,tI,tE])
        elif(dif == img[0].size):
            contFrames -= 1
        else:
            if(fI != -1):
                fE = i
                tE = t[i]
                data.append([fI,fE,tI,tE])
                fI = -1

    if (len(data) == 0):
        data.append([-1, -1, -1 ,-1])
    
    effectiveFPS = contFrames/info['time']
    
    return (data,effectiveFPS)

def imgFreeze(img,t):
    th = img[0].size # Change threshold to take into account when there is a move
    fI = -1
    fE = -1
    tI = -1
    tE = -1
    imgDif = []
    data = []
    thF = 3
    for i in range (1,img.shape[0]):
        eq = np.sum(img[i-1] == img[i])
        if(eq >= th):
            if(fI == -1): # It means that it is the first freeze frame
                fI = i
                tI = t[i]
                
            if (i == img.shape[0]-1): # It means that it is the last element
                fE = i 
                tE = t[i]
                data.append([fI,fE,tI,tE])
        else:
            if(fI != -1):
                if (i - fI > thF): # It is considered freeze when more than thF consecutive frames are equals 
                    fE = i
                    tE = t[i]
                    data.append([fI,fE,tI,tE])
                fI = -1
    return data

def groupFramesbyAction(imgt,tim):
    i = 0
    inde = []
    for t in tim:
        found = False
        while(not found):
            try:
                if(t<imgt[i]):
                    found = True
                    inde.append(i)
                i += 1
            except:
                print("Index out of range --> imgGroup")
                print("size -->", imgt.size)
                print("Index -->",i)
                break
  
    return inde
    
    

############################################################################
# This function is in charge of grouping different groups of consecutive changing
# frames. In this way, it allows to correct a possible error of capturing.
# This function returns a list with n rows (being n the number of groups) and
# 4 colums (firstFrame, lastFrame,initial timestamp, ending timestamp, duration)  
############################################################################
def deltaFrame(data):
    ff = -1
    newData = []
    print(data.shape[0]-1)
    deltaFrame = 4 # Max difference between last frame of a group and the first frame of the next one in order to be considered the same group
    for x in range(0,data.shape[0]-1):
        aux = data[x+1,0] - data[x,1]
        if(aux <deltaFrame):
            if (ff == -1):
                if (x == data.shape[0]-2):
                    newData.append([data[x][0],data[x][1],data[x][2],data[x][3],data[x][3]-data[x][2]])
                else:
                    ff = x
            elif(x== data.shape[0]-2):
                newData.append([data[ff,0],data[x+1,1],data[ff,2],data[x+1,3],data[x+1,3]-data[ff,2]])
        else:
            if (ff != -1):
                newData.append([data[ff,0],data[x,1],data[ff,2],data[x,3],data[x,3]-data[ff,2]])
                ff = -1
            else:
                newData.append([data[x][0],data[x][1],data[x][2],data[x][3],data[x][3]-data[x][2]])

    return newData

def deltaFrame2(data,time):
    ff = -1
    newData = []
    index = []
    #print(data.shape[0]-1)
    inde = []
    i = 0
    for t in time:
        found = False
        while(not found):
            try:
                if(t<data[i,2]):
                    found = True
                    inde.append(i)
                i += 1
            except:
                print("Index out of range --> imgGroup")
                break

    if (len(inde) != time.size):
        time = time[:len(inde)]

    print(inde)
    deltaFrame = 4 # Max difference between last frame of a group and the first frame of the next one in order to be considered the same group
    for x in range(0,data.shape[0]-1):
        aux = data[x+1,0] - data[x,1]
        if(aux <deltaFrame): #If the difference between frames is less than the threshold, they are considered in the same group
            if (ff == -1): # If there is not a initiated group
                if (x == data.shape[0]-2): # If it is the last sample of the dataset
                    newData.append([data[x][0],data[x][1],data[x][2],data[x][3],data[x][3]-data[x][2]])
                    index.append({'f':x,'l':x})
                else:
                    ff = x # Initialize group

            elif(x== data.shape[0]-2): # If this difference is between a group but it is the last sample of the dataset
                newData.append([data[ff,0],data[x+1,1],data[ff,2],data[x+1,3],data[x+1,3]-data[ff,2]])
                index.append({'f':ff,'l':x+1})

        else: # If the diference is greater than the treshold
            if (ff != -1): # If there is a group, it is closed
                newData.append([data[ff,0],data[x,1],data[ff,2],data[x,3],data[x,3]-data[ff,2]])
                index.append({'f':ff, 'l':x})
                ff = -1 # Reset new group

            else: # If not, it means that it is not neccesary to gather with other Group of frames
                newData.append([data[x][0],data[x][1],data[x][2],data[x][3],data[x][3]-data[x][2]])
                index.append({'f':x, 'l':x})

    print(index)
    return newData
###################################################################################
# This function take the n elements with more gap and sorts it out cronologically
###################################################################################
def takeNElement(n,data):
    sortArray = []
    auxTE = data[:,4]
    sortedTE = np.sort(auxTE)[::-1]

    for x in range(0,n):
        sortArray.append(data[np.where(auxTE==sortedTE[x])[0][0]].tolist())

    sortArrayTE = np.asarray(sortArray)
    auxTE = sortArrayTE[:,0]

    sortArray2 = np.sort(auxTE)
    aux = []
    for x in range(0,sortArray2.shape[0]):
        aux.append(sortArrayTE[np.where(sortArrayTE[:,0] == sortArray2[x])[0][0]].tolist())

    return np.asarray(aux)

def responseMouse(time,data):
    dat = []
    tim = []
    siz = min(time.size,data.shape[0])
    if(time.size < data.shape[0]):
        d = 0
        for t in time:
            tim.append(t)
            found = False
            while(not found):
                if (d == time.size):
                    break
                if (data[d,2]>t):
                    dat.append(data[d])
                    found = True
                elif (bool(dat) and dat[len(data)-1][4]<data[d,4]):
                    dat[len(data)-1] = data[d]
                d += 1
    else:
        d = 0
        for i in data:
            
            dat.append(i)
            found = False
            while(not found):
                if (d == data.shape[0]):
                    break
                if (i[2]<time[d]):
                    tim.append(time[d])
                d +=1
    return (np.asarray(tim),np.asarray(dat))

def takeScreenshot():
    #mon = {"top":250, "left":700, "width": 400, "height":400} # Coordinates of the monitor part which will be record
    monitor = monitorInfo()[1]
    mLeft = int(monitor['width']*0.36) + monitor['left']
    mTop = int(monitor['height']*0.13) + monitor['top']
    mon = {"top":mTop,"left":mLeft, "width": 400, "height":400}
    sct = mss.mss()
    title = "Move record"

 
    #img = np.asarray(sct.grab(mon)) # Take screenshot
    img = sct.grab(mon)
    mss.tools.to_png(img.rgb,img.size,output="prueba.png")

    # Save list in numpy array form
    #np.save(name2Save +'_images',np.asarray(array))


###################################################################################
# This function returns a list with information about the available monitors:
# The first element of the list corresponds with the whole monitor of the computer,
# this means, the combination of all monitors (if there is more than one). The rest
# of elements corresponds with the individual information of each connected monitor
###################################################################################
def monitorInfo():
    return np.asarray(mss.mss().monitors)


def mouseMeasurement(data,filename):
    mouseClicks = []
    print("Move")
    for x in data:
        #Get time between actions
        if ("dMove" in x):
            dMove = x['dMove']
        else: # If this time is not given in the data, it is taken 1 sec
            dMove = 1
            #Get repetitions
        if ("repetitions" in x):
            rep = x['repetitions']
        else: # If is not set, it is set to 1
            rep = 1
        
        for m in range(0,rep):
            for action in x['actions']:
                print(m)
                print(action)
                mouse.move(action['x'],action['y'],absolute=True)
                    #mouseClicks.append(time.time())
                mouse.right_click()
                t = time.time()
                mouseClicks.append(t)
                time.sleep(dMove)

    #filename = "pruebas"
    np.save(filename +'_mouse',np.asarray(mouseClicks))
    #np.save("mouse",np.asarray(mouseClicks))
    return np.asarray(mouseClicks)
def checkREST(ip,port):
    base = "http://"+ip+":"+ str(port)
    header =  {'content-type' : 'application/json'}
    url = "/info"
    d = dict()
    print(base)
    try:
        r = requests.post(base+url, data = json.dumps([d]), timeout= 5, headers = header)
        return True
    except:
        print("REST unavailable")
        return False

def serverPrepare(ip,port):
    base = "http://"+ip+":"+ str(port)
    header =  {'content-type' : 'application/json'}
    url = "/action/keyboard"
    d = dict()
    d['action'] = ["control+shift+i","shift+h", "y"]
    r = requests.post(base+url, data = json.dumps([d]), headers = header)


def serverPrepareGame(ip,port,mode):
    base = "http://"+ip+":"+ str(port)
    header =  {'content-type' : 'application/json'}
    url = "/action/configureClient"
    d = dict()
    d['type'] = mode
    # Start session
    r = requests.post(base+url, data = json.dumps(d), headers = header)

    # Prepare session
    #serverPrepare(ip,port)
 
#serverPrepareGame("192.168.0.57",5000,"trainingTool")


def serverCapture(nActions,q = None):
    try:
        base ="http://192.168.0.100:5000"
        header =  {'content-type' : 'application/json'}
        url = "/frame/hostMeasurement?nActions="+str(nActions)
        r = requests.get(base+url)
        resp = r.json()
    except: 
        traceback.print_exc()
        resp = {}
        
    if (q != None):
        q.put(resp)

    return resp

def serverScreenInfo():
    base = "http://192.168.0.100:5000"
    header ={'content-type': 'application/json'}
    url = "/frame/info"
    d = dict()
    r = requests.post(base + url,data = json.dumps(d),timeout=20,headers=header)
    return r.json()

def serverCapture2(pos):
    base ="http://192.168.0.100:5000"
    header =  {'content-type' : 'application/json'}
    url = "/frame/host"

    monitor = serverScreenInfo()['monitor'][0]
    d = dict()
    d['repetitions'] = pos['repetitions']
    d['dMove'] = pos['dMove']
    xd = int(monitor['width']*pos['coordinates']['x'])
    yd = int(monitor['height']*pos['coordinates']['y'])
    d['actions'] = [{'x':xd, 'y':yd}]
    data2send = [d]

    r = requests.post(base + url,data = json.dumps(data2send), timeout= 300 ,headers=header)
    return r.json()

def loadData(name):
    # try:
    #     imgt = np.load(name+'_timestampN.npy')
    # except:
    #     normalizedDeltaFrames(name)
    #     try:
    #         imgt = np.load(name+'_timestampN.npy')
    #     except:
    #         print("Variables not found --> Check filename")
    #         return ([],[])
    try:
        imgt = np.load(name+"_timestamp.npy")
    except:
        print("wrong")
    try:
        img = np.load(name+'_images.npy')
    except:
        print("Variables not found --> Check filename")
        return ([],[])
        
    return (img,imgt)



def getResponsivity(times,img,imgt):
    # Load data
    #(img, imgt) = loadData(name)
    #print(imgt)
    iRes = imgChange(img,imgt)
    iC = np.asarray(iRes[0]) # Relevant Information
    iCh = np.asarray(iRes[1]) # Number of pixel
    #print(iC)
    imgGroup = np.asarray(deltaFrame(iC))
    if(times.size != imgGroup.shape[0]):
        times, imgGroup = responseMouse(times,imgGroup)
        print("Size times:",times.size)
        print("Size imgGroup", imgGroup.shape[0])

    latency = imgGroup[:,2] - times
    #print("HIII")
    return latency

def getResponsivity2(times,img,imgt):
    # Load data
    #(img, imgt) = loadData(name)
    #print(imgt)
    indexs = groupFramesbyAction(imgt,times)

    imgGr = [] # Grouped frames by actions
    imgDiff = [] # Difference between consecutives frames
    for i in range(len(indexs)):
        fI = indexs[i]
        
        if(i == len(indexs) -1):
            (data,df) = imgChange2(img[fI:], imgt[fI:])
        else:
            (data,df) = imgChange2(img[fI:indexs[i+1]], imgt[fI:indexs[i+1]])

        imgGr.append(data)
        imgDiff.append(df)
    
    latency = []
    for x in range(len(times)):
        try:
            latency.append(imgGr[x][0][2] - times[x])
            # print("Index -->",x)
            # print(imgGr[x])
        except:
            latency.append(-1)


    return latency

def getResponsivity3(times,img,imgt):
    indexs = groupFramesbyAction(imgt,times)
    
    fV = getFPS(imgt)
    delta = getDeltaTime(fV["avgFPS"])
    latency = []

    imgGr = [] # Grouped frames by actions
    imgDiff = [] # Difference between consecutives frames
    for i in range(len(indexs)):
        fI = indexs[i]
        
        if(i == len(indexs) -1):
            (data,df) = imgChange2(img[fI:], imgt[fI:])
        else:
            (data,df) = imgChange2(img[fI:indexs[i+1]], imgt[fI:indexs[i+1]])

        imgGr.append(data)
        imgDiff.append(df)

    # Calculate latency
    for x in range(len(times)):
        try:
            latency.append(imgGr[x][0][0]*delta)
        except:
            latency.append(-1)
    return np.asarray(latency)

def getResponsivity4(times,img,imgt):
    try:
        indexs = groupFramesbyAction(imgt,times)
        eFPS = 0
        fV = getFPS(imgt)
        delta = getDeltaTime(fV["avgFPS"])
        latency = []

        imgGr = [] # Grouped frames by actions
        imgDiff = [] # Difference between consecutives frames
        indexsL = []
        for i in range(len(indexs)):
            fI = indexs[i]
            if(i == len(indexs) -1):
                lI = imgt.size
            else:
                lI = indexs[i+1]
            
            indexsL.append([fI,lI])
            (data,eFPS) = imgChange2(img[fI:lI],imgt[fI:lI])

            imgGr.append(data)
            #imgDiff.append(df)

        latency = []
        # Calculate latency
        for x in range(len(times)):
            latency.append(calculateLatency(delta,times[x],imgt[indexsL[x][0]: indexsL[x][1]],imgGr[x],imgt[-1]))

    except:
        print("Error in calculating Responsivity4")
        traceback.print_exc()
        latency = [0]* len(times)
        eFPS = 0
    return (np.asarray(latency),eFPS, fV["avgFPS"])

def getDeltas(imgt):
    deltas = []
    for x in range(1,imgt.size):
        deltas.append((imgt[x] - imgt[x-1]))
    return deltas

def calculateLatency(delta,t0,imgt,imgGr,tE):
    try:
        index = imgGr[0][0] # Index
        if (index != -1):
            t1 = imgt[0] - t0
            deltas = np.asarray(getDeltas(imgt))
            diff = deltas[:index] - delta
            latency = (imgGr[0][2] - t0) - diff.sum()

        else:
            latency = tE - t0
    except:
        latency = 0
    return latency

def getResponsivityComb(times,img,imgt):
    # Method 1
    iRes = imgChange(img,imgt)
    iC = np.asarray(iRes[0]) # Relevant Information
    iCh = np.asarray(iRes[1]) # Number of pixel
    #print(iC)
    imgGroup = np.asarray(deltaFrame(iC))
    if(times.size != imgGroup.shape[0]):
        times, imgGroup = responseMouse(times,imgGroup)
        print("Size times:",times.size)
        print("Size imgGroup", imgGroup.shape[0])

    latency = imgGroup[:,2] - times
    t1 = imgGroup[:,2].tolist()

    # Method 2
    indexs = groupFramesbyAction(imgt,times)

    imgGr = [] # Grouped frames by actions
    imgDiff = [] # Difference between consecutives frames
    for i in range(len(indexs)):
        fI = indexs[i]
        
        if(i == len(indexs) -1):
            (data,df) = imgChange2(img[fI:], imgt[fI:])
        else:
            (data,df) = imgChange2(img[fI:indexs[i+1]], imgt[fI:indexs[i+1]])

        imgGr.append(data)
        imgDiff.append(df)
    
    latency2 = []
    t2 = []
    for x in range(len(times)):
        try:
            latency2.append(imgGr[x][0][2] - times[x])
            t2.append(imgGr[x][0][2])
            # print("Index -->",x)
            # print(imgGr[x])
        except:
            latency2.append(-1)


   # Method 3
    fV = getFPS(imgt)
    delta = getDeltaTime(fV["avgFPS"])
    latency3 = []
    t3 = []
    imgGr = [] # Grouped frames by actions
    imgDiff = [] # Difference between consecutives frames
    for i in range(len(indexs)):
        fI = indexs[i]
        
        if(i == len(indexs) -1):
            (data,df) = imgChange2(img[fI:], imgt[fI:])
        else:
            (data,df) = imgChange2(img[fI:indexs[i+1]], imgt[fI:indexs[i+1]])

        imgGr.append(data)
        imgDiff.append(df)
    t3 = []
    # Calculate latency
    for x in range(len(times)):
        try:
            latency3.append(imgGr[x][0][0]*delta)
            t3.append(times[x] + imgGr[x][0][0]*delta)
        except:
            latency3.append(-1)
            t3.append(-1) 
    
    return {'mouse':times.tolist(),'latency1':latency.tolist(), 't1': t1, 't2': t2, 't3':t3 ,'latency2':latency2, 'latency3':latency3}

def getStalls(name,fps,q = None):

    # Load data
    (img,imgt) = loadData(name)
    info = getFPS(imgt)
    if(info['avgFPS'] > fps):
        (img,imgt) = diemadoFPS2(name,fps)
    iRes = imgFreeze(img,imgt)
    del img
    
    iC = np.asarray(iRes) # Relevant Information
    info = getFPS(imgt)
    #print(iC)
    res = dict()
    res['numberStalls'] = iC.shape[0]
    res['numberTotalFrames'] = imgt.size
    try:
        res['stallDuration'] = (iC[:,3] - iC[:,2]).tolist()
        res['stallNFrames'] = ((iC[:,1] - iC[:,0]).astype('int32')).tolist()
        res['stallIFrame'] = (iC[:,0].astype('int32')).tolist()
        res['stallLFrame'] = (iC[:,1].astype('int32')).tolist()
        res['stallInit'] = iC[:,2].tolist()
        res['stallTotalTime'] = np.sum(iC[:,3] - iC[:,2])
        res['freezePercent'] = res['stallTotalTime'] /info['time']
    except:
        print("No freeze has occured")
        res['stallDuration'] = []
        res['stallNFrames'] = []
        res['stallIFrame'] = []
        res['stallLFrame'] = []
        res['stallInit'] = []
        res['stallTotalTime'] = 0
        res['freezePercent'] = 0
    del iC
    if (q != None):
        q.put(res)
    return res

def getSummaryLatency(data):
    # Delete negative values
    try:
        ndata = data[data>0]
        avg = np.sum(ndata)/ndata.size
        maxV = np.max(ndata)
        minV = np.min(ndata)
        percent25 = np.percentile(ndata, 25, axis = 0)
        percent50 = np.percentile(ndata,50,axis = 0)
        percent75 = np.percentile(ndata,75,axis=0)
        
    except:
        minV = 0
        maxV = 0
        avg = 0
        percent25 = 0
        percent75 = 0
        percent50 = 0
    res = {'min':minV, 'max':maxV,'avg':avg,'percent25':percent25,'percent50':percent50, 'percent75':percent75}
    return res
#gettingFramesDemo(20)


def getFPS(t):
    dT = []
    for x in range (1,t.size):
        dT.append(t[x]-t[x-1])
    #plotDataDistribution(dT)
    dT2 = np.asarray(dT)
    res = dict()
    res['avgFPS'] = round(t.size/(t[t.size-1]-t[0]))
    res['avgDeltaFrame'] = np.sum(dT2)/dT2.size
    res['time'] = t[t.size-1] - t[0]
    res['nFrames'] = t.size
    return res


def getDeltaTime(fps):
    return 1/fps

def normalizedDeltaFrames(name):
    imgt = np.load(name+'_timestamp.npy')
    fpsInfo = getFPS(imgt)
    targetDelta = fpsInfo['avgFPS']
    nT = [imgt[0]]
    for x in range(1,imgt.size):
        vT = nT[len(nT)-1] + fpsInfo['avgDeltaFrame']
        nT.append(vT)
    np.save(name +'_timestampN.npy',np.asarray(nT))
    #return np.asarray(nT)

def diemadoFPS(name,targetFPS):
    (img,imgt) = loadData(name)    
    currentFPS = getFPS(imgt)['avgFPS']
    targetDelta = getDeltaTime(targetFPS)
    if(currentFPS > targetFPS):
        img = np.load(name+'_images.npy')
        index2del = []
        indexI = 0
        for x in range(1,imgt.size):
            if (imgt[x] - imgt[indexI] < targetDelta):
                index2del.append(x)
            else:
                indexI = x
        
        #print(index2del)
        img2 = np.delete(img,index2del,0)
        imgt2 = np.delete(imgt,index2del)

        print(getFPS(imgt2))

        return (img2,imgt2)
    else:
        print("Diemado can't be done --> CurrentFPS is greater than targetFPS")
        return (img,imgt)

def diemadoFPS2(name,targetFPS):
    (img,imgt) = loadData(name)    
    info= getFPS(imgt)
    duration = info['time']
    
    targetNumberFrames = round(duration * targetFPS)
    im = np.asarray(imgt)
    
    deltas = np.asarray(getDeltas(imgt))
    
    pFrames = targetNumberFrames/info["nFrames"] * 100
    percent = 100 - pFrames
    
    th = np.percentile(deltas,percent)
    
    index2del = []
    for x in range(1,imgt.size):
        dif = imgt[x] - imgt[x-1]
        if (dif< th):
            index2del.append(x)
       
        #print(index2del)
    img2 = np.delete(img,index2del,0)
    imgt2 = np.delete(imgt,index2del)
    
    return (img2,imgt2)


