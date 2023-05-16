from utils.utils import *


getFromConsole("route delete 0.0.0.0 MASK 0.0.0.0 192.168.1.1")
getFromConsole("route delete 0.0.0.0 MASK 0.0.0.0 192.168.0.1")
#getFromConsole("route add 0.0.0.0 MASK 0.0.0.0 192.168.0.1  IF 24")
#getFromConsole("route add 0.0.0.0 MASK 0.0.0.0 192.168.8.1 metric 35 IF 20")
getFromConsole("route delete 192.168.1.0 MASK 255.255.255.0")
getFromConsole("route delete 192.168.0.0 MASK 255.255.255.0")
getFromConsole("route add 192.168.0.56 MASK 255.255.255.255 192.168.0.1 IF 27")
print(getFromConsole("route print -4").decode('utf-8'))
