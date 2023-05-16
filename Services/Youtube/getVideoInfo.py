import sys
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from sys import platform
from pyvirtualdisplay import Display
def prepareDriver():
        d = DesiredCapabilities.CHROME
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
        chrome_options.add_argument("--mute-audio")
        
        chrome_options.add_argument("--headless")

        dir_path = "./chromedriver"
        if platform.find("linux") != -1:  # Linux
            dir_path += "/linux/chromedriver"
        elif platform.find("win") != -1:  # Windows
            dir_path += "/win/chromedriver.exe"


        browser = webdriver.Chrome(desired_capabilities=d, executable_path = dir_path, options = chrome_options)
        return browser



def prepareYoutube(driver, url):
        # Load YouTube
        print("Getting Youtube's website")
        driver.get(url) # Video used for enabling stats (it has ads)

        #self.quitCookies()
        # Skip initial popup
        playerReady = skipInitialPopup(driver)

        # If player is not ready, quit driver and return false
        if not playerReady:
            print("Couldn't skip first popup, restarting the driver...")
            driver.quit()
            time.sleep(1)
            return playerReady
        
            
def get_video_id(url):
    return url.split("=")[1]
       
def skipInitialPopup(driver):

    # Sometimes the intial popup is different. The two more usual are included in the list
        xpathPolicy = []

        # Reject cookies
        xpathPolicy.append("/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div/div[6]/div[1]/ytd-button-renderer[1]/a/tp-yt-paper-button")
        xpathPolicy.append("/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[1]/a/tp-yt-paper-button")
        xpathPolicy.append("/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[1]/yt-button-shape/button")

        skip = False # Flag to know if the skipping has been done
        counter = 0 # Counter to set an attempt limit
        time.sleep(1)
        while not skip and counter < 30:
            try:
                # Try to get the button to skip the popup. The attempts will be alternating between the known buttons
                nT = driver.find_element_by_xpath(xpathPolicy[counter%len(xpathPolicy)])
                nT.click()
                # If no exception arised, it means that the button has been clicked
                skip = True
                print("Initial popup skipped")
                #print("Initial popup skipped")
            except:
                #self.__print(traceback.print_exc(),level="debug")
                # If some error occurred, create a new attempt
                print("Trying to skip popup. Attempt " + str(counter))
                #print("Trying yo skip popup. Attempt " + str(counter))
                counter = counter + 1
                time.sleep(1)
        time.sleep(1)
        return skip



#                 return fixRes
#             else: 
#                 # Auto
#                 return True
    # def isADs(driver):

    #     adElements = ["ytp-ad-preview-container", "ytp-ad-preview-text", "ytp-ad-skip-button"]

    #     # ytp-ad-preview-container -- corresponds to the countdown container to skip the ad
    #     # ytp-ad-preview-text -- corresponds to the spam that notify that the video will play after the ad (no skip is possible)
    #     # ytp-ad-skip-button -- corresponds to the button to skip the ad

    #     # if one of these elements is reached by selenium means that there is an ad.
    #     print("Checking if there is an AD")
    #     isAd = False

    #     for element in adElements:
    #         try:
    #             print("Checking element --> " + element)
    #             e = driver.find_elements_by_class_name(element)[0]
                
    #             isAd = True
    #             break
    #         except:
    #             pass

    #     return isAd
    #  def skipAd(driver):
    #     buttonClass = "ytp-ad-skip-button"
    #     find = False
    #     while(not find):
    #         try:
    #             skipButton = driver.find_elements_by_class_name(buttonClass)[0]

    #             skipButton.click()
    #             find = True
    #         except:
    #             if isADs():
    #                 print("There is not ad to skip --> Leaving skipAD function")
    #                 break
    #             #time.sleep(1)

    #     print("Ad skipped")
    #     return find
#display = Display(visible=0, size=(3840, 2160))
#display.start()

# url = "https://www.youtube.com/watch?v=WWZ9pNJrVy4"
# driver = prepareDriver()
# prepareYoutube(driver, url)
# print("Ready")
#
# # Title
# time.sleep(1)
# print(driver.find_element_by_xpath("//*[@id=\"title\"]/h1").text)
#
# # Vieo duration
# time.sleep(1)
#
# duration = driver.find_element_by_class_name("ytp-time-duration").text
# if duration =="":
#     print("Not VOD")
# else:
#     print("Duration -- " + duration)
# print(get_video_id(url))
#
# live = driver.find_element_by_class_name("ytp-live-badge").text
#
# if live =="":
#     print("Not Live")
# else:
#     print("Live")
# driver.quit()

from youtube import YouTube
import json


urls = ["https://www.youtube.com/watch?v=o_24LPjOIHI", "https://www.youtube.com/watch?v=RSxsi0ISKZQ",
        "https://www.youtube.com/watch?v=zFHxyMkJvRo", "https://www.youtube.com/watch?v=LXb3EKWsInQ",
        "https://www.youtube.com/watch?v=WjoplqS1u18"]

#yt = YouTube(video[4], 60)


for url in urls:
    yt = YouTube()
    vd = yt.getVideoObject(url = url)
    yt.addVideo2Pool(vd)
    print(vd)
    yt.quit()