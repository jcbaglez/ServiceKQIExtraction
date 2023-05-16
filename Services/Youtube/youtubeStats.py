from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import mouse
from datetime import datetime

DIVS = [1,2,3,4,5,9,10,11,12,15]
DIV_TO_KEY = {}
INTERVAL = 0.5

def enable_stats(browser):
    movie_player = browser.find_element_by_id('movie_player')
    hover = ActionChains(browser).move_to_element(movie_player)
    hover.perform()
    ActionChains(browser).context_click(movie_player).perform()
    options = browser.find_elements_by_class_name('ytp-menuitem')
    for option in options:
        option_child = option.find_element_by_class_name('ytp-menuitem-label')
        if option_child.text == 'Stats for nerds':
            option_child.click()
            print("Enabled stats collection.")
            return True
    return False 

def get_current_seek(driver):
    elem = driver.find_element_by_css_selector(".ytp-time-current")
    return elem.text

def get_stats(driver,stat_dict):
    stat_dict['Timestamp'] = time.time()
    stat_dict['Current Seek'] = get_current_seek(driver)
    for div_id in DIVS:
        elem = driver.find_element_by_css_selector(".html5-video-info-panel-content > div:nth-child(%d) > span:nth-child(2)"%div_id)
        stat_dict[DIV_TO_KEY[div_id]] = elem.text

    return stat_dict

def create_new_stat_dict(driver):
    stat = {}
    stat['Timestamp'] = None
    stat['Current Seek'] = None
    print("\nCollecting following stats...")
    for div_id in DIVS:
        key = driver.find_element_by_css_selector(".html5-video-info-panel-content > div:nth-child(%d) > div:nth-child(1)"%div_id).text
        stat[key] = None
        print(div_id,key)
            #Populate DIV_TO_KEY dict
        DIV_TO_KEY[div_id] = key
    return stat


def collect_stats(self):
    try:
        stat_dict = self.create_new_stat_dict()
        n = min(2*self.playback_seconds, self.config['number_of_data_points'])
        print("Started collecting... it'll take %d seconds." % (n/2))
        for i in range(n):
            start = time.time()
            if i % 2 == 0:
                self.hover.perform()
            self.get_stats(stat_dict)
            stat_dict['Ad'] = False
            self.flowfetch.post_video_stat(stat_dict)
            time_taken = time.time()-start
            #print("Time taken",time_taken)
            time.sleep(max(0,INTERVAL - time_taken))
        return True
    except Exception as e:
        print("Ecountered error while collecting stats", e)
        return False


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


dir_path = "C:/chromedriver/chromedriver.exe"
browser = webdriver.Chrome(desired_capabilities=d, executable_path = dir_path, options = chrome_options)
browser.get("https://www.youtube.com")

#browser.get("https://www.youtube.com/watch?v=NGYzZo4x0ec")

time.sleep(2)
xpathNT = "//*[@id=\"dismiss-button\"]/yt-button-renderer"
xpathNTF = "/html/body/ytd-app/ytd-popup-container/paper-dialog/yt-upsell-dialog-renderer/div/div[3]/div[1]/yt-button-renderer"
#xpathNTF = "/html/body/ytd-app/ytd-popup-container/paper-dialog/yt-upsell-dialog-renderer/div/div[3]/div[1]/yt-button-renderer/a"
try:
    nT = browser.find_element_by_xpath(xpathNTF)
except:
    time.sleep(5)
    try:
        nT = browser.find_element_by_xpath(xpathNTF)
    except:
        print("No buttom 1")
#nT = browser.find_element_by_id("dismiss-button")
print("isDisplayed 1?")
while (not nT.is_displayed()):
    time.sleep(1)
    print(nT.is_displayed())
nT.click()

time.sleep(3)
xpathNTF = "/html/body/div/c-wiz/div[2]/div/div/div/div/div[2]/form/div/div[2]"
id = "introAgreeButton"

#nT = browser.find_element_by_id("introAgreeButton")
#nT.click()
#while (not nT.is_displayed()):
#    time.sleep(1)
#    print(nT.is_displayed())
print(mouse.get_position())
mouse.move(885, 630, absolute=True)

time.sleep(2)
print(mouse.get_position())
mouse.click()

time.sleep(2)
browser.get("https://www.youtube.com/watch?v=YOYUXqR8T9g")


time.sleep(2)
enable_stats(browser)
statsD = create_new_stat_dict(browser)
res = get_stats(browser,statsD)
time.sleep(4)

print(res)
#nT.click()
#bufferXP = "/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[1]/div/div/div/ytd-player/div/div/div[24]/div/div[11]/span/span[2]"
#buff = browser.find_element_by_xpath(bufferXP)
#print(buff.text)
#time.sleep(2)
#print("nT:")
#print(nT)
#xpath ="//*[@id=\"movie_player\"]/div[19]"
#time.sleep(10)
#a = browser.get_element_by_xpath(xpath)
#print(a)