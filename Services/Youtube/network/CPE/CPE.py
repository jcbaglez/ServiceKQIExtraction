import csv
import os
import traceback

from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
import pandas as pd
import time
import signal


class CPE():

    def __init__(self, ip= "",user="", password=""):
        self.user = user
        self.password = password
        self.ip = "192.168.8.1"
        #self.client = self.client_()
        if (ip != ""):
            self.ip = ip


    def init_connection(self):
        connection = AuthorizedConnection("http://" + self.ip + "/", password=self.password)
        self.client = Client(connection)
        #return Client(connection)

    def close_connection(self):
        self.client.user.logout()

    def clear_stats(self):
        try:
            self.init_connection()
            self.client.monitoring.set_clear_traffic()
            self.close_connection()
        except:
            traceback.print_exc()
            self.client = self.init_connection()
            self.client.monitoring.set_clear_traffic()

    def get_traffic_stats(self):

        data = ['CurrentUpload', 'CurrentUploadRate', 'CurrentDownload', 'CurrentDownloadRate', 'TotalUpload',
                'TotalDownload']
        times = ['CurrentConnectTime', 'TotalConnectTime']
        try:
            self.init_connection()
            t = self.client.monitoring.traffic_statistics()
            self.close_connection()
        except:
            traceback.print_exc()
            #self.client = self.client_()
            #t = self.client_().monitoring.traffic_statistics()

        for x in ["CurrentUploadRate", "CurrentDownloadRate"]:
            t[x + "_kbps"] = int(t[x]) *8 / 1000
            del t[x]

        for x in ["CurrentUpload", "CurrentDownload", "TotalUpload", "TotalDownload"]:
            t[x + "_kb"] = int(t[x]) * 8 / 1000
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
            self.init_connection()
            p = self.client.device.information()
            self.close_connection()
        except:

            p = self.client.device.information()
        return p

    def deviceSignal(self):
        try:
            self.init_connection()
            p = self.client.device.signal()
            self.close_connection()
        except:

            p = self.client.device.signal()
        try:
            p['rsrq_dB'] = float(p['rsrq'][:p['rsrq'].find('dB')])
            p['rsrp_dBm'] = float(p['rsrp'][:p['rsrp'].find('dBm')])
            p['rssi_dBm'] = float(p['rssi'][p['rssi'].find('=') + 1:p['rssi'].find('dBm')])

        except:
            p['rsrq_dBm'] = None
            p['rsrp_dB'] = None
            p['rssi_dBm'] = None


        aux = p['sinr']
        try:
            if(aux.find(">=") != -1):
                p['sinr_dB'] = float(aux[aux.find(">=")+2:aux.find("dB")])
            else:
                p['sinr_dB'] = float(aux[:aux.find("dB")])
        except:
            #traceback.print_exc()
            try:
                p['sinr_dB'] = float(aux[:aux.find("dB")])
            except:
                p['sinr_dB'] = None


        aux = p['rscp']  # TODO

        # p['mode'] = int(p['mode'])

        try:
            aux = p['ulbandwidth']
            p['ulbandwidth_MHz'] = float(aux[:aux.find('MHz')])

            aux = p['dlbandwidth']
            p['dlbandwidth_MHz'] = float(aux[:aux.find('MHz')])
        except:
            p['ulbandwidth_MHz'] = None
            p['dlbandwidth_MHz'] = None

        aux = p['txpower']  # TODO
        try:
            for m in aux.split(" "):
                ax = m.split(":")
                p[ax[0] + "_dBm"] = float(ax[1][:ax[1].find('dBm')])
                # del p['nrtxpower']
        except:
            pass

        aux = p['tdd']  # TODO

        aux = p['ul_mcs']  # Not modify for the moment

        aux = p['dl_mcs']  # Not modify for the moment

        try:
            aux = p['ul_mcs'].split(" ")# Not modify for the moment
            p["ul_mcs_"] = p['ul_mcs']
            p["ul_mcs"] = aux[0].split(":")[1]
        except:
            p["ul_mcs"] = None


        try:
            aux = p['dl_mcs'].split(" ")# Not modify for the moment
            p["dl_mcs_"]= p['dl_mcs']
            p["dl_mcs"] = aux[0].split(":")[1]
        except:
            p["dl_mcs"] = None


        aux = p['earfcn']  # TODO

        aux = p['rrc_status']  # TODO

        aux = p['rac']  # TODO

        aux = p['lac']  # TODO

        # p['band'] = int(p['band'] #CHECK

        aux = p['wdlfreq']  # TODO

        aux = p['lteulfreq']  # TODO

        aux = p['ltedlfreq']  # TODO

        aux = p['transmode']  # TODO

        try:
            p['cqi0'] = float(p['cqi0'])
        except:
            pass

        try:
            p['cqi1'] = float(p['cqi1'])
        except:
            pass


        aux = p['ulfrequency']  # TODO

        aux = p['dlfrequency']  # TODO

        try:
            aux = p['nrulbandwidth']
            p['nrulbandwidth_MHz'] = float(aux[:aux.find('MHz')])

            aux = p['nrdlbandwidth']
            p['nrdlbandwidth_MHz'] = float(aux[:aux.find('MHz')])
        except:
            p['nrulbandwidth_MHz'] = None
            p['nrdlbandwidth_MHz'] = None

        try:
            aux = p['nrulmcs'].split(" ")# Not modify for the moment
            p["nrulmcs_"] = p['nrulmcs']
            p["nrulmcs"] = aux[0].split(":")[1]
        except:
            p["nrulmcs"] = None


        try:
            aux = p['nrdlmcs'].split(" ")# Not modify for the moment
            p["nrdlmcs_"]= p['nrdlmcs']
            p["nrdlmcs"] = aux[0].split(":")[1]
        except:
            p["nrdlmcs"] = None


        aux = p['nrtxpower']

        try:
            for m in aux.split(" "):
                ax = m.split(":")
                p["nr" + ax[0] + "_dBm"] = float(ax[1][:ax[1].find('dBm')])
                # del p['nrtxpower']
        except:
            pass

        aux = p['nrearfcn']

        try:
            for m in aux.split(" "):
                ax = m.split(":")
                p['nrearfcn' + ax[0]] = float(ax[1])
        except:
            pass

        try:
            aux = p['nrsinr']
            if(aux.find(">=") != -1):
                p['nrsinr_dB'] = float(aux[aux.find(">=")+2:aux.find("dB")])
            else:
                p['nrsinr_dB'] = float(aux[:aux.find("dB")])
        except:
            #traceback.print_exc()
            try:
                p['nrsinr_dB'] = float(aux[:aux.find("dB")])
            except:
                p['nrsinr_dB'] = None

        aux = p['nrrsrp']
        try:
            p['nrrsrp_dBm'] = float(aux[:aux.find('dBm')])
        except:
            p['nrrsrp_dBm'] = None

        aux = p['nrrsrq']
        try:
            p['nrrsrq_dB'] = float(aux[:aux.find('dB')])
        except:
            try:
                p['nrrsrq_dB'] = float(aux[1:aux.find('dB')])
            except:
                p['nrrsrq_dB'] = None

        return pd.DataFrame(p,index=[0])

    def deviceSignalS(self):
        sig = self.deviceSignal().to_dict('records')[0]
        print(sig)
        data = dict()
        data['RSRP'] = sig['rsrp_dBm']
        data['RSRQ'] = sig['rsrq_dB']
        data['RSSI'] = sig['rssi_dBm']
        data['SINR'] = sig['sinr_dB']
        data["PPucch_dBm"] = sig["PPucch_dBm"]
        data["PPusch_dBm"] = sig["PPusch_dBm"]
        data["PSrs_dBm"] = sig["PSrs_dBm"]
        data["PPrach_dBm"] = sig["PPrach_dBm"]
        data["dl_mcs"] = sig["dl_mcs"]
        data["ul_mcs"] = sig["ul_mcs"]
        data["radioBandwidth"] = sig["dlbandwidth_MHz"]


        data['NR_RSRP'] = sig['nrrsrp_dBm']
        data['NR_RSRQ'] = sig['nrrsrq_dB']
        data['NR_SINR'] = sig['nrsinr_dB']
        data["NR_PPucch_dBm"] = sig["nrPPucch_dBm"]
        data["NR_PPusch_dBm"] = sig["nrPPusch_dBm"]
        data["NR_PSrs_dBm"] = sig["nrPSrs_dBm"]
        data["NR_PPrach_dBm"] = sig["nrPPrach_dBm"]
        data["NR_dl_mcs"] = sig["nrdlmcs"]
        data["NR_ul_mcs"] = sig["nrulmcs"]

        data["NR_radioBandwidth"] = sig["nrdlbandwidth_MHz"]


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

        path = os.getcwd() + '/data/'
        if (os.path.exists(path) == False):
            os.mkdir("data")

        path = path + filename

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
                try:
                    start = time.time()
                    tStats = self.get_traffic_stats() # Get traffic stats (pandas object)
                    tStats['timestamp'] = start
                    signal = self.deviceSignal() # Get radio metrics (pandas object)
                    signal['timestamp'] = start
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

                except:
                    print("Error getting sample")
                    self.client = self.client_()
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

    def __trafficAVG(self, data):
        results = dict()
        # Traffic summary
        aux = pd.DataFrame(data)
        results["DLRate_kbps_avg"] =  aux["CurrentDownloadRate_kbps"].mean()
        results["DLRate_kbps_max"] = aux["CurrentDownloadRate_kbps"].max()
        results["DLRate_kbps_min"] = aux["CurrentDownloadRate_kbps"].min()

        results["ULRate_kbps_mean"] = aux["CurrentUploadRate_kbps"].mean()
        results["ULRate_kbps_max"] = aux["CurrentUploadRate_kbps"].max()
        results["ULRate_kbps_min"] = aux["CurrentUploadRate_kbps"].min()

        return results

    def __signalAVG(self, data):
        results = dict()
        # Signal summary
        aux = pd.DataFrame(data)
        keys = ['rsrq_dB', 'rsrp_dBm', 'rssi_dBm', 'sinr_dB', 'PPusch_dBm', 'PPucch_dBm',
                'PSrs_dBm', 'PPrach_dBm', 'ul_mcs','dl_mcs', 'nrPPusch_dBm', 'nrPPucch_dBm',
                'nrPSrs_dBm', 'nrPPrach_dBm', 'nrsinr_dB', 'nrrsrp_dBm', 'nrrsrq_dB', 'nrulmcs',
                'nrdlmcs']

        for key in keys:
            try:
                results[key+"_avg"] = aux[key].mean()
                results[key+"_max"] = aux[key].max()
                results[key + "_min"] = aux[key].min()
            except:
                results[key+"_avg"] = float("NaN")
                results[key+"_max"] = float("NaN")
                results[key + "_min"] = float("NaN")

        return results

    def monitoring(self, timer = 10, thread = None, q = None):
        results = {"traffic": [], "radio": [], "timestamps": []}
        if thread != None:
            while thread.is_alive():
                results["traffic"].append(self.get_traffic_stats().to_dict(orient='records')[0])
                results["radio"].append(self.deviceSignal().to_dict(orient="records")[0])
                results["timestamps"].append(time.time())
                time.sleep(1)
        elif timer >0:
            for x in range(timer):
                results["traffic"].append(self.get_traffic_stats().to_dict(orient='records')[0])
                results["radio"].append(self.deviceSignal().to_dict(orient="records")[0])
                results["timestamps"].append(time.time())
                time.sleep(1)



        results["avgTraffic"] = self.__trafficAVG(results["traffic"])
        results["avgRadio"] = self.__signalAVG(results["radio"])


        if q != None:
            q.put(results)

        return results


