
import subprocess
import shlex
import pexpect
import time
import os
import sys
import platform
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

import mouse

import pandas as pd
import numpy as np
from PIL import ImageGrab
import cv2
import mss
import traceback

# Get information about the resolution of the screen
def monitorInfo(im = None):
	if (im is None): #If any parameter is given as input, it will return all the screens information
		return np.asarray(mss.mss().monitors)
	else: # Converserly, if a parameter is give, it will only return the information of the specific screen (given as input)
		try:
			return mss.mss().monitors[im] 
		except: # If an exception is thrown , it means that the parameter given as input is out of range of the array. In this case, this function will return the general information
			return mss.mss().monitors[0]
	
# Returns the number of monitors which the computer is using
def numberOfMonitors():
	return monitorInfo().size -1


def mouseMovement(pos,q):
    while(1):
        pos2 = mouse.get_position()
        if (pos[0] != pos2[0] or pos[1] != pos2[1]):
            q.put(time.time())
            return time.time()

def detectMove(t,q):
	mon = {"top":250, "left":700, "width": 400, "height":400}
	#mon = {"top": 1300, "left": 700, "width": 400, "height": 400} # MSI
	fps = 0
	fpsAux = 0
	s = 0
	res = []
	frameI = []
	frameE = []
	moveITime = []
	moveETime = []
	title = "TEST"
	sct = mss.mss()
	changeTime = 0
	th = 0.75 * mon['width'] * mon['height'] * 4
	imgAux = np.asarray(sct.grab(mon))
	initTime = time.time()
	while(initTime + t > time.time()):
		img = np.asarray(sct.grab(mon))
		fps += 1
		cv2.imshow(title,img)
		if cv2.waitKey(25) & 0xFF == ord("q"):
			cv2.destroyAllWindows()
			break
		if (np.sum(imgAux == img) < th):
			if(fpsAux == 0):
				s = time.time()
				moveITime.append(q)
				frameI.append(fps)
				print("Character starts to move")
				fpsAux = fps
		else:
			if(fpsAux != 0):
				e = time.time()
				res.append([fpsAux,fps,s,e])
				moveETime.append(e)
				print("Character has stopped")
				frameE.append(fpsAux)
				fpsAux = 0
				print("Character has been moving for ", e - s)
		imgAux = img
	#q.put((frameI,frameE,moveITime,moveETime))
	#q.put([frameI,frameE,moveITime,moveETime])
	q.put(res)
def getFromConsole(cmd):

	plat = platform.system()

	if (plat == "Linux"):
		args = [cmd, "/etc/services"]
	elif (plat == "Windows"):
		args = ["powershell.exe", cmd]
	
	proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	#print(out)
	return out

def getProcess(pName):

	process = pName.split(" ")[0]
	plat = platform.system()
	if (plat == "Windows"):
		cmd = "Get-Process " + process +"*"
	# TODO LINUX command

	try:
		resp = getFromConsole(cmd).decode('utf-8')
		print(resp)
		# Convert response to a Pandas DataFrame
		# Get headers
		headers = []
		index1 = resp.find("\r\n")+len("\r\n")
		index = resp.find("ProcessName") + len("ProcessName")
		s1 = resp[index1:index]
		s1 = s1.split(" ")
		for elem in s1:
			if (elem != ("")):
				headers.append(elem)
		
		# Get Processes
		index = resp.find("-")
		s2 = resp[index:]
		index = s2.find("\r\n") + len("\r\n")
		s3 = s2[index:].split("\r\n")
		data = []
		for line in s3:
			x2 = line.split(" ")
			l = []
			for elem in x2:
				if (elem != ("")):
					l.append(elem)
			
			if (len(l)> len(headers)):
				lElement =""
				ll = len(l)
				iT = len(headers)
				for i in range (iT,ll):
					l[iT -1] += " " + l[iT]
					del l[iT]
				
			if (bool(l)):
				data.append(l)
		
		# Create DataFrame
		df = pd.DataFrame (data,columns = headers)
	except:
		traceback.print_exc()
		print("Error in getProcess")
		df = []
	return df

def isProcessRunning(pName):
	process = getProcess(pName)
	print(process)
	if (not process.empty):
		p = process.loc[process["ProcessName"] == pName]
		return not p.empty
	else:
		return False
def killProcess(pName):
	cmd = "TASKKILL /F /IM " + pName +".exe"
	getFromConsole("TASKKILL /F /IM \""+pName+".exe\"")

def consoleCall (cmd):
	args = shlex.split(cmd)
	subprocess.call(args)


