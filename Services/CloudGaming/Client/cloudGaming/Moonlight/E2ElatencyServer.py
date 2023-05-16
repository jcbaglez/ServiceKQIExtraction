import time

import mouse as mouse
#import pyautogui
from utils.utils import *
import threading
import multiprocessing
import numpy as np
import json
def imgChange(img,t):
    th = 0.75*img[0].size
    fI = -1
    fE = -1
    tI = -1
    tE = -1
    imgDif = []
    data = []
    for i in range (1,img.shape[0]):
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


def deltaFrame2(data):
    ff = -1
    newData = []
    print(data.shape[0]-1)
    for x in range(0,data.shape[0]-1):
        aux = data[x+1,0] - data[x,1]
        #print(aux)

        if(aux <4):
            #print("numbers:",data[x-1,1],",",data[x,0])
            if (ff == -1):
                if (x == data.shape[0]-2):
                    newData.append([data[x][0],data[x][1],data[x][2],data[x][3],data[x][3]-data[x][2]])
                    #newData.append([data[x].tolist(),data[x][3]-data[x][2]])
                    print("point1")
                else:
                    ff = x
            elif(x== data.shape[0]-2):
                print("point2")
                newData.append([data[ff,0],data[x+1,1],data[ff,2],data[x+1,3],data[x+1,3]-data[ff,2]])
        else:
            if (ff != -1):
                newData.append([data[ff,0],data[x,1],data[ff,2],data[x,3],data[x,3]-data[ff,2]])
                ff = -1
            else:
                newData.append([data[x][0],data[x][1],data[x][2],data[x][3],data[x][3]-data[x][2]])
                #newData.append([data[x][.tolist()],data[x][3]-data[x][2]])

    return newData

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


# Load data
img = np.load('data2.npy')
imgt = np.load('time2.npy')

iRes = imgChange(img,imgt)
iC = np.asarray(iRes[0]) # Relevant Information
iCh = np.asarray(iRes[1]) # Number of pixel

imgGroup = np.asarray(deltaFrame2(iC))
res = []
names = ['FirstFrame','LastFrame','InitTime','EndTime','Duration']
for i in imgGroup:
    res.append(dict(zip(names,i)))
results = json.dumps(res)
print(results)
#groups = takeNElement(mt.size,imgGroup)
