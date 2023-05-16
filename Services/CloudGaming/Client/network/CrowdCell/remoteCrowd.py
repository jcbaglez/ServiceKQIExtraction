
import requests
import sys
import json
import traceback

#from network.HuaweiE3372.lteStick import *

class remoteCrowd:
    def __init__(self,IP,port):
        self.IP = IP
        self.port = port

    def doRequest(self,url, d=dict()):
        base = "http://"+ self.IP + ":"+ self.port
        header =  {'content-type' : 'application/json'}

        r = requests.post(base + url,data = json.dumps(d), headers=header)
        if(r.status_code == 200):
            return r.json()
        else:
            return None

    def doGetRequest(self,url):
        base = "http://"+ self.IP + ":"+ self.port
        r = requests.get(base + url)
        if(r.status_code == 200):
            return r.json()
        else:
            return None
    def prepareConfiguration(self,var):
        conf = dict()
        for v in var:
            t = self.get_param(v)

            if(type(var[v]) != type(t)):
                if (type(t) == int):
                    var[v] = int(var[v])

                elif (t is float):
                    var[v] = float(var[v])
            
            if (var[v] != t): # If both values aren't equals, add to conf dictionary in order to change CrowdCell configuration
                conf[v] = var[v]
        return conf
    def configureCrowd(self,conf):
        #print(conf)
        #print("adaptTypes")
        conf = self.prepareConfiguration(conf)
        #print(conf)

        if (bool(conf)): # Change parameters if any
            # Delete from conf dictionary parameters which do not require to reboot the CrowdCell
            try:
                snr = conf['snr']
                del conf['snr']
            except:
                snr = None
            try:
                gain = conf['gain']
                del conf['gain']
            except:
                gain = None
            
            # Check again in there are parameters to change
            if (bool(conf)): # If any, reboot is required
                self.set_config(conf)
                self.reboot()
        
            if(gain != None):
                self.cell_gain(gain)
            if(snr != None):
                self.snr(snr)


            
    # GET
    def get_param(self,param,element="enb"):
        p = self.doGetRequest("/configuration/" + element + param)
        return p[param]

    def config_get(self,element="enb"):
        return self.doRequest("/amarisoft/" + element + "/config_get")

    def ue_get(self,element="enb", id = -1):
        payload = dict()
        payload['stats'] = True
        if (id != -1):
            payload['ue_id'] = id

        return self.doRequest("/amarisoft/" + element + "/ue_get", payload)

    def stats(self,element="enb"):
        return self.doRequest("/amarisoft/" + element + "/stats")

    def erab_get(self,element="enb"):
        return self.doRequest("/amarisoft/" + element + "/erab_get")

    def log_get(self,element="enb"):
        return self.doRequest("/amarisoft/" + element + "/log_get")

    def configFile_get(self,element="enb"):
        #return self.doRequest("/configuration/crowdcell?parameter=all")
        return self.doGetRequest("/configuration/"+ element +"/all")


    # SET
    def set_config(self,parameters,element = "enb"):
        print(parameters)
        return self.doRequest("/crowdcell/" + element +"/configuration",parameters)

    def cell_gain(self,gain):
        payload = {'cell_id':1 , 'gain':gain}
        return self.doRequest("/amarisoft/enb/cell_gain", payload)

    def rf(self,tx_gain=None, tx_channel_index = None, rx_gain = None, rx_channel_index=None, rx_arg = None, rx_agc_timeout = None):
        # TODO
        print("TODO")
        #return doRequest("/amarisoft/enb/rf", payload)

    def snr(self,snr):
        payload = {'snr': snr}
        return self.doRequest("/amarisoft/enb/snr",payload)

    def log_reset(self,element="enb"):
        return self.doRequest("/amarisoft/" + element + "/log_reset")
    def reboot(self, element):
        self.doRequest("/crowdcell" + element+"/action?t=reboot")

    # INFO
    def quit(self,element="enb"):
        return self.doRequest("/amarisoft/"+ element + "/quit")

    def help(self,element="enb"):
        return self.doRequest("/amarisoft/"+ element + "/help")



    # ADDITIONAL

    def cell_config(self,element = "enb"):
        c = self.config_get(element)
        configFile = self.configFile_get()
        tx_channels = c['tx_channels']
        rx_channels = c['rx_channels']
        rf_ports = c['rf_ports']

        config = dict()
        config = c['cells']['1']
        config['transmision_mode'] = configFile['cell_default_2']['transmission_mode']
        config['mac_config'] = configFile['cell_default_2']['mac_config']
        config['srs_dedicated'] = configFile['cell_default_2']['srs_dedicated']


        config['tx_channels'] = c['tx_channels']
        config['rx_channels'] = c['rx_channels']
        config['rf_ports'] = c['rf_ports']
        return config

    def cell_config2(self,element="enb"):
        c = self.config_get(element)
        configFile = self.configFile_get()


        config = dict()


        config = c['cells']['1']
        print("CrowdCell config")
        print(config)
        print("CrowdCell config File")

        print(configFile)
        #time.sleep(20)
        config['transmision_mode'] = configFile['cell_default_2']['transmission_mode']
        config['mac_config'] = configFile['cell_default_2']['mac_config']
        rf_port = c['rf_ports'][0]['channel_sim']
        try:
            config['noise_level'] = rf_port['noise_level'][0]
            config['path_delay'] = rf_port['path_delay'][0]
            config['path_type'] = rf_port['path_type'][0]
            config['channelSimulator'] = True
        except Exception:
            traceback.print_exc()
            config['channelSimulator'] = False
        return config
    def ue_enb_stats(self):
        ue = self.find_ueID()
        stats = dict()
        try:
            resp = self.ue_get("enb",ue['enb_ue_id'])
            stats = resp['ue_list'][0]['cells'][0]
            stats['ue_dl_retx'] = stats['dl_retx']

            stats['UE_ul_retx'] = stats['ul_retx']
            stats['UE_dl_bitrate'] = stats['dl_bitrate']
            stats['UE_ul_bitrate'] = stats['ul_bitrate']
            del stats['dl_retx']
            del stats['ul_retx']
            del stats['dl_bitrate']
            del stats['ul_bitrate']
        except:
            print("Error in enb_stats")
            stats['ue_dl_retx'] = 0

            stats['UE_ul_retx'] = 0
            stats['UE_dl_bitrate'] = 0
            stats['UE_ul_bitrate'] = 9
            #stats.update(ue)
        return stats


    def find_ueID(self):
        #ltestick = HuaweiE3372()
        # kpi = ltestick.getKPI()
        # imei = kpi['Imei'][:-1] + "00"
        # ues = self.ue_get("mme")["ue_list"]
        #
        # for ue in range(len(ues)):
        #     if(ues[ue]['imeisv'] == imei):
        #
        #         return ues[ue]

                return None
    def cell_counters(self,element="enb"):
        r = self.stats(element)
        if (element == "enb"):
            d2 = r["cells"]["1"]["counters"]["messages"]
            data = r["counters"]["messages"]
            data.update(d2)

        else:
            data = r["counters"]["messages"]
            data['emm_registered_ue_count'] = r['emm_registered_ue_count']
            data['emm_connected_ue_count'] = r['s1_connections'][0]['emm_connected_ue_count']

        data['cpu'] = r['cpu']
        data['time'] = r['time']
        return data


    def cell_stats(self,element="enb"):
        r = self.stats(element)

        if element == "enb":
            stats = r['cells']['1']
            del stats["counters"]
        else:
            stats = dict()
            stats['emm_registered_ue_count'] = r['emm_registered_ue_count']
            stats['emm_connected_ue_count'] = r['s1_connections'][0]['emm_connected_ue_count']

        return stats

    def error(self,element="enb"):
        r = self.stats(element)

        if element == "enb":
            error = r['cells']['1']["counters"]["errors"]
            error.update(r['counters']['errors'])
        else:
            error = r['counters']['errors']

        return error

