from utils import *
from network.CPE.CPE import *
from network.CrowdCell.remoteCrowd5G import *
#print(ping("8.8.8.8",4))
#
#cpe = CPE(ip="192.168.8.1", password="areyouready?1")
#kpi = cpe.deviceSignal().to_dict('records')[0]
#kpi = cpe.deviceSignal()
#print(kpi)

#kpi = cpe.get_traffic_stats()

#print(kpi)

print("···················································")

#crowd = remoteCrowd("192.168.192.160", "5000")


#stats = crowd.get_stats()  # Reset cell stats

#stats = crowd.get_log()
#print(stats)

#stats = crowd.cell_config_LTE("enb")

#stats = crowd.get_cellConfig("enb")

#print(stats)
#stats2 = crowd.get_stats()
#print(stats2)

import subprocess

## call date command ##
import os
from network.CrowdCell.remoteCrowd5G import *




def sendNotification_telegram(message):
    # Bot token
    TOKEN = "6178152957:AAHohcK3zHu2i50mBtbgt38zEvuT0Ym6Oe8"
    # URL
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

    # Get chat info
    #print(requests.get(url).json())

    # ID chat
    chat_id = "216201786"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json()) # this sends the message





niter = 20
duration = 60
videoID = 3

videos = [3,4]
RESOLUTIONS = ["Auto","4K", "1440p", "1080p", "720p"]
#RESOLUTIONS =["1080p"]


prbs = [5,10,15,20,25,30,35,40,45,50, 55, 60, 65, 70,75, 100]

#prbs = [10,15,20,25,30,35,40,45,50, 55, 60, 65, 70,75, 100]
prbs = [25,50,75,100]
crowd = remoteCrowd("192.168.192.160", "5000")


params = dict()
params["cells"] = dict()

cfg = dict()
#cfg["pdsch_mcs"] = 28
cfg["pdsch_fixed_rb_alloc"] = True
cfg["pdsch_fixed_rb_start"] = 0
cfg["pdsch_fixed_l_crb"] = 100
params["cells"]["1"] = cfg


noise_level = [-5]
gains = [0, -10, -20]
crowdt = False
if crowdt:
    #gains = [-20]

    #crowd.noise_level(-30)
    for gain in gains:
        crowd.cell_gain(cell_id=0, gain=gain)
    #for noise in noise_level:
    #     crowd.noise_level(noise)
        for prb in prbs:
            params["cells"]["1"]["pdsch_fixed_l_crb"] = prb
            #crowd.set_config_live(params)
            for r in RESOLUTIONS:
            #output_pattern = "test_5G_PRB" + str(prb) + "_noise" + str(noise) + "_28mcs_videoID4_auto.json"
                #output_pattern = "test_5G_PRB" + str(prb) + "_gain" + str(gain) +"_" + str(mcs) + "mcs_videoID4_auto.json"
                # output_pattern = "test_5G_PRB" + str(prb) + "_gain" + str(gain) + "_videoID" + str(videoID)+ "_resolution"+ str(r) + ".json"

                #output_pattern = "test_5GNSA_videoID_"+str(videoID)+"_resolution_"+str(r) + "_gain_" + str(gain) + "_PRB_" + str(prb) + ".json"
                output_pattern = "test_LTE_PRB_"+str(prb)+ "_gain"+str(gain) +"_videoID"+str(videoID) + "_"+str(r)+".json"
                cmd = "python main_crowdcell.py --niter " + str(niter) + " --videoID "+ str(videoID) + " --resolution " + r + " --duration " + str(duration) + " --output \"" + output_pattern + "\""
                sendNotification_telegram("Starting " + cmd)
                os.system(cmd)

else:

    for vID in videos:
        for r in RESOLUTIONS:
            if r == "Auto":
                niter = 20
            else:
                niter = 20
            output_pattern = "test_WIFI_videoID"+str(vID)+"_"+str(r)+".json"
            cmd = "python main_crowdcell.py --niter " + str(niter) + " --videoID " + str(
                vID) + " --resolution " + r + " --duration " + str(
                duration) + " --output \"" + output_pattern + "\""
            sendNotification_telegram("Starting " + cmd)
            os.system(cmd)

sendNotification_telegram("Measures campaign has ended!")