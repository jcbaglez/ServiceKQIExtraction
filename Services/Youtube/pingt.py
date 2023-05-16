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

crowd = remoteCrowd("192.168.192.160", "5000")


#stats = crowd.get_stats()  # Reset cell stats

#stats = crowd.get_log()
#print(stats)

#stats = crowd.cell_config_LTE("enb")

#stats = crowd.get_cellConfig("enb")

#print(stats)
#stats2 = crowd.get_stats()
#print(stats2)


params = dict()
params["cells"] = dict()

cfg = dict()
cfg["pdsch_mcs"] = 15
cfg["pdsch_fixed_rb_alloc"] = True
cfg["pdsch_fixed_rb_start"] = 0
cfg["pdsch_fixed_l_crb"] = 100

params["cells"]["1"] = cfg
#crowd.set_conf_remoteAPI(params)

cpe = CPE(ip="192.168.8.1", password="areyouready?1")
while 1:
    print(cpe.deviceSignal()[["rsrp", "rsrq", "rssi", "sinr"]])

    print(cpe.deviceSignal()[["nrrsrp", "nrrsrq", "nrsinr"]])
    print("\n ----------------------------------------------------------")
    time.sleep(2)