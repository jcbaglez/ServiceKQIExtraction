
##################################################################################################
#                                           IMPORTS
##################################################################################################
# Python libraries
from subprocess import check_output, CalledProcessError
from multiprocessing import Process, Manager
import json
import time
import platform
import traceback
import datetime
import os
import multiprocessing
import os
import argparse
# Network
from network.CrowdCell.remoteCrowd import *
from network.CPE.CPE import *
from network.HuaweiE3372.STICK import *
# Gaming
from cloudGaming.Moonlight.Macro import MacroLoL
from cloudGaming.Moonlight.metricas_fich import LogMetrics
# Others
from utils.utils import *




# Gaming imports
#import mouse
#import pyautogui



##################################################################################################
#                                           FUNCTIONS
##################################################################################################
def getRadioKPI():
    try:
        kpi = json.loads(getFromConsole("python userKPI.py"))
    except:
        kpi = dict()
        kpi["RSRP"] = 0
        kpi["RSRQ"] = 0
        kpi["RSSI"] = 0
        kpi["SINR"] = 0
        kpi["PCI"] = 0
    finally:
        return kpi

def testChannel():
    q = multiprocessing.Queue()
    ip = "192.168.0.101"
    port = 5002
    test = multiprocessing.Process(target = tcpTest, args = (ip,port, 5, 10, 32768, "tcpTest.txt",q,))
    #res = tcpTest("192.168.0.102", 5002, 10, 32768, "tcpTest.txt")
    #print(res)
    test.start()
    t = time.time() + 20
    while(time.time() < t):
        if (not test.is_alive()):
            break
        #print("TCP test is doing")

    if(test.is_alive()):
        test.terminate()
        print("TCP Test timeout has expired")
        res['TCP_BW_Receiver'] = 0
        res['TCP_BW_Sender'] = 0
        
    else:
        print("Getting TCP test results")
        res = q.get()
    
    test = multiprocessing.Process(target = udpTest, args = (ip, port, 5, "udpTest.txt",q,))
    test.start()
    t = time.time() + 30
    while(time.time() < t):
        if (not test.is_alive()):
            break
    if(test.is_alive()):
        test.terminate()
        print("UDP Test timeout has expired")
        res['UDP_duration'] = 0
        res['UDP_tam'] = 0
        res['UDP_BW'] = 0
        res['UDP_jitter'] = 0
        res['UDP_lost'] = 0
        res['UDP_totalDatagram'] = 0
        res['UDP_lossPercent'] = 0
    else:
        print("Getting UDP test results")
        res.update(q.get())
    
    
    
    #res.update(udpTest("192.168.0.102", 5002, "udpTest.txt"))
    return res
def moonlightServiceETH(service,allMeas = True):
    try:
        #print("Iteration " + str(i))
        timestamp = time.time()
        kqi = dict()
        #kqi = service.experimentETH(mov)
        kqi = service.experimentETH(mov,allMeas)
        #print(kqi)
        # if (time.time() > iterInitTime + 2700):
        #     service.quitGame()
        #     time.sleep(5)
        #     iterInitTime = service.startConfiguration()
    except:
        #print("Error in Iteration "+ str(i))
        traceback.print_exc()

        # with open(path2Save + 'dataBackup.json','w')as outfile:
        #     json.dump(kqis,outfile,indent=6)

    #kqi.update(testChannel())
    return kqi
def moonlightService(service,allMeas,isCrowd):
    try:
        #print("Iteration " + str(i))
        timestamp = time.time()
        kqi = dict()
        kqi = service.experimentCrowd(mov,allMeas)
        #kqi = service.experiment3(mov,allMeas,isCrowd)
        #print(kqi)
        # if (time.time() > iterInitTime + 2700):
        #     service.quitGame()
        #     time.sleep(5)
        #     iterInitTime = service.startConfiguration()
    except:
        #print("Error in Iteration "+ str(i))
        traceback.print_exc()

        # with open(path2Save + 'dataBackup.json','w')as outfile:
        #     json.dump(kqis,outfile,indent=6)

    #kqi.update(testChannel())
    return kqi
