# import iperf3


import argparse

import multiprocessing
from videoCapturing.imageCapture import *
from utils.utils import *


from cloudGaming.Moonlight.moonlight import *
from cloudGaming.Moonlight.LOL import *

from cloudGaming.Moonlight.KQI_extraction import *

import argparse

def parseArgs(parser):
    # Add long and short argument
    parser.add_argument("--niter", "-n", help="number of Iterations")
    parser.add_argument("--output","-o", help="file to save results")
    parser.add_argument("--resolution", "-r", help = "resolution for the video")
    parser.add_argument("--framerate", "-d", help = "duration of the video")

    parser.add_argument("--verbose", "-v")

    # Read arguments from the command line
    args = parser.parse_args()

    arg = dict()
    # Default values
    arg["nIter"]= 1
    arg["file2Save"] = "./default.json"
    arg["resolution"] = "1080p"
    arg["framerate"] = "60"
    arg["verbose"] = False
    # Check for --width
    if args.niter:
	    arg["nIter"] = int(args.niter)

    if args.output:
        arg["file2Save"] = "./" + args.output

    if args.framerate:
        arg["framerate"] = int(args.framerate)

    if args.resolution:
        arg["resolution"] = args.resolution

    if args.verbose:
        arg["verbose"] = args.verbose
        #print("Verbose enable")

    return arg





if __name__=='__main__':

    # Initiate the parser
    parser = argparse.ArgumentParser()
    args = parseArgs(parser)

    mov = dict()
    mov['repetitions'] = 5
    mov['dMove'] = 4
    mov['coordinates'] = {'x': 0.6, 'y': 0.35}


    ping = [
        {"ip": "8.8.8.8", "label":"Ping_DNS", "packetSize":80, "nPackets":10},
        {"ip": "192.168.159.201", "label": "Ping_Server", "packetSize": 80, "nPackets": 10}
    ]


    #moonlight = Moonlight(coordinatesFile="cloudGaming/Moonlight/coordinates/client_conf_labMSI4K.json/")
    moonlight = Moonlight()
    rmLol = remoteLOL(ip="192.168.159.201", port = "5000")


    ext = CG_KQI_extraction(moonlight=moonlight, remoteLol=rmLol)


    host = multiprocessing.Process(target= rmLol.prepareGame, args=())

    host.start()

    moonlight.conf_Moonlight(resolution= args["resolution"], framerate = args["framerate"])

    host.join()
    kqis = []
    tI = time.time()
    for x in range(args["nIter"]):
        print("iteration " + str(x))

        ##################################################################################
        # TODO: CPE metrics
        # TODO: Crowd metrics
        ##################################################################################

        (kqi, ping_results) = ext.experiment(pos= mov, serverTest = True, pings = ping)
        kqis.append(kqi)
        print("CG latency --> " + str(kqi["cg_latency50Percent"]))
        print("Client latency --> " + str(kqi["client_latency50Percent"]))
        print("Host latency --> " + str(kqi["host_latency50Percent"]))
        #print(ping_results)

        ##################################################################################
        # TODO: CPE metrics
        # TODO: Crowd metrics
        ##################################################################################

    tE = time.time()
    print("Time taken (seconds) -->" + str(tE - tI))




    #rmLol.quitGame()

    with open(args["file2Save"], 'w') as outfile:
        print(kqis)
        json.dump(kqis, outfile, indent=6)





