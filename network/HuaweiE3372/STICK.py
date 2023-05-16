import csv
import os
import traceback

from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
import pandas as pd
import time



class STICK():

    def __init__(self, user="", password=""):
        self.user = user
        self.password = password
        self.client = self.client_()

    def client_(self):
        connection = AuthorizedConnection('http://192.168.8.1/', password=self.password)
        return Client(connection)

    def clear_stats(self):
        try:
            self.client.monitoring.set_clear_traffic()
        except:
            self.client = self.client_()
            self.client.monitoring.set_clear_traffic()

    def get_traffic_stats(self):

        data = ['CurrentUpload', 'CurrentUploadRate', 'CurrentDownload', 'CurrentDownloadRate', 'TotalUpload',
                'TotalDownload']
        times = ['CurrentConnectTime', 'TotalConnectTime']
        try:
            t = self.client_().monitoring.traffic_statistics()
        except:
            self.client = self.client_()
            t = self.client_().monitoring.traffic_statistics()

        for x in data:
            t[x + "_kbps"] = int(t[x]) *8 / 1000
            del t[x]

        for x in times:
            t[x + "_s"] = int(t[x])
            del t[x]
        try:
            del t['showtraffic']
        except:
            None

        return pd.DataFrame(t, index=[0])

    def deviceInformation(self):
        try:
            p = self.client.device.information()
        except:
            self.client = self.client_()
            p = self.client.device.information()
        return p

    def deviceSignal(self):
        try:
            p = self.client.device.signal()
        except:
            self.client = self.client_()
            p = self.client.device.signal()
        print(p)
        try:
            p['rsrq_dB'] = float(p['rsrq'][:p['rsrq'].find('dB')])
            p['rsrp_dBm'] = float(p['rsrp'][:p['rsrp'].find('dBm')])
            p['rssi_dBm'] = float(p['rssi'][p['rssi'].find('=') + 1:p['rssi'].find('dBm')])

        except:
            p['rsrq_dBm'] = None
            p['rsrp_dB'] = None
            p['rssi_dBm'] = None


        aux = p['sinr']  # TODO
        try:
            p['sinr_dB'] = float(aux[:aux.find("dB")])
        except:
            try:
                p['sinr_dB'] = float(aux[:aux.find("dB")])
            except:
                p['sinr_dB'] = None
        aux = p['rscp']  # TODO


        return pd.DataFrame(p,index=[0])


    def deviceSignalS(self):
        sig = self.deviceSignal().to_dict('records')[0]
        #print(sig)
        data = dict()
        data['RSRP'] = sig['rsrp_dBm']
        data['RSRQ'] = sig['rsrq_dB']
        data['RSSI'] = sig['rssi_dBm']
        data['SINR'] = sig['sinr_dB']
    
        return data
    def recordData(self, restart=True, duration=10, thread=None, delta=5, dataFormat ="all"):
        periodic = ['ul_mcs', 'dl_mcs', 'rrc_status', 'rsrq', 'rsrp', 'rssi', 'sinr', 'txpower',
                    'rscp', 'cqi0', 'cqi1', 'nrulmcs', 'nrdlmcs', 'nrtxpower', 'nrsinr', 'nrrsrp',
                    'nrrsrq']

        if (restart):
            self.clear_stats()

        signals = pd.DataFrame()
        tsStats = pd.DataFrame()


        if thread != None:
            # Record data
            while (thread.is_alive()):
                start = time.time()
                tStats = self.get_traffic_stats()
                signal = self.deviceSignal()
                signals = pd.concat([signals, signal])
                tsStats = pd.concat([tsStats, tStats])
                time_taken = time.time() - start
                time.sleep(max(0, delta - time_taken))


        else:
            # Record data
            for x in range(max(1, int(duration / delta))):
                start = time.time()
                tStats = self.get_traffic_stats()
                signal = self.deviceSignal()
                signals = pd.concat([signals, signal])
                tsStats = pd.concat([tsStats, tStats])
                time_taken = time.time() - start
                time.sleep(max(0, delta - time_taken))
        #signals = signals.dropna(axis=1)
        tsStats = tsStats.dropna(axis=1)
        signals.reset_index(drop=True)
        tsStats.reset_index(drop=True)

        if (dataFormat == "byGroup"):
            return self.formattingDataByGroups(signals, tsStats), signals.to_dict('list'), tsStats.to_dict('list')
        else:
            return self.formattingData(signals, tsStats), signals.to_dict('list'), tsStats.to_dict('list')


    def recordDataFile(self, restart=True, duration=10, thread=None, delta=5, filename='results.csv'):
        periodic = ['ul_mcs', 'dl_mcs', 'rrc_status', 'rsrq', 'rsrp', 'rssi', 'sinr', 'txpower',
                    'rscp', 'cqi0', 'cqi1', 'nrulmcs', 'nrdlmcs', 'nrtxpower', 'nrsinr', 'nrrsrp',
                    'nrrsrq']

        if (restart):
            self.clear_stats()

        signals = pd.DataFrame()
        tsStats = pd.DataFrame()

        path = os.getcwd() + '/data/' + filename

        if thread != None:
            # Record data
            while (thread.is_alive()):
                start = time.time()
                tStats = self.get_traffic_stats()
                signal = self.deviceSignal()
                signals = pd.concat([signals, signal])
                tsStats = pd.concat([tsStats, tStats])
                time_taken = time.time() - start
                time.sleep(max(0, delta - time_taken))


        else:
            # Record data during a time given as input
            for x in range(max(1, int(duration / delta))):
                start = time.time()
                tStats = self.get_traffic_stats() # Get traffic stats (pandas object)
                signal = self.deviceSignal() # Get radio metrics (pandas object)
                try:
                    if (x == 0): # If it's the first iteration, headers must be added
                        tStats.to_csv(path + "_traffic.csv", index = False, header = True)
                        signal.to_csv(path + "_signal.csv" , index = False, header = True)
                    else:
                        # If not, we only have to add the values in a row of the csv file
                        tStats.to_csv(path + "_traffic.csv", mode = 'a', index = False, header = False)
                        signal.to_csv(path + "_signal.csv", mode = 'a', index= False, header = False)

                    # Also adding to a backup variables
                    signals = pd.concat([signals, signal])
                    tsStats = pd.concat([tsStats, tStats])

                    time_taken = time.time() - start
                    time.sleep(max(0, delta - time_taken))
                except:
                    traceback.print_exc()
                    # If there is an excepcion, save the backup in csv files and end loop
                    tsStats.to_csv(path + "_traffic_backup.csv", index=False, header=True)
                    signals.to_csv(path + "_signal_backup.csv", index=False, header=True)
                    break


            signals = signals.dropna(axis=1)
            tsStats = tsStats.dropna(axis=1)
            signals.reset_index(drop=True)
            tsStats.reset_index(drop=True)

            return self.formattingDataByGroups(signals, tsStats), signals.to_dict('list'), tsStats.to_dict('list') , path

    def formattingData(self, signals, tsStats):
        avgMet_traffic = ['CurrentUploadRate_kbps', 'CurrentDownloadRate_kbps']
        #avgMet_signal_lte = ['rsrq_dBm', 'rsrp_dB', 'rssi_dBm', 'nrPPusch_dBm', 'nrPPucch_dBm',
        #                 'nrPSrs_dBm', 'nrPPrach_dBm', 'nrsinr_dB', 'nrrsrp_dBm', 'nrrsrq_dB']
        avgMet_signal_lte = ['rsrq_dB', 'rsrp_dBm', 'rssi_dBm', 'PPucch_dBm', 'PSrs_dBm', 'PPrach_dBm']
        avgMet_signal_5G = ['nrrsrp_dBm', 'nrrsrq_dB', 'nrsinr_dB', 'nrPPucch_dBm', 'nrPSrs_dBm', 'nrPPrach_dBm']
        # Get avg, max and min
        xs = dict()

        info = self.deviceInformation()
        for x in avgMet_traffic:
            xs[x + "_avg"] = tsStats[x].mean()
            xs[x + "_max"] = tsStats[x].max()
            xs[x + "_min"] = tsStats[x].min()

        xs['workmode'] = info['workmode']
        if xs['workmode'] == "LTE":
            avgMet_signal = avgMet_signal_lte
        else:
            avgMet_signal = avgMet_signal_5G
        for x in avgMet_signal:
            try:
                xs[x + "_avg"] = signals[x].mean()
                xs[x + "_max"] = signals[x].max()
                xs[x + "_min"] = signals[x].min()
            except:
                xs[x + "_avg"] = None
                xs[x + "_max"] = None
                xs[x + "_min"] = None

        for x in signals:
            if x not in avgMet_signal:
                try:
                    xs[x] = signals.iloc[0][x]
                except:
                    xs[x] = 'None'
        # Formatting Data
        # xs['radio_meas'] = [signals.to_dict('list')]
        # xs['traffic_meas'] = [tsStats.to_dict('list')]

        # xs['CPEInfo'] = [info]
        return xs

    def formattingDataByGroups(self, signals, tsStats):
        avgMet_traffic = ['CurrentUploadRate_kbps', 'CurrentDownloadRate_kbps']
        #avgMet_signal_lte = ['rsrq_dBm', 'rsrp_dB', 'rssi_dBm', 'nrPPusch_dBm', 'nrPPucch_dBm',
        #                 'nrPSrs_dBm', 'nrPPrach_dBm', 'nrsinr_dB', 'nrrsrp_dBm', 'nrrsrq_dB']
        avgMet_signal_lte = ['rsrq_dB', 'rsrp_dBm', 'rssi_dBm']
        avgMet_signal_5G = ['nrrsrp_dBm', 'nrrsrq_dB', 'nrsinr_dB', 'nrPPucch_dBm', 'nrPSrs_dBm', 'nrPPrach_dBm']
        # Get avg, max and min
        xs = dict()

        info = self.deviceInformation()
        xss = dict()
        for x in avgMet_traffic:
            xss[x + "_avg"] = tsStats[x].mean()
            xss[x + "_max"] = tsStats[x].max()
            xss[x + "_min"] = tsStats[x].min()
        xs['traffic'] = xss

        xss = dict()
        xss['workmode'] = info['workmode']
        if xss['workmode'] == "LTE":
            avgMet_signal = avgMet_signal_lte
        else:
            avgMet_signal = avgMet_signal_5G
        for x in avgMet_signal:
            try:
                xss[x + "_avg"] = signals[x].mean()
                xss[x + "_max"] = signals[x].max()
                xss[x + "_min"] = signals[x].min()
            except:
                xss[x + "_avg"] = None
                xss[x + "_max"] = None
                xss[x + "_min"] = None

        for x in signals:
            if x not in avgMet_signal:
                try:
                    xss[x] = signals.iloc[0][x]
                except:
                    xss[x] = None
        xs['radio'] = xss
        # Formatting Data
        # xs['radio_meas'] = [signals.to_dict('list')]
        # xs['traffic_meas'] = [tsStats.to_dict('list')]

        # xs['CPEInfo'] = [info]
        return xs

    def reboot(self):
        return self.client.device.reboot()