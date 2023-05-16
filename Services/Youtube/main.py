from youtube import YouTube
from monitorSystem import *
from monitorProcess import *
import json
import time
import traceback
from pyvirtualdisplay import Display
import argparse
import pickle
import requests
from utils import *
import os
import multiprocessing
from threading import Thread
from network.CPE.CPE import *
from network.CrowdCell.remoteCrowd5G import *

def parseArgs(parser):
    # Add long and short argument
    parser.add_argument("--niter", "-n", help="number of Iterations")
    parser.add_argument("--output","-o", help="file to save results")
    parser.add_argument("--resolution", "-r", help = "resolution for the video")
    parser.add_argument("--duration", "-d", help = "duration of the video")
    parser.add_argument("--virtualDisplay", "-V", help = "Enable virtual display (True by default)")
    parser.add_argument("--videoID", help = "Video Index in the provided list")
    parser.add_argument("--url", help = "URL of the video to play")
    parser.add_argument("--ping", help = "Enable ping test (default: True)")
    parser.add_argument("--verbose", "-v")

    # Read arguments from the command line
    args = parser.parse_args()

    arg = dict()
    # Default values
    arg["nIter"]= 1
    arg["file2Save"] = "./results/default.json"
    arg["duration"] = 60
    arg["resolution"] = "Auto"
    arg["virtualDisplay"] = True
    arg["videoID"] = 0
    arg["verbose"] = False
    arg["ping"] = True
    # Check for --width
    if args.niter:
	    arg["nIter"] = int(args.niter)

    if args.output:
        arg["file2Save"] = "results/" + args.output

    if args.duration:
        arg["duration"] = int(args.duration)

    if args.resolution:
        arg["resolution"] = args.resolution

    if args.virtualDisplay:

        arg["virtualDisplay"] = args.virtualDisplay == "True"

    if args.videoID:
        arg["videoID"] = int(args.videoID)
    if args.verbose:
        arg["verbose"] = args.verbose
        #print("Verbose enable")

    if args.url:
        arg["url"] = args.url

    if args.ping:
        arg["ping"] = args.ping
    return arg




def saveResults(file2Save, kqis):
    print("Saving results -->" + file2Save)
    try:
        #with open(path2Save + '/kqi.json','w') as outfile:
        with open(file2Save,'w') as outfile:
            json.dump(kqis,outfile,indent = 6)
    except:
        print("Something wrong, file can not be saved")
        traceback.print_exc()
        pickle.dump(kqis,open("backfileResults.asv", "wb"))



with open("./videoPool.json", encoding="utf-8") as videofile:
    video = json.load(videofile)

if __name__ == "__main__":

    CPE_ip = None

    service = dict()
    service["type"] = list()
    service["platform"] = list()
    service["metrics"] = list()

    network = dict()
    network["cellstats"] = list()
    network["ueStats"] = list()

    netAdapter = dict()
    netAdapter["stats"] = list()
    netAdapter["radioKPI"] = list()
    netAdapter["stats_"] = list()
    netAdapter["radioKPI_"] = list()

    pingTest = dict()
    pingTest["ping_dns"] = list()
    pingTest["ping_dns_"] = list()
    pingTest["ping_youtube_"] = list()

####################################
    # Initiate the parser
    parser = argparse.ArgumentParser()
    args = parseArgs(parser)

