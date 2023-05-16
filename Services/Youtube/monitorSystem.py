import threading
import time
import psutil
import datetime
import pandas as pd
import traceback

class monitorSystem(object):

    def __init__(self,interval = 1):
        self.interval = interval
        self._reset()
        

    def _bytes2human(self,n):
        #'' 'El método de conversión de unidades de memoria' ''
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return '%.1f%s' % (value, s)
        return "%sB" % n

    def get_cpu_info(self):
        #'' 'Obtener el uso de la CPU' ''
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        return dict(cpu_count=cpu_count, cpu_percent=cpu_percent)

    def get_memory_info(self):
        #'' 'Obtener información de la memoria' ''
        # virtual_mem = psutil.virtual_memory()
        # mem_total = self._bytes2human(virtual_mem.total)
        # mem_percent = virtual_mem.percent
        # mem_free = self._bytes2human(virtual_mem.free + virtual_mem.buffers + virtual_mem.cached)
        # mem_used = self._bytes2human(virtual_mem.total * mem_percent / 100)
        # return dict(mem_total=mem_total, mem_percent=mem_percent, mem_free=mem_free, mem_used=mem_used)
        virtual_mem = psutil.virtual_memory()._asdict()

        return virtual_mem


    def get_disk_info(self):
        #'' 'Obtener información del disco' ''
        disk_usage = psutil.disk_usage('/')
        disk_total = self._bytes2human(disk_usage.total)
        disk_percent = disk_usage.percent
        disk_free = self._bytes2human(disk_usage.free)
        disk_used = self._bytes2human(disk_usage.used)
        return dict(disk_total=disk_total, disk_percent=disk_percent, disk_free=disk_free, disk_used=disk_used)

    def get_boot_info(self):
        #'' 'Obtener hora de inicio' ''
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        return dict(boot_time=boot_time)

    def get_cpu_percent(self):
        data = dict()

        cpuData = psutil.cpu_percent(percpu=True)
        m = 0
        for ncpu in range(len(cpuData)):
            key = "cpu_percent_" + str(ncpu+1)
            data[key] = cpuData[ncpu]
            m += cpuData[ncpu]

        data["cpu_percent_avg"] = m/len(cpuData)

        return data

    def get_cpu_freq(self):
        data = dict()
        cpuData = psutil.cpu_freq(percpu=True)

        for ncpu in range(len(cpuData)):
            key = "cpu_freq_" + str(ncpu + 1)
            data[key] = cpuData[ncpu].current

        return data

    def terminate(self):
        self._running = False

    def monitoring(self):
        data = {}
        data["timestamp"] = time.time()
        data.update(self.get_cpu_percent())
        data.update(self.get_memory_info())
        return data

    def getSystemGeneralData(self):
        data = {}
        data.update(self.get_boot_info())
        data.update(self.get_cpu_info())
        #data.update(self.get_memory_info())
        data.update(self.get_disk_info())
        return data


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
            self.data["resources"].append(self.monitoring())
            netAux.append(self.network())
            time.sleep(self.interval)
        self.data["general"] = self.getSystemGeneralData()

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
        self.data["resources"] = []


# c = monitorSystem()
# t = threading.Thread(target = c.run)
# t.start()
#
# time.sleep(5)
#
# c.terminate()
#
# t.join()
#
# #print(c.data)
# print(pd.DataFrame(c.data["monitoring"]))
# print(c.data["general"])





