
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
        #p = self.doGetRequest("/configuration/" + element + param)
        p = self.doGetRequest("/configuration/" + param)

        print(p)
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
        #return self.doGetRequest("/configuration/"+ element +"/all")
        return self.doGetRequest("/configuration/all")

    # SET
    def set_config(self,parameters,element = "enb"):
        print(parameters)
        #return self.doRequest("/crowdcell/" + element +"/configuration",parameters)
        return {}
    def set_config_live(self, parameters, element = "enb"):
        return self.doRequest("/amarisoft/" + element + "/config_set", parameters)

    def cell_gain(self,cell_id = 1, gain=0):
        payload = {'cell_id':cell_id , 'gain':gain}
        return self.doRequest("/amarisoft/enb/cell_gain", payload)

    def rf(self,tx_gain=None, tx_channel_index = None, rx_gain = None, rx_channel_index=None, rx_arg = None, rx_agc_timeout = None):
        # TODO
        print("TODO")
        #return doRequest("/amarisoft/enb/rf", payload)

    def snr(self,snr):
        # Deprecated
        payload = {'snr': snr}
        return self.doRequest("/amarisoft/enb/snr",payload)

    def noise_level(self,cell_id = 1, noise_level = 0):
        payload = {"cell_id": cell_id, "noise_level": noise_level}

        return self.doRequest("/amarisoft/enb/noise_level", payload)

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

    def cell_config(self,element="enb"):

        c = self.config_get(element)
        fileconf = self.configFile_get()
        config = dict()
        if "cells" in c:
            config["cells"] = c["cells"]

            for cellId in config["cells"].keys():
                rf_port_index = config["cells"][cellId]["rf_port"]
                config["cells"][cellId]["rf_port"] = c["rf_ports"][rf_port_index]

                if "channel_dl" in c["rf_ports"][rf_port_index] and "noise_level" in c["rf_ports"][rf_port_index][
                    "channel_dl"]:
                    config["cells"][cellId]["channel_simulator"] = True
                    config["cells"][cellId]["noise_level"] = c["rf_ports"][rf_port_index]["channel_dl"]["noise_level"][
                        0]
                else:
                    config["cells"][cellId]["channel_simulator"] = False

        if "nr_cells" in c:
            config["nr_cells"] = c["nr_cells"]

            for cellId in config["nr_cells"].keys():
                # print(c["nr_cells"].keys())

                fileconf["nr_cell_list"][0]["subcarrier_spacing"]
                try:
                    config["nr_cells"][cellId]["subcarrier_spacing"] = fileconf["nr_cell_list"][0]["subcarrier_spacing"]
                except:
                    config["nr_cells"][cellId]["subcarrier_spacing"] = -1

                try:
                    config["nr_cells"][cellId]["bandwidth"] = fileconf["nr_cell_default"]["bandwidth"]
                except:
                    config["nr_cells"][cellId]["bandwidth"] = -1

                rf_port_index = config["nr_cells"][cellId]["rf_port"]
                # print(rf_port_index)
                config["nr_cells"][cellId]["rf_port"] = c["rf_ports"][rf_port_index]

        return config

    def __gatherCellStats_UE(self, targetUE):
        stats = dict()
        resp = self.ue_get("enb")
        linked_cell = -1
        #print(targetUE)
        for ue in resp["ue_list"]:
            if (("enb_ue_id" in ue) and (ue["enb_ue_id"] == targetUE["enb_ue_id"])):
                stats[ue["cells"][0]["cell_id"]] = ue["cells"][0]
                stats[ue["cells"][0]["cell_id"]].update({"cell_type": "LTE"})
                if "linked_ran_ue_id" in ue:  # This means that it has a linked NR cell (so it is 5G/NSA)
                    # For this case, need to get stats from this cell too
                    linked_cell = ue["linked_ran_ue_id"]

            elif ("ran_ue_id" in ue and ue["ran_ue_id"] == linked_cell):
                stats[ue["cells"][0]["cell_id"]] = ue["cells"][0]
                stats[ue["cells"][0]["cell_id"]].update({"cell_type": "NR"})

        return stats

    def ue_enb_stats(self, ip = None):
        # TODO: Extend to 5G SA
        stats = dict()
        if ip != None:
            # TODO: Check Ip address pattern
            targetUE = self.find_ueID_byIP(ip = ip)

            stats = self.__gatherCellStats_UE(targetUE)

        else:

            ueInfo = self.ue_get(element="mme")
            for targetUE in ueInfo["ue_list"]:
                stats[targetUE["mme_ue_id"]] = self.__gatherCellStats_UE(targetUE)



        return stats


    def cell_stats(self,element= "enb", cell_id = -1):
        stats = self.stats(element="enb")

        stats = stats["cells"]
        if cell_id != -1:
            stats = stats[cell_id]

        return stats


    def find_ueID_byIP(self,ip):
        ues = self.ue_get("mme")["ue_list"]

        res = dict()

        paramInterest = ["enb_id", "enb_ue_id", "mme_ue_id"]


        for ue in ues:
            try:
                # TODO: Extend for the case when multibearers are associated to an UE
                if ip == ue["bearers"][0]["ip"]:
                    try:
                        for param in paramInterest:
                            res[param] = ue[param]

                    except:
                        print("UE does not have an enb association --> It is in idle state!")
                        for param in paramInterest:
                            res[param] = ue[param]
            except:
                print("Something wrong in find_ueID_byIP")

        return res



    def cell_counters(self,element="enb"):
        r = self.stats(element)

        data = dict()
        if element == "enb":
            for cell_id in r["cells"].keys():
                data[cell_id] = r["cells"][cell_id]["counters"]["messages"]
        else:
            data = r["counters"]["messages"]
            data['emm_registered_ue_count'] = r['emm_registered_ue_count']
            data['emm_connected_ue_count'] = r['s1_connections'][0]['emm_connected_ue_count']

        data['cpu'] = r['cpu']
        data['time'] = r['time']
        return data


    # def cell_stats(self,element="enb"):
    #     r = self.stats(element)
    #
    #     if element == "enb":
    #         stats = r['cells']['1']
    #         del stats["counters"]
    #     else:
    #         stats = dict()
    #         stats['emm_registered_ue_count'] = r['emm_registered_ue_count']
    #         stats['emm_connected_ue_count'] = r['s1_connections'][0]['emm_connected_ue_count']
    #
    #     return stats

    def error(self,element="enb"):
        r = self.stats(element)

        error = dict()
        if element == "enb":
            for cell_id in r["cells"].keys():
                error[cell_id] = r["cells"][cell_id]["counters"]["errors"]
        else:
            error = r["cells"]["counters"]["errors"]
        return error