###################  PREAMBLE #########################
    networkAdapter = "WIFI"
    CROWD = False

    # Start virtual display if enabled
    if args["virtualDisplay"] and platform.find("linux") != -1:
        display = Display(visible=0, size=(3840, 2160))
        display.start()



     # CPE initialization
    if networkAdapter == "CPE":
        try:
            cpe = CPE(ip="192.168.8.1", password="areyouready?1")
        except:
            time.sleep(10)
            cpe = CPE(ip="192.168.8.1", password="areyouready?1")

        CPE_ip = cpe.deviceInformation()["WanIPAddress"]

    # CROWD initialization
    if CROWD:
        try:
            crowd = remoteCrowd("192.168.192.160", "5000")
            crowd.ue_enb_stats()  # Reset ue stats
            crowd.cell_stats() # Reset cell stat
        except:
            time.sleep(10)
            crowd = remoteCrowd("192.168.192.160", "5000")
            crowd.ue_enb_stats()  # Reset ue stats
            crowd.cell_stats() # Reset cell stat

    for x in range(args['nIter']):

        if args["ping"]:
            # Initialize dict to save data
            print("Pinging DNS")
            ping_dns = ping(ip="8.8.8.8", nPackets = 5)
            if (not ping_dns["connectivity"]):
                print("No internet connection")
                break
            print("Pinging Youtube")
            ping_youtube = ping(ip="www.youtube.com", nPackets = 5)
            if (not ping_youtube["connectivity"]):
                print("No Internet connection. Check connectivity")

            # # Start system monitoring
            q_dns = multiprocessing.Queue()
            #
            t_ping_dns = Thread(target=ping, args=("8.8.8.8", args["duration"]+5, q_dns))




        ############################ Start Youtube experiment ###################################
        print("Experiment " + str(x))

        if networkAdapter == "CPE":
            try:
                cpe.clear_stats()
                signals = cpe.deviceSignal().to_dict('records')[0]
            except:
                pass

        # Prepare experiment
        #yt = YouTube(video[args["videoID"]], args["duration"], interval= 1, resolution = args["resolution"])
        #yt = YouTube(videoIndex=3, duration=-1, logLevel="debug")
        # yt = YouTube(url = "https://www.youtube.com/watch?v=LXb3EKWsInQ", duration = args["duration"])
        #yt = YouTube(video[x%3], args["duration"], interval = 1, resolution = args["resolution"])
        if "url" in args:
            yt = YouTube(url=args["url"], duration=args["duration"], resolution=args["resolution"])
        else:
            yt = YouTube(videoIndex= args["videoID"] ,duration = args["duration"], resolution=args["resolution"])

        if args["ping"]:
            t_ping_dns.start()

        # Start experiment
        q = multiprocessing.Queue()
        proc = Thread(target=yt.play, kwargs={"queue":q})
        proc.start()

        if networkAdapter == "CPE":
            try:
                CPEresults = cpe.monitoring(thread=proc)
            except:
                traceback.print_exc()
                pass

        proc.join()

        ytb = q.get()
        # End experiment
        yt.quit()

        if CROWD:
            try:
                cellStats = crowd.cell_stats()  # Get stats Crowd
                ueStats = crowd.ue_enb_stats(ip = CPE_ip)
                network["configuration"] = crowd.cell_config("enb")
            except:
                pass





        #########################################################################################



        if args["ping"]:
            t_ping_dns.join()

        if bool(ytb):
            # Add values to the list
            service["metrics"].append(ytb)
            service["type"].append("VOD")
            service["platform"].append("Youtube")

            if CROWD:
                network["cellstats"].append(cellStats)
                network["ueStats"].append(ueStats)

            if networkAdapter == "CPE":
                try:
                    netAdapter["stats_"].append(CPEresults["traffic"])
                    netAdapter["radioKPI_"].append(CPEresults["radio"])
                    netAdapter["stats"].append(CPEresults["avgTraffic"])
                    netAdapter["radioKPI"].append(CPEresults["avgRadio"])
                except:
                    traceback.print_exc()
                    pass
            if args["ping"]:
                pingTest["ping_dns"].append(q_dns.get())
                pingTest["ping_dns_"].append(ping_dns)
                pingTest["ping_youtube_"].append(ping_youtube)





    results = dict()
    results["pingTest"] = pingTest
    results["service"] = service
    results["networkAdapter"] = netAdapter
    results["network"] = network

    saveResults(args['file2Save'], results)
    print("End experiments")



