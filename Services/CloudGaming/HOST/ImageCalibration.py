import keyboard
import mouse
import time
import os
import json
from utils import *
from pynput.mouse import Button, Controller

def calibration(top,left,width,height):
    mon = {"top":top, "left":left, "width":width, "height":height}
    sct = mss.mss()
    return np.asarray(sct.grab(mon))
def gettingFrames_2(t):
    mon = {"top":150, "left":450, "width": 300, "height":300}
    sct = mss.mss()
    imgAux = np.asarray(sct.grab(mon))
    array = []
    times=[]
    initTime = time.time()
    title = "Image Calibration"
    while(initTime + t > time.time() ):
        img = np.asarray(sct.grab(mon))
        #print('loop took {} seconds'.format(time.time()-last_time))
        times.append(time.time())
        array.append(img)
        #fps +=1
        cv2.imshow(title, img)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break
    return img
    #np.save('data2',np.asarray(array))
    #np.save('time2',np.asarray(times))
        #print(previous_time)
    #print(initTime+t - previous_time)
    #print("Average FPS option 1", fps/t)


#print(calibration(200,500,400,400))
i = gettingFrames_2(20)
cv2.imshow("Test",i)

time.sleep(60)