def serverPrepare():
    #base = "http://192.168.0.101:5000"
    base = "http://10.147.17.239:5000"
    header =  {'content-type' : 'application/json'}
    url = "/action/keyboard"
    d = dict()
    d['action'] = ["control+shift+i","shift+h", "y"]
    r = requests.post(base+url, data = json.dumps([d]), headers = header)



def getNumberConsecutiveValues(data,keys):
    nC = 1
    for x in data.keys():
        if(x not in keys):
            nC = nC*len(data[x])
    return nC


def getNumberCombinations(data):
    nC = 1
    for x in data.keys():
        nC = nC*len(data[x])
    return nC

def sortKeys(data,sKeys):
    if (sKeys is None):
            sKeys = []
            for key in data.keys():
                sKeys.append(key)
    elif (len(sKeys) < len(data.keys())):
        for key in data.keys():
            if (key not in sKeys):
                sKeys.append(key)
    return sKeys

def combineConfiguration(data,sKeys=None):
    nC = getNumberCombinations(data)

    nStep = []
    aux = []
    lC = []
    sKeys = sortKeys(data,sKeys)


    for key in sKeys:
        aux.append(key)
        nStep.append(getNumberConsecutiveValues(data,aux))


    for index in range (0,len(sKeys)):
        nS = nStep[index]
        nRep = (nC/nS)/ len(data[sKeys[index]])
        cont = 0
        for rep in range(0,int(nRep)):
            for val in data[sKeys[index]]:
                for v in range(0,nS):
                    if index == 0:
                        d = dict()
                        for k in sKeys:
                            if (k == sKeys[index]):
                                d[k] = val
                            else:
                                d[k] = None
                        lC.append(d)
                    else:
                        lC[cont][sKeys[index]] = val
                        cont +=1

    return lC


def displayExecutionTime(initTime,endTime):
    seconds = int(endTime - initTime)
    minutes = seconds/60
    hours = minutes/60
    days = hours/24
    print("Seconds:" + str(seconds))
    print("Min:" + str(minutes))
    print("Hours:" + str(hours))
    print("Days:" + str(days))

##################################################################################################
#                                   TESTBED CONFIGURATION
##################################################################################################
topFolder = "LTE_G30_N30"
# Display results in command
displayResults = False

# Number of experiment for each configuration
nIter = 10

# Connection (0 --> Ethernet/WiFI, 1 --> CrowdCell, 3 --> Test)
connectionType = 0


# CrowdCell configuration (Only requires if connectionType is set to 1)
if (connectionType == 1):

    combination = True

    conf = dict()
    
    if combination:
        # Radio bandwidth
        #conf['n_rb_dl'] = [25, 50, 75, 100]
        conf['n_rb_dl'] = [100]
        # Antennas' gain
        conf['gain'] = [0]

        # Channel simulator configuration
        conf['snr'] = [30]

        # Transmission Mode
        conf['transmission_mode'] = [4]


        # Sort values
        #sortValues = ['tx_mode','n_rb_dl','gain','snr']
        sortValues = ['n_rb_dl','gain','snr','transmission_mode']
        crowdCellConfiguration = pd.DataFrame(combineConfiguration(conf,sortValues))

    else:
        n_elems = 2
        ruido = np.ones(n_elems)*30
        bw = np.ones(n_elems)*50
        bw[1] = 75
        c = dict()
        c['snr'] = ruido
        c['n_rb_dl'] = bw
        crowdCellConfiguration = pd.DataFrame(c)
##################################################################################################
#                                   MOONLIGHT CONFIGURATION
##################################################################################################
# Service type (only for information in logs)
serviceType = "Cloud Gaming"

# Game
game = 'LoL'
#
allMeas = True
# Moves
mov = dict()
mov['repetitions'] = 5
mov['dMove'] = 4
mov['coordinates'] = {'x':0.6, 'y':0.35}

