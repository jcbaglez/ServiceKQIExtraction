import sys

import pprint

import requests

import xmltodict

import platform

from utils import *

import traceback



class HuaweiE3372(object):

  BASE_URL = 'http://{host}'

  COOKIE_URL = '/html/index.html'

  XML_APIS = [

    '/api/device/information',

    '/api/device/signal'

    '/api/monitoring/status',

    '/api/monitoring/traffic-statistics',

    '/api/dialup/connection',

    '/api/global/module-switch',

    '/api/net/current-plmn',

    '/api/net/net-mode',

  ]

  session = None



  def __init__(self,host='192.168.8.1'):

    self.host = host

    self.base_url = self.BASE_URL.format(host=host)

    self.session = requests.Session()

    # get a session cookie by requesting the COOKIE_URL

    r = self.session.get(self.base_url + self.COOKIE_URL)



  def get(self,path):

    return xmltodict.parse(self.session.get(self.base_url + path).text).get('response',None)


  def getKPI(self):
    intent = 0
    results = {}
    try:
      for path in self.XML_APIS:
        for key,value in self.get(path).items():
          results[key] = value
    except Exception:
      print("Error en getKPI")
      traceback.print_exc()
      intent = intent + 1
      if(intent < 10):
        time.sleep(2)
        self.getKPI()
    return results

  def getRadioKPI(self):
    kpi = self.getKPI()
    resKPI = dict()
    resKPI['RSRP'] =int(kpi['rsrp'][:kpi['rsrp'].find("dBm")])
    resKPI['RSRQ'] = int(kpi['rsrq'][:kpi['rsrq'].find("dB")])
    resKPI['RSSI'] = int(kpi['rssi'][kpi['rssi'].find("=")+1:kpi['rssi'].find("dBm")])
    resKPI['SINR'] = int(kpi['sinr'][kpi['sinr'].find("=")+1:kpi['sinr'].find("dB")])
    resKPI['PCI'] = kpi['pci']
    return resKPI
  
  def rebootStick(self):
    browser = getBrowser(True)
    browser.get('http://192.168.8.1/html/reboot.html')
    bReb = browser.find_element_by_id("button_reboot")
    bReb.click()
    time.sleep(1)
    accept = browser.find_element_by_id("pop_confirm")
    accept.click()
