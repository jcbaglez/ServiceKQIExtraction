
from monitorProcess import *
import signal
import threading
import pickle
from progress.spinner import MoonSpinner
from datetime import datetime
import json
def saveResults(file2Save, kqis):
    print("Saving results")
    try:
        #with open(path2Save + '/kqi.json','w') as outfile:
        with open(file2Save,'w') as outfile:
            json.dump(kqis,outfile,indent = 6)
        print("Results have been saved in " + file2Save)
    except:
        print("Something wrong, file can not be saved")
        traceback.print_exc()
        pickle.dump(kqis,open("backfileMonitoring.asv", "wb"))


def handler(signum,frame):
    msg = "\nFinishing script"
    print(msg)
    global terminator
    terminator = True


if __name__ == "__main__":
    global terminator
    terminator = False

    signal.signal(signal.SIGINT,handler)
    # count = 0
    #p = monitorProcess("lte-")
    p = monitorProcess("all")
    t = threading.Thread(target=p.run)
    t.start()

    with MoonSpinner("Processing...") as bar:

        while not terminator:
            time.sleep(0.02)
            bar.next()

    # Stop system monitoring
    p.terminate()
    t.join()

    filename = datetime.now().strftime("%Y%m%d_%H%M") + "_processMonitoring.json"

    print(p.data)
    saveResults(filename,p.data)