# Server address
#sIP = "192.168.0.101"
#sIP = "10.147.17.239" # Torre Carlos
#sIP = "10.147.17.25"
sIP = "192.168.192.201"
#sIP = "192.168.8.105"
sPort = 5000

sConf = dict()
# Resolution of the session
#sConf['resolution'] = ['720p','1080p','1440p','4K']
sConf['resolution'] = ['1440p']
# Bitrate of the session
sConf['bitrate'] = ['Automatic']
#sConf['bitrate'] = ["150 mbps"]
# Frames per seconds of the session
#sConf['fps'] = ['30FPS','60FPS']
sConf['fps'] = [30,60,120]
# Type of audio
sConf['audio'] = ['Stereo']

# Decoder type (Automatic_decoder, Software_decoding, Hardware_decoding)
sConf['decoder'] = ['Hardware_decoding',]

# Codec type (Automatic, H.264, H.265, HDR)
sConf['codec'] = ['H.264']






##################################################################################################
#                                           MAIN
##################################################################################################
if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--resolution", help = "Session Resolution")
    parser.add_argument("-f", "--framerate", help = "Session Frame Rate")
    parser.add_argument("-n", "--network", help = "Network Link to check (Ethernet, WiFi, CPE, CrowdCell")
    parser.add_argument("-d", "--directory", help="Directory to save results")
    args = parser.parse_args()

    if(args.resolution is not None):
        if(args.resolution in ["720p", "1080p", "1440p", "4K"]):
            sConf['resolution'] = [args.resolution]

    if(args.framerate is not None):
        if(args.framerate in ["30", "60", "120"]):
            sConf['fps'] = [int(args.framerate)]
        elif (args.framerate == "all"):
            sConf['fps'] = [30,60,120]

    if(args.network is not None):
        if(args.network == "Ethernet" or args.network == "WiFi"):
            connectionType = 0
        elif(args.network == "CrowdCell"):
            connectionType = 1
        elif(args.network == "CPE"):
            connectionType == 2


    # Make a directory with results
    if (os.path.exists ("results") == False):
        os.mkdir("results")


    dirL = "./results/"
    if args.directory is not None:
        dirs = args.directory.split("/")

        for dir in dirs:
            if (dir != "" and dir != "results"):
                dirL += dir +"/"
                print(dirL)
                if (os.path.exists (dirL) == False):
                    os.mkdir(dirL)

    #folderName = sConf['resolution'][0]+ "_" + str(sConf['fps'][0])

    folderName = sConf['resolution'][0]

    date = datetime.datetime.now()
    dirname = date.strftime("%d_%m_%Y_%H_%M")
    path2Save = dirL + folderName+"_"+dirname
    #path2Save = "results/"+folderName+"_"+dirname
    try:
        os.mkdir(path2Save)
    except Exception:
        traceback.print_exc()

    print(sConf["resolution"])
    print(sConf["fps"])
    print(connectionType)
    moonlightConfiguration = combineConfiguration(sConf)
    print(moonlightConfiguration)

    initTime = time.time()
    ############################### Preambles #########################################

    pathMoonlight = "C:/Program Files/Moonlight Game Streaming/Moonlight.exe"
    service = MacroLoL(game,pathMoonlight,sIP,sPort) # Moonlight instance

    crowd = remoteCrowd("10.147.17.51", "5000")
    #ltestick = HuaweiE3372()

        
    #path2Save = base+folderName+"/"+dirname

    resultado = []
    resultadoBack = []
    kqis = []

    try:
        if (connectionType == 0): # Ethernet/WiFi
            kqis = []
            for mConfig in moonlightConfiguration:
                rM = multiprocessing.Process(target = service.startConfiguration,args=())
                rM.start()
                # Configure Moonlight
                service.conf_service(mConfig)
                # Start Moonlight
                #service.startConfiguration()
                rM.join()
                for i in range(nIter):
                    print("Iteration  ", i)
                    tI = time.time()
                    kqi = moonlightServiceETH(service,allMeas)
                    tE = time.time()

                    print("Time taken (seconds) --> " + str(tE - tI))
                    print(kqi)
                    #kqi = moonlightService(service,allMeas,False)
                    kqis.append(kqi)
                #service.quitGame()
                # if (time.time() > iterInitTime + 2700):
                #     service.quitGame()
                #     time.sleep(5)
                #     iterInitTime = service.startConfiguration()
            service.quitGame()
        elif (connectionType == 1): # CrowdCell
            print("CrowdCell")
            kpis = []
            ueStats = []
            confs = []
            cellStats = []
            allM = []
            #stick = STICK(user="admin", password="admin")
            #cpe = CPE(password="admin2020?")
            cpe = STICK(user="admin", password="admin")
            rM = multiprocessing.Process(target=service.startConfiguration, args=())
            rM.start()
            for mConfig in moonlightConfiguration:

                    # Configure Moonlight
                service.conf_service(mConfig)
                    # Start Moonlight
                    #service.startConfiguration()
                rM.join()
                for x in range(nIter):

                        #getFromConsole("python routes.py") # Set routing table
                    print("Iteration " + str(x))
                    timestamp = time.time()

                    configuration = crowd.cell_config2()
                    stats = crowd.stats() # Reset cell stats
                    #cpe = CPE(password="areyouready?1")
                    #cpe = CPE(password="admin2020?")
                    cpe = STICK(user = "admin", password="admin")
                    cpe.clear_stats()
                    kpi = cpe.deviceSignal().to_dict('records')[0]

                        #kpi = getRadioKPI()
                        
                    kpis.append(kpi)
                        # Service
                        #kqi = moonlightService(service, allMeas)
                    kqi = moonlightService(service,allMeas,True)
                        # Get data
                    kqis.append(kqi)
                    ue_stats = crowd.ue_enb_stats()
                    stats = crowd.stats()
                        #cellStats.append(stats)
                    ress = dict()
                    ress = configuration
                       
                    ress.update(ue_stats)
                    ress.update(stats)
                    ress.update(kpi)
                    ress.update(kqi)

                    allM.append(ress)

            service.quitGame()
        elif(connectionType == 2):
            print("CPE")
            kpis = []


            allM = []
            #cpe = CPE(password="areyouready?1")
            #cpe = CPE(password="admin2020?")
            rM = multiprocessing.Process(target=service.startConfiguration, args=())
            rM.start()
            for mConfig in moonlightConfiguration:

                # Configure Moonlight
                service.conf_service(mConfig)
                # Start Moonlight
                # service.startConfiguration()
                rM.join()
                for x in range(nIter):
                    getFromConsole("python routes.py")  # Set routing table
                    print("Iteration " + str(x))
                    timestamp = time.time()
                    #cpe = CPE(password="areyouready?1")
                    #cpe = CPE(password="admin2020?")
                    #cpe.clear_stats()
                    #kpi = cpe.deviceSignal().to_dict('records')[0]

                    #kpis.append(kpi)
                    # Service
                    # kqi = moonlightService(service, allMeas)
                    kqi = moonlightServiceETH(service, allMeas)
                    #kpi.update(cpe.get_traffic_stats().to_dict('records')[0])
                    # Get data
                    kqis.append(kqi)

                    # cellStats.append(stats)
                    #kqi.update(kpi)
                    allM.append(kqi)

            service.quitGame()
        elif(connectionType == 3): # Test
            print("TEST")
            #service.sendMouseAction(600,100, 'rightClick')
            res = testChannel()
            print(res)
    except:
        print("something wrong")
        traceback.print_exc()
    finally:
        try:
            with open(path2Save + '/kqi.json','w') as outfile:
                print(kqis)
                json.dump(kqis, outfile, indent = 6)

        except:
            print("kqi File can't be saved")
            traceback.print_exc()
        try:
            with open(path2Save + '/allData.json','w') as outfile:
                json.dump(allM,outfile, indent = 6)
        
        except:
            print("Files can't be saved")
    endTime = time.time()

    displayExecutionTime(initTime,endTime)
