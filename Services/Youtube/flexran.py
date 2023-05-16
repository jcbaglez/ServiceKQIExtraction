import requests
import time
import json

class flexran():
    def __init__(self,ipaddr, port):
        self.ip = ipaddr
        self.port = str(port)

    
    def __url(self,query):
        return "http://" + self.ip + ":" + self.port + query
     
    def get_enb_info(self):
        url = self.__url("/stats/enb_config")
        #print(url)
        payload = ""

        response = requests.request("GET", url, data=payload)
        #print(response.json())
        return response.json()


    def get_enb_conf(self):
        conf = self.get_enb_info()["eNB_config"]
        # TODO
        return conf

    def get_enb_bw(self):
        conf = self.get_enb_info()["eNB_config"][0]["eNB"]["cellConfig"][0]["dlBandwidth"]
        return conf

    def get_enb_slices(self):
        enbInfo = self.get_enb_info()["eNB_config"]
        slice_conf = enbInfo[0]["eNB"]["cellConfig"][0]["sliceConfig"]  
        return slice_conf
    
    def set_enb_slices(self,dl,ul,id = -1):

        url = self.__url("/slice/enb/" + str(id))

        headers = {'Content-Type': 'application/json'}

        conf2set = self.create_slicing_set_template(dl,ul)
        payload = json.dumps(conf2set)
        print(payload)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        #time.sleep(1)
        conf = self.get_enb_slices()
        return conf 
    
    def delete_allSlices(self,id = -1):
        url = self.__url("/slice/enb/" + str(id))

        headers = {'Content-Type': 'application/json'}

        conf2set = dict()
        conf2set["dl"] = {"algorithm": "None"}
        conf2set["ul"] = {"algorithm": "None"}

        print(conf2set)
        payload = json.dumps(conf2set)
        
        response = requests.request("POST", url, data=payload, headers=headers)

        time.sleep(1)
        conf = self.get_enb_slices()
        return conf 

    def delete_slice(self,sliceId, id =-1):
        url = self.__url("/slice/enb/" + str(id))

        headers = {'Content-Type': 'application/json'}

        sld = dict()
        sld["ul"] = dict()
        sld["ul"]["slices"] = [{"id": sliceId}]
        sld["dl"] = dict()
        sld["dl"]["slices"] = [{"id": sliceId}]

        
        print(sld)
        payload = json.dumps(sld)
        
        response = requests.request("DELETE", url, data=payload, headers=headers)

        return response.json()
    def get_slice_template_obj(self):
        temp = dict()
        temp["id"] = 0
        temp["label"] = "default"
        #temp["scheduler"] = "round_robin_dl"
        temp["static"] = dict()
        temp["static"]["posLow"] = 0
        temp["static"]["posHigh"] = 3


        return temp

    
    def check_slice_conf_setting(self,conf):
        conf_set = self.get_enb_slices()




    def set_slice_value(self, id, label, posLow, posHigh):
        temp = self.get_slice_template_obj()
        temp["id"] = id
        temp["label"] = label
        temp["static"]["posLow"] = posLow
        temp["static"]["posHigh"] = posHigh

    
        return temp
    
    def create_slicing_set_template(self, dl, ul):
        tmp = dict()
        tmp["dl"] = dict()
        tmp["dl"]["algorithm"] = "Static"
        tmp["dl"]["slices"] = dl

        tmp["ul"] = dict()
        tmp["ul"]["algorithm"] = "Static"
        tmp["ul"]["slices"] = ul

        return tmp        

    def send_ue_association(self,ueID, sliceID):
        if ueID <10:
            ueID = "0" + str(ueID)
        else:
            ueID = str(ueID)
        url = self.__url("/ue_slice_assoc/enb/-1")
        headers = {'Content-Type': 'application/json'}
        payload = dict()
        payload["ueConfig"] = []
        ue = dict()
        ue["imsi"] = "2089201000011"+ ueID
        ue["dlSliceId"] = sliceID
        ue["ulSliceId"] = sliceID
        payload["ueConfig"].append(ue)

        
        
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)


if __name__ == "__main__":

    f = flexran(ipaddr = "192.168.193.102", port = 9999)

    conf = f.get_enb_info()
    
    sl0_dl = f.set_slice_value(0, "default", 9,12)
    sl1_dl = f.set_slice_value(1, "test", 0, 1)

    sl0_ul = f.set_slice_value(0, "default", 9,12)
    sl1_ul = f.set_slice_value(1, "test", 2, 5)

    dl = [sl0_dl, sl1_dl]
    ul = [sl0_ul,sl1_ul]

    conf2set = f.create_slicing_set_template(dl,ul)

    conf_in_enb = f.get_enb_slices()

    print(conf2set)

    print("\n")
    print(conf_in_enb)


    print(conf_in_enb == conf2set)


    print("\n Setting slicing")
    conf_set = f.set_enb_slices(dl,ul)

    print(conf2set == conf_set)

    time.sleep(1)
    print(f.delete_slice(1))

    time.sleep(1)
    confL = f.get_enb_slices()

    print(confL)

    f.delete_allSlices()
    time.sleep(1)
    print(f.get_enb_slices())
        #sl1_dl = f.