def pingTest(ip,name,size,num,queue = None):

	try:
		plat = platform.system()
		language = "EN"
		vD = dict()
		if(plat == "Windows"):
			out = getFromConsole("ping -l " + str(size) +" -n " + str(num)+ " " + ip).decode('utf-8','ignore')
			
			
			print (out)

		
		# Get packet lenght
		index = out.find("with")
		l = len("with")
		if (index == -1): #If not found, try with Spanish
			index = out.find("con")
			language = "ES"
			l = len("con")

		aux = out[index+l:out.find(":")]
		aux = aux[:aux.find("bytes")-1]
		
		try:
			vD[name+'_packetLength'] = int(aux) #Bytes
			#vD['PING_packetLength'] = int(aux) #Bytes
		except:
			vD[name+'_packetLength'] = None
			#vD['PING_packetLength'] = None

		# Get statistics
		index = out.find("Packets")
		index2 = out.find("Approximate")
		if (index == -1):
			index = out.find("Paquetes")
			index2 = out.find("aproximados")
		

		aux = out[index:index2]
		index = aux.find(":")+1
		aux = aux[index:-3]
		index = aux.find("(")
		aux2 = aux[index:]
		aux = aux[:index]

		values = aux.split(",")
		
		for i in values:
			index = i.find("=")+1
			aux = i[index+1:]
			key = i[:index-2]
			aux = aux[:index]
			#vD["PING_"+key.strip()] = int(aux)
			
			if(aux.find("\r") != -1):
				aux = aux[:aux.find("\r")]
				# print(key.strip())
				# while(aux.find('') != -1):
				# 	print("hi")
				# 	aux = aux[aux.find(''):]
			
			vD[name+key.strip()] = int(aux.strip())
		aux2 = aux2[1:aux2.find("%")]
		vD[name+'_LossPercentage'] = int(aux2)
		#vD['PING_LossPercentage'] = int(aux2)




		# Get RTT
		index = out.find("Minimum")
		if (index == -1):
			index = out.find("Mnimo")
		aux = out[index:-1]
		values = aux.split(",")
		for i in values:
			index = i.find("=")+1
			aux = i[index+1:]
			key = i[:index-2]
			index = aux.find("m")
			aux = aux[:index]
			vD[name+"PING_"+key.strip()] = int(aux)

		# #if queue is not None:
		# queue.put(vD)
		# return vD
	except:
		traceback.print_exc()
		vD = dict()
		if(language =="ES"):
			vD[name+"_packetLength"] = 0
			vD[name+"_LossPercentage"] = 0
			vD[name+"_PING_Mnimo"] = 0
			vD[name+"_PING_Mximo"] = 0
			vD[name+"_PING_Media"] = 0
		else:
			vD[name+"_packetLength"] = 0
			vD[name+"_LossPercentage"] = 0
			vD[name+"_PING_Minimum"] = 0
			vD[name+"_PING_Maximum"] = 0
			vD[name+"_PING_Average"] = 0
	
	vD[name+"_IP"] = ip

	queue.put(vD)
	return vD
def connectionAvailable(ip):
	connection = False
	plat = platform.system()

	if (plat == "Linux"):	
		out = getFromConsole("ping -c1 " + ip).decode("utf-8")
		if(out.find("1 received") != -1):
			#print("Hay conexión")
			connection = True
		# else:
		# 	print("No hay conexión")
	elif(plat == "Windows"):
		out = str(getFromConsole("ping -n 1 " + ip))
		if(out.find("Received = 1") != -1):
			connection = True

	return connection

def getBrowser(headless=False):
	d = DesiredCapabilities.CHROME
	#d['loggingPrefs'] = { 'browser':'ALL' }
	d['goog:loggingPrefs'] = {'browser': 'ALL'}

	chrome_options = webdriver.ChromeOptions()
	chrome_options.accept_untrusted_certs = True
	chrome_options.assume_untrusted_cert_issuer = False
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-impl-side-painting")
	chrome_options.add_argument("--disable-setuid-sandbox")
	chrome_options.add_argument("--disable-seccomp-filter-sandbox")
	chrome_options.add_argument("--disable-breakpad")
	chrome_options.add_argument("--disable-client-side-phishing-detection")
	chrome_options.add_argument("--disable-cast")
	chrome_options.add_argument("--disable-cast-streaming-hw-encoding")
	chrome_options.add_argument("--disable-cloud-import")
	chrome_options.add_argument("--disable-popup-blocking")
	chrome_options.add_argument("--ignore-certificate-errors")
	chrome_options.add_argument("--disable-session-crashed-bubble")
	chrome_options.add_argument("--disable-ipv6")
	chrome_options.add_argument("--allow-http-screen-capture")
	chrome_options.add_argument("--allow-running-insecure-content")
	chrome_options.add_argument("--allow-insecure-localhost")
	chrome_options.add_argument("--start-maximized")
	if(headless):
		chrome_options.add_argument("headless")
	if(platform.system() == "Linux"):
		dir_path = "/usr/bin/chromedriver"
		browser = webdriver.Chrome(desired_capabilities=d, executable_path = dir_path, chrome_options=chrome_options)
	elif(platform.system() == "Windows"):
		dir_path = "C:/chromedriver/chromedriver.exe"
		browser = webdriver.Chrome(desired_capabilities=d, executable_path = dir_path, options = chrome_options)

	return browser



def getLine (key,listInputs):

	found = False
	line = 1
	#print(key)
	#print(len(listInputs))
	while (found == False and line < len(listInputs)):
		#print(listInputs[line])
		if(listInputs[line].find(key) != -1):
			found = True
		else:
			line = line + 1

	if(found ==False):
		line = -1

	return line


def getValue (text):

	value = text[text.find("\"")+1:]
	value = value[:value.find("\"")]

	return value







