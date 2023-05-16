from network.CPE.CPE import *

cpe = CPE(ip = "192.168.8.1", password="areyouready?1")

signals = cpe.deviceSignal()
print('RSRQ_dB = ' + str(signals['rsrq_dB']))
print('RSRP_dBm = ' + str(signals['rsrp_dBm']))
print('SINR_dB = ' + str(signals['sinr_dB']))
print('NR BW = ' + str(signals['nrdlbandwidth_MHz']))
print('LTE BW = ' + str(signals['dlbandwidth_MHz']))
print('NR EARFCN = ' + str(signals['nrearfcn']))
