import threading
import time
import psutil
import datetime
import pandas as pd
import traceback

class monitorProcess(object):

    def __init__(self, processName, interval = 1):
        self.interval = interval
        self.processName = processName
        self.process = self.getProcess(processName)
        self._reset()
        
    def getPID(self,processName):
        pid = []
        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"].find(processName) != -1:
                pid.append(proc.indo["pid"])

        return pid

    def getProcess(self,processName):
        process = []
        
        for proc in psutil.process_iter(["pid", "name"]):
            if processName == "all":
                process.append(psutil.Process(proc.info["pid"]))
            if proc.info["name"].find(processName) != -1:
                process.append(psutil.Process(proc.info["pid"]))

        return process

    def terminate(self):
        self._running = False

    def get_cpu_info(self):
        #'' 'Obtener el uso de la CPU' ''
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        return dict(cpu_count=cpu_count, cpu_percent=cpu_percent)
    def get_cpu_percent(self):
        data = dict()

        cpuData = psutil.cpu_percent(percpu=True)
        m = 0
        print(cpuData)
        for ncpu in range(len(cpuData)):
            key = "cpu_percent_" + str(ncpu)
            data[key] = cpuData[ncpu]
            m += cpuData[ncpu]

        data["cpu_percent_avg"] = m/len(cpuData)

        return data
    def monitoring(self):
        d = []
        attr = ["pid", "name", "status", "cpu_num", "memory_percent", "connections", "num_threads",
                "create_time"]
        #attr = ["pid", "name", "status", "cpu_num", "memory_percent", "num_threads"]
        cpu_data = self.get_cpu_percent()
        ram_data = psutil.virtual_memory()[2]
        for p in self.process:
            data = dict()
            try:
                data["timestamp"] = time.time()
                with p.oneshot():
                    data.update(p.as_dict(attrs=attr))
                    data["memory_usage_rss"] = p.memory_full_info().rss / (1024 * 1024) # MB
                    data["memory_usage_vms"] = p.memory_full_info().vms / (1024 * 1024) # MB
                    
                    #data["cpu_percentp"] = p.cpu_percent(interval=None) / psutil.cpu_count()
                    #data["cpu_percentp2"] = p.cpu_percent(interval=None)
                    data["cpu_percent"] = cpu_data["cpu_percent_" +str(data["cpu_num"])]
                data.update(cpu_data)
                data["ram_usage_percentage"] = ram_data
                d.append(data)
            except:
                #print("Something went wrong capturing process ")
                pass
        return d


    def network(self):
        d = dict()
        d["timestamp"] = time.time()
        d.update(psutil.net_io_counters(pernic=True))
        return d

    def __net_usage(self,data, inf):
        dr = []
        ds = []
        dpr = []
        dps = []
        t = []
    
        results = dict()
        results['net_bitrate_in'] = []
        results['net_bitrate_out'] = []
        results['net_packetrate_in'] = []
        results['net_packetrate_out'] = []

        for x in range(len(data)):

            try:
                t.append(data[x]["timestamp"])
                dr.append(data[x][inf].bytes_recv)
                ds.append(data[x][inf].bytes_sent)
                dpr.append(data[x][inf].packets_recv)
                dps.append(data[x][inf].packets_sent)
                

                if x != 0:
                    # Calculate datarate (This value is in MBps)
                    datarI = (dr[-1] - dr[-2]) / (t[-1] - t[-2])  # Input datarate
                    datarO = (ds[-1] - ds[-2]) / (t[-1] - t[-2])  # Output datarate
                    packetI = (dpr[-1] - dpr[-2]) / (t[-1] - t[-2])  # Input datarate
                    packetO = (dps[-1] - dps[-2]) / (t[-1] - t[-2])  # Output datarate
                    # Convert to bps and round
                    results['net_bitrate_in'].append(round(datarI * 8, 3))
                    results['net_bitrate_out'].append(round(datarO * 8, 3))
                    results['net_packetrate_in'].append(round(packetI, 3))
                    results['net_packetrate_out'].append(round(packetO, 3))
                else:
                    results['net_bitrate_in'].append(0)
                    results['net_bitrate_out'].append(0)
                    results['net_packetrate_in'].append(0)
                    results['net_packetrate_out'].append(0)
            except:
                print("x --> "+ str(x) )
                print("inf --> " + inf)
                print(" data[x][inf]")
                print(data[x][inf])
                traceback.print_exc()
        results['timestamp'] = t
        return results
    def run(self):
        self._reset()
        netAux = []
        while self._running:
            self.data["process_stats_" + self.processName] += self.monitoring()
            netAux.append(self.network())
            time.sleep(self.interval)

        self.data["network"] = dict()
        # Iterate through the available interfaces
        infs = psutil.net_if_addrs()
        for inf in infs.keys():
            try:
                # For each inf, get usage
                self.data["network"][inf] = self.__net_usage(netAux,inf)

                self.data["network"][inf]["ipaddr"] = infs[inf][0].address
            except:
                traceback.print_exc()
                pass


    def _reset(self):
        self._running = True
        self.data = dict()
        self.data["process_stats_" + self.processName] = []







