from monitorProcess import *
from utils import *
import time
import argparse
import pickle
import json
def parseArgs(parser):
    # Add long and short argument
    parser.add_argument("--niter", "-n", help="number of Iterations")
    parser.add_argument("--output","-o", help="file to save results")
    parser.add_argument("--verbose", "-v")

    # Read arguments from the command line
    args = parser.parse_args()

    arg = dict()
    # Default values
    arg["nIter"]= 1
    arg["file2Save"] = "/results/default.json"
    arg["verbose"] = False
    # Check for --width
    if args.niter:
	    arg["nIter"] = int(args.niter)

    if args.output:
        arg["file2Save"] = "results/" + args.output

    if args.verbose:
        arg["verbose"] = args.verbose
        #print("Verbose enable")

    return arg
def saveResults(file2Save, kqis):
    print("Saving results")
    try:
        #with open(path2Save + '/kqi.json','w') as outfile:
        with open(file2Save,'w') as outfile:
            json.dump(kqis,outfile,indent = 6)
    except:
        print("Something wrong, file can not be saved")
        traceback.print_exc()
        pickle.dump(kqis,open("backfileResults.asv", "wb"))

if __name__ == "__main__":
        # Initiate the parser
    parser = argparse.ArgumentParser()
    args = parseArgs(parser)

    ping_v = []

    for x in range (args["nIter"]):
        print("Pinging GTP")
        ping_gtp = ping("172.16.0.1", nPackets = 20)
        if (not ping_gtp["connectivity"]):
            print("GTP connection doesn't work")
            break
        print("Pinging DNS")
        ping_dns = ping(ip="8.8.8.8", nPackets = 20)
        if (not ping_dns["connectivity"]):
            print("No internet connection")
            break
            print("Pinging Youtube")
        ping_youtube = ping(ip="www.youtube.com", nPackets = 20)
        if (not ping_youtube["connectivity"]):
            print("No dns available. Configuring DNS...")
            os.system("sudo echo 'nameserver 8.8.8.8' >> /etc/resolv.conf")
            time.sleep(1)
            print("Trying DNS again...")
            ping_youtube = ping(ip="www.youtube.com")
        if (not ping_youtube["connectivity"]):
            print("Something went wrong with the DNS")
            break

        p_dic = dict()
        p_dic["gtp"] = ping_gtp
        p_dic["dns"] = ping_dns
        p_dic["youtube"] = ping_youtube 
        ping_v.append(p_dic)

    saveResults(args['file2Save'], ping_v)
=======
# p = monitorProcess("lte-softmodem")

# print(p.monitoring())

import psutil

def get_cpu_percent():
    data = dict()

    cpuData = psutil.cpu_percent(percpu=True)
    m = 0
    print(cpuData)
    for ncpu in range(len(cpuData)):
        key = "cpu_percent_" + str(ncpu+1)
        data[key] = cpuData[ncpu]
        m += cpuData[ncpu]

    data["cpu_percent_avg"] = m/len(cpuData)

    return data

p = psutil.Process()



# with p.oneshot():
#     print(p.name())
#     print(p.cpu_times())
processName = "lte-"
# pid = -1
# for proc in psutil.process_iter(["pid", "name"]):
#     #if proc.is_running():
#     #    print(proc)
#     #print(str(proc.info["pid"]) + " - " + proc.info["name"] + " -  " + proc.info["cpu_num"])
#     if proc.info["name"].find(processName) != -1:
        
#         #process.append(psutil.Process(proc.info["pid"]))
#         pr = psutil.Process(proc.info["pid"])
#         pr.children()
        #with pr.oneshot():
        #    print(pr.ppid())
        #    print(pr.parents())

print(get_cpu_percent())

