from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from subprocess import call
import time
from utils import *
chrome_options = webdriver.ChromeOptions();
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
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("headless")



#-------------------Webdriver's path----------------------

dir_path = "/usr/bin/chromedriver"  #Linux
#dir_path = os.path.dirname(os.path.realpath(__file__)) + "/chromedriver/chromedriver.exe" #Windows

#-------------------Browser options-----------------------

d = DesiredCapabilities.CHROME
d['loggingPrefs'] = { 'browser':'ALL' }


browser = webdriver.Chrome(desired_capabilities=d,executable_path=dir_path, chrome_options=chrome_options) #LINUX

browser.get('http://192.168.8.1/html/reboot.html')

bReb = browser.find_element_by_id("button_reboot")
bReb.click()
time.sleep(1)
acept = browser.find_element_by_id("pop_confirm")
acept.click()
time.sleep(20)
while(not connectionAvailable()):
	#print("No hay conexión")
	time.sleep(1)

browser.quit()