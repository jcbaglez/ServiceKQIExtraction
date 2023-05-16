import os
import time
import traceback
from sys import platform
#import lsb_release

# # Function that replace all the pattern in a file
# def replaceTextSed(file, pattern,newValue):
# 	# Create sed command for replacing pattern in a file
# 	#comand = "sed -i '' 's/" + pattern + "/" + newValue + "/g' " + file
# 	comand = "sed -i 's/" + pattern + "/" + newValue + "/g' " + file

# 	#print(comand)
# 	# Send command to terminal
# 	x = os.popen(comand).read()
# 	print(x)
	
# # Function that copy a file
# def copyFile(sourceFile,newFile):
# 	# Create sed command for copy a file
# 	cmd = "sed -n 'p' " + sourceFile + ">"  + newFile

# 	print(cmd)
# 	# Send command to terminal
# 	os.system(cmd)


# # Function that returns the pattern in the file from the dictionary key
# # TO TAKE INTO ACCOUNT --> Change if patterns are changed in the templates
# # Actual pattern --> <KEY>
# def key2pattern(var):
# 	pattern = "<" + var + ">"
# 	print("Pattern: " + pattern)
# 	return pattern

# def configureElement(template,newFileName,values):
# 	# Create a copy of the template -> It will be the new conf file
# 	#newFileName = file[:file.find("template")] + "ue" + str(values["UEID"]) +".conf" 
# 	print("Template file --> " + template)
# 	print("New file --> " + newFileName)
# 	copyFile(template, newFileName)

# 	# Iterate on all parameters
# 	for key in values.keys():
# 		val = values[key]
# 		if (type(val) is not str):
# 			val = str(val)
# 		# Replace value in the template's copy
# 		replaceTextSed(newFileName, key2pattern(key), val)

# 	return newFileName





# def getIPInterface(interface, netspace = None):
# 	# Build command for searching ip
# 	# We use ifconfig <interfaceName> to show the values of such interface
# 	# Grep is used to only show inet property

# 	lsb = lsb_release.get_lsb_information()
# 	osRelease = lsb["RELEASE"]

# 	# Ubuntu 16.04 shows ip addr with the form inet addr: 127.0.0.1
# 	if osRelease == "16.04":
# 		query = "inet addr:"
# 	else: 
# 		query = "inet "

# 	#cmdB = "ifconfig " + interface + "| grep 'inet '"	
# 	cmdB = "ifconfig " + interface + "| grep '" + query + "'"

# 	# Create command for netspace if it is introduced as input
# 	if netspace != None:
# 		cmd = "ip netns exec " + netspace + " " + cmdB
# 	else:
# 		cmd = cmdB

	
# 	print("Getting IP from interface " + interface)
# 	# Send command to terminal
# 	x= os.popen(cmd).read()
# 	#print(x)
# 	# Expected value (Ubuntu 18) --> inet 127.0.0.1 netmask 255.255.255.255	
# 	x = x[x.find("inet"):]
# 	response = x.split(" ")
# 	#print(response)

# 	if osRelease == "16.04":
# 		response = response[1].split(":")
# 	#print(response)
# 	# Ip value must be in the second field of the array
# 	ip = response[1]

# 	return ip



def getStatsFromPing(data):
	# Find line with statistics
	results = data.split("\n")
	index = 0
	res = dict()
	RTT_values = []
	for l in range(len(results)):
		if results[l].find("PING") != -1:
			data = results[l][results[l].find("PING") + len("PING"): results[l].find(")")].strip()
			res["ping_dest"] = data[:data.find("(")]
			res["ping_dest_ip"] = data[data.find("(")+1:]
		elif results[l].find("time=") != -1:
			rtt_value_str = results[l][results[l].find("time=") + len("time="):results[l].find(" ms")]
			RTT_values.append(float(rtt_value_str))
		elif results[l].find("statistics") != -1:
			#print(l)
			#print(results[l])
			index = l
	index = index + 1
	#print(RTT_values)
	try:
		stats = results[index].split(",")

		res["packetTransmited"] = int(stats[0].split(" ")[0])
		
		res["packetReceived"] = int(stats[1].split(" ")[1])

		res["packetLoss"] = stats[2].split(" ")[1]

		# The next line provides RTT metrics
		index = index + 1
		#print(results[index])
		stats = results[index].split("=")
		#print(stats)
		desc = stats[0].split(" ")[1].split("/")
		val = stats[1].split(" ")[1].split("/")
		#val = stats[1].split("/")

		for key in range(len(desc)):
			res["RTT_" + desc[key]] = float(val[key])
		res["RTT_values"] = RTT_values
		# There will be connectivity if at least one packet is received
		res["connectivity"] = res["packetReceived"] > 0
	except:
		res["connectivity"] = False
	return res

def getStatsPing_windows(data):
	# TODO: surrond each element with a exception
	# Find line with statistics
	results = data.split("\n")
	index = 0
	res = dict()
	RTT_values = []


	for l in range(len(results)):
		if results[l].find("Haciendo ping") != -1:

			data = results[l].split(" ")
			res["ping_dest"] = data[3].strip()

			if data[4].find("[") != -1:
				res["ping_dest_ip"] = data[4][1:-1].strip()
			else:
				res["ping_dest_ip"] = data[3].strip()

		elif results[l].find("tiempo=") != -1:
			rtt_value_str = results[l][results[l].find("tiempo=") + len("tiempo="):results[l].find("ms")]
			RTT_values.append(float(rtt_value_str))
		elif results[l].find("Estad") != -1:
			# print(l)
			# print(results[l])
			index = l
	index = index + 1
	# print(RTT_values)
	try:
		keys = ["Transmited", "Received", "Loss"]
		stats = results[index].split(",")
		for ind,k in enumerate(keys):
			try:
				res["packet"+k] = int(stats[ind].split("=")[1])
			except:
				res["packet" + k] = stats[ind].split("=")[1].strip()

		index += 1
		res["packetLoss_percentage"] = int(results[index][results[index].find("(")+1:results[index].find("%")])
		# The next line provides RTT metrics
		index += 2
		# print(results[index])

		stats = results[index].split(",")
		# print(stats)
		desc = ["min", "avg", "max"]


		for ind,key in enumerate(desc):
			ax = stats[ind].split("=")
			res["RTT_" + key] = float(ax[1][:-2])
		res["RTT_values"] = RTT_values
		# There will be connectivity if at least one packet is received
		res["connectivity"] = res["packetReceived"] > 0
	except:
		res["connectivity"] = False
	return res

def ping(ip, nPackets = 4, q = None):
	res = dict()
	#cmdB = "ping " +

	cmd = "ping " + ip

	# Regarding the platform, the flag of number of packets is different
	if platform.find("linux") != -1: # Linux
		cmd += " -c " + str(nPackets)
		t_init = time.time()
		x = os.popen(cmd).read()
		t_end = time.time()
		res = getStatsFromPing(x)

	elif platform.find("win") != -1: #Windows
		cmd += " -n " + str(nPackets)
		t_init = time.time()
		x = os.popen(cmd).read()
		t_end = time.time()
		res = getStatsPing_windows(x)

	res["t_init"] = t_init
	res["t_end"] = t_end

	if q != None:
		q.put(res)

	return res
