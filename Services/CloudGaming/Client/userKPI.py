
from lteStick import *
import json
import time

ltestick = HuaweiE3372()
kpi = ltestick.getKPI()
#print(kpi)
#print(kpi['CurrentDownloadRate'])
resKPI = {}


resKPI['RSRP'] =int(kpi['rsrp'][:kpi['rsrp'].find("dBm")])
resKPI['RSRQ'] = int(kpi['rsrq'][:kpi['rsrq'].find("dB")])
resKPI['RSSI'] = int(kpi['rssi'][kpi['rssi'].find("=")+1:kpi['rssi'].find("dBm")])
resKPI['SINR'] = int(kpi['sinr'][kpi['sinr'].find("=")+1:kpi['sinr'].find("dB")])
resKPI['PCI'] = kpi['pci']
print(json.dumps(resKPI))
