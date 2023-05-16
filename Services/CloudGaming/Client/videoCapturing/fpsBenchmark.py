import time

import cv2
import mss
import numpy as np


def monitorInfo():
    return np.asarray(mss.mss().monitors)


def fpsMonitor(t=10):
    monitor = monitorInfo()[1]  # Monitor information
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
        img = np.asarray(aux)
        # img = np.asarray(sct.grab(mon)) # Take screenshot
        times.append(time.time())  # Add timestamp to the list
        array.append(np.asarray(aux))  # Add screenshot to the list
        fps += 1
            # if(showImages):
            #     cv2.imshow(title, img) # Show image
            #     if cv2.waitKey(25) & 0xFF == ord("q"):
            #         cv2.destroyAllWindows()
            #         break

    print("Average FPS: ", fps / t)
    return fps/t

def screen_record():
    try:
        from PIL import ImageGrab
    except ImportError:
        return 0

    # 800x600 windowed mode
    mon = (0, 40, 800, 640)

    title = "[PIL.ImageGrab] FPS benchmark"
    fps = 0
    last_time = time.time()

    while time.time() - last_time < 1:
        img = numpy.asarray(ImageGrab.grab(bbox=mon))
        fps += 1

        cv2.imshow(title, cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

    return fps


def screen_record_efficient():
    # 800x600 windowed mode
    monitor = monitorInfo()[1]  # Monitor information
    mLeft = int(monitor['width'] * 0.36) + monitor['left']
    mTop = int(monitor['height'] * 0.13) + monitor['top']
    mon = {"top": mTop, "left": mLeft, "width": 400, "height": 400}  # Area of recording
    #mon = {"top": 40, "left": 0, "width": 800, "height": 640}

    title = "[MSS] FPS benchmark"
    fps = 0
    sct = mss.mss()
    last_time = time.time()

    while time.time() - last_time < 1:
        img = np.asarray(sct.grab(mon))
        fps += 1

        cv2.imshow(title, img)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

    return fps

#print("PIL:", screen_record())
#print("MSS:", screen_record_efficient())
print(fpsMonitor())