
import sys
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import mouse
import traceback

from sys import platform
import numpy as np
from datetime import datetime
from progress.bar import Bar


DIVS = [1,2,3,4,5,9,10,11,12,15]
DIVS_NOT_ARRAY = [1, 5]
DIVS_NOT_ARRAY_LIVE = [1, 5,13]
#DIVS_ARRAY = [2,3,4,9,10,11,15]
DIVS_ARRAY = [2,3,4,9,10,11,12,15]
DIVS_ARRAY_LIVE =[2,3,4,9,10,11,12,15]
DIV_TO_KEY = {}
DIV_TO_KEY_LIVE = {}


RES= {'144':'144p', 
     '240' : '240p',
     '360': '360p',
     '480': '480p',
     '720': '720p',
     '1080': '1080p',
     '1440': '2K',
     '2160': '4K',
     '4320': '8K'}


PLAY_STATUS = {
    "4": "PAUSE",
    "8": "PLAYING"
}

STATS = [
    "Video ID", "sCPN", "Codecs",
     "Resolution",
     "FPS",
     "Resolution_received",
     "FPS_received",
     "Resolution_optimal",
     "FPS_optimal",
     "Frames_dropped",
     "Frames_total",
     "Frames_dropped_ratio",
     "Volume",
     "Volume_normalized",
     "Volume_content_loudness",
     "Connection_speed",
     "Connection_speed_units",
     "Network_activity",
     "Network_activity_units",
     "Buffer_health",
     "Buffer_health_units",
     "Ad",
     "Play_state",
     "Play_time",
     "Buffer_stored_init",
     "Buffer_stored_end"
]

LOG_LEVELS = ["debug", "error", "info", "disable"]

class YouTube(object):

    # def __init__(self, video, duration,interval=1, resolution = "Auto", logLevel = "info"):
    #     self.video = video
    #     self.playback_seconds = self.get_sec_from_time_str(video['duration'])
    #     self.availableResolutions = []
    #     self.resolution = resolution
    #     self.interval = interval
    #     self.logLevel = logLevel
    #
    #     if (self.playback_seconds < duration or self.duration == -1):
    #         self.duration = self.playback_seconds
    #     else:
    #         self.duration = durat
    #
    #     prYoutube = False
    #     while not prYoutube:
    #         self.driver = self.__prepareDriver()
    #         prYoutube = self.prepareYoutube()
    #     self.__print("Youtube is ready")

    def __init__(self, **kwargs):


        self.video = None


        if "logLevel" in kwargs:
            self.logLevel = kwargs["logLevel"]
        else:
            self.logLevel = "info"
        
        if "url" in kwargs:
            # get video in pool
            self.video = self.getVideoObject(url = kwargs["url"])

        elif "videoIndex" in kwargs:

            self.video = self.getVideoObject(index = kwargs["videoIndex"])


        if self.video != None:
            self.playback_seconds = self.get_sec_from_time_str(self.video['duration'])
            self.availableResolutions = self.video["resolutions"]
        else:
            self.playback_seconds = 0
            self.availableResolutions = [value for key, value in RES.items()]


        if "interval" in kwargs:
            self.interval = kwargs["interval"]
        else:
            self.interval = 1

        if "resolution" in kwargs:
            self.resolution = kwargs["resolution"]
        else:
            self.resolution = "Auto"




        if "duration" in kwargs:
            duration = kwargs["duration"]
        else:
            duration = -1
        self.duration = self.__setDuration(duration)
        # Youtube Preambule
        prYoutube = False
        while not prYoutube:
            self.driver = self.__prepareDriver(headless=False)
            prYoutube = self.prepareYoutube()
        self.__print("Youtube is ready")

        #time.sleep(90000)

    def __setDuration(self,duration):
        if self.playback_seconds != 0:
            if (self.playback_seconds < duration or duration == -1):
                duration = self.playback_seconds
            else:
                duration = duration
        else:
            duration = 60

        return duration
        
    def __getIndexPoolByURL(self, url):
        # Check if there is a video object created in the pool file
        with open("./videoPool.json", encoding="utf-8") as videofile:
            videoPool = json.load(videofile)

        for index, video in enumerate(videoPool):
            if video["url"] == url:
                return index

        return -1

    def getVideoObject(self, **kwargs):
        if "url" in kwargs:
            # get video in pool
            video = self.__getVideofromPool(url=kwargs["url"])
            if video == None:
                # If video is None, it will mean that it is not in the pool --> should be made an object
                video = self.createVideoObject(url =kwargs["url"])
        elif "index" in kwargs:
            video = self.__getVideofromPool(index=kwargs["index"])
        return video
    def __getVideofromPool(self,**kwargs):
        # Return video object with index given as input from the video pool file
        try:
            with open("./videoPool.json", encoding="utf-8") as videofile:
                videoPool = json.load(videofile)

            if "index" in kwargs:
                if kwargs["index"] < len(videoPool):
                    return videoPool[kwargs["index"]]
                else:
                    # If index is out of range, first video will be taken.
                    self.__print("Index out of range --> Video 0 from pool is taken")
                    return videoPool[0]
            elif "url" in kwargs:
                for index, video in enumerate(videoPool):
                    if video["url"] == kwargs["url"]:
                        return video
                return None
        except:
            return None

    def addVideo2Pool(self,video):

        if self.__getVideofromPool(url=video["url"]) != -1:
            try:
                with open("./videoPool.json", encoding="utf-8") as videofile:
                    videoPool = json.load(videofile)
            except:
                videoPool = []
            vd = {"index" : len(videoPool)}
            vd.update(video)
            videoPool.append(vd)
            with open("./videoPool.json", "w",encoding="utf-8") as videofile:

                json.dump(videoPool, videofile, indent = 4)

    def createVideoObject(self, url):

        # TODO some improvements: Check if the video is valid (i.e., can be played...)
        self.__print("Getting Video Information")
        prevLog = self.logLevel
        self.logLevel = "disable"
        videoInfo = dict()
        videoInfo["url"] = url
        prYoutube = False
        while not prYoutube:
            self.driver = self.__prepareDriver()
            prYoutube = self.prepareYoutube()

        self.__print("Youtube is ready")


        self.driver.get(url)
        time.sleep(1)
        self.__print("Enabling stats...", endl=" --> ")
        # Create an attempt every 1 second until enable the stats
        cont = 0
        while (not self.enable_stats()):
            time.sleep(1)
            cont += 1
            if cont == 20:
                self.__print("False")
                self.__print("Stats can't be enabled. Restarting the driver...", level="info")
                self.quit()
                return False

        title = self.driver.find_element_by_xpath("//*[@id=\"title\"]/h1").text
        videoInfo["title"] = title

        self.__print("Title: " + title, level="debug")
        videoID = self.__get_video_id(url)


        contAD = 0
        while self.get_notPeriodical_stats()["Video ID"].strip() != videoID:
            if self.isADs():
                self.__print("AD displaying", level="debug")

                self.skipAd()
                contAD += 1
            else:
                print("No AD")
            time.sleep(1)


        duration = self.driver.find_element_by_class_name("ytp-time-duration").text
        live = self.driver.find_element_by_class_name("ytp-live-badge").text

        if duration == "":
            self.__print("Not VOD", level="debug")
            if live != "":
                self.__print("Live Streaming", level="debug")
                videoInfo["type"] = "LiveStreaming"
            else:
                videoInfo["type"] = "Unknown"
                self.__print("Something wrong", level="debug")

            videoInfo["duration"] = -1
        else:
            videoInfo["type"] = "VOD"
            self.__print("Duration -- " + duration, level="debug")
            videoInfo["duration"] = duration

        self.__dropDownQualityMenu(videoID=videoID)
        availRes,_  = self.__getAvailableResolutions()


        videoInfo["resolutions"] = availRes
        videoInfo["AD"] =  contAD > 0

        self.logLevel = prevLog

        return videoInfo





    def __print(self,msg,level = "info", endl = "\n"):
        # TODO: Implement logging python
        if self.logLevel != "disable":
            if self.logLevel == "debug":
                print(msg, end=endl, flush=True)
            elif level == self.logLevel:
                print(msg, end=endl, flush=True)

    def __errorLog(self,msg):
        with open('errorLog.txt', 'a') as file_obj:
            now = datetime.now()
            try:
                date_time = now.strftime("%m/%d/%Y - %H:%M:%S")
                file_obj.write("\n")
                file_obj.write(date_time + ": " + msg)
                file_obj.write("\n")
            except:
                pass

    def __prepareDriver(self, headless = False):
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

        #chrome_options.add_argument("--auto-open-devtools-for-tabs")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("log-level=3")

        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=3840,2160")

        dir_path = "./chromedriver"
        if platform.find("linux") != -1:  # Linux
            dir_path += "/linux/chromedriver"
        elif platform.find("win") != -1:  # Windows
            dir_path += "/win/chromedriver.exe"


        browser = webdriver.Chrome(desired_capabilities=d, executable_path = dir_path, options = chrome_options)
        return browser

    def skipInitialPopup(self):

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
                nT = self.driver.find_element_by_xpath(xpathPolicy[counter%len(xpathPolicy)])
                nT.click()
                # If no exception arised, it means that the button has been clicked
                skip = True
                self.__print("Initial popup skipped", level="info")
                #print("Initial popup skipped")
            except:
                #self.__print(traceback.print_exc(),level="debug")
                # If some error occurred, create a new attempt
                self.__print("Trying to skip popup. Attempt " + str(counter), level = "debug")
                #print("Trying yo skip popup. Attempt " + str(counter))
                counter = counter + 1
                time.sleep(1)
        time.sleep(1)
        return skip

    def quitYoutubeUsePolicy(self):
        self.__print("Quitting Youtube Terms of use", level = "info")
        time.sleep(2)
        mouse.move(885, 630, absolute=True)
        mouse.click()
        time.sleep(0.5)

    def quitControlNotice(self):
        self.__print("Quitting Notify of Automation", level = "info")
        mouse.move(1252,89,absolute = True)
        time.sleep(0.5)
        mouse.click()
        time.sleep(0.5)

    def quitCookies(self):
        xpath = "/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[1]/a/tp-yt-paper-button"
        nT = self.driver.find_element_by_xpath(xpath)
        nT.click()
        skip = False  # Flag to know if the skipping has been done
        counter = 0  # Counter to set an attempt limit
        while not skip and counter < 45:
            try:
                # Try to get the button to skip the popup. The attempts will be alternating between the known buttons
                nT = self.driver.find_element_by_xpath(xpath)
                nT.click()
                # If no exception arised, it means that the button has been clicked
                skip = True
                self.__print("Cookies rejected", level="info")
            except:
                # If some error occurred, create a new attempt
                counter = counter + 1
                time.sleep(1)

        return skip

    # This function returns is the obtained stats are from an ad
    def statsFromAD(self, stat_dict):
        try:
            data = stat_dict['Mystery Text']
            if (data.find("vd:g") != -1):
                return True
            else:
                return False
        except:
            self.__print("Can not check if it is an Ad", level = "info")
            self.__(traceback.print_exc(), level = "debug")
            return False

    def isADs(self):

        adElements = ["ytp-ad-preview-container", "ytp-ad-preview-text", "ytp-ad-skip-button"]

        # ytp-ad-preview-container -- corresponds to the countdown container to skip the ad
        # ytp-ad-preview-text -- corresponds to the spam that notify that the video will play after the ad (no skip is possible)
        # ytp-ad-skip-button -- corresponds to the button to skip the ad

        # if one of these elements is reached by selenium means that there is an ad.
        self.__print("Checking if there is an AD", level="debug")
        isAd = False

        for element in adElements:
            try:
                self.__print("Checking element --> " + element , level="debug")
                e = self.driver.find_elements_by_class_name(element)[0]
                self.__print(e, level="debug")
                isAd = True
                break
            except:
                pass

        return isAd
    def skipAd(self):
        buttonClass = "ytp-ad-skip-button"
        find = False
        while(not find):
            try:
                skipButton = self.driver.find_elements_by_class_name(buttonClass)[0]

                skipButton.click()
                find = True
            except:
                if not self.isADs():
                    self.__print("There is not ad to skip --> Leaving skipAD function", level = "debug")
                    break
                #time.sleep(1)

        self.__print("Ad skipped", level = "info")
        return find

    def prepareYoutube(self):
        # Load YouTube
        self.__print("Getting Youtube's website", level = "info")
        self.driver.get("https://www.youtube.com/watch?v=rpeOOYpvEuo") # Video used for enabling stats (it has ads)

        #self.quitCookies()
        # Skip initial popup
        playerReady = self.skipInitialPopup()

        # If player is not ready, quit driver and return false
        if not playerReady:
            self.__print("Couldn't skip first popup, restarting the driver...", level = "info")
            self.quit()
            time.sleep(1)
            return playerReady
        
            

        # Enable stats
        self.__print("Enabling stats...", endl=" --> ")
        # Create an attempt every 1 second until enable the stats
        cont = 0
        while (not self.enable_stats()):
            time.sleep(1)
            cont += 1
            if cont == 20:
                self.__print("False")
                self.__print("Stats can't be enabled. Restarting the driver...", level = "info")
                self.quit()
                return False

        self.__print("True")
        #time.sleep(1)
        # Return to YouTube main website
        self.click_YoutubeLogo()


        return True

    def searchVideo(self,title):
        #search = self.driver.find_element_by_xpath("/html/body/ytd-app/div/div/ytd-masthead/div[3]/div[2]/ytd-searchbox/form/div/div[1]/input")

        path = "/html/body/ytd-app/div[1]/div/ytd-masthead/div[4]/div[2]/ytd-searchbox/form/div[1]/div[1]/input"
        search = self.driver.find_element_by_xpath(path)
        search.send_keys(title)

        #fxpathSearch = "/html/body/ytd-app/div/div/ytd-masthead/div[3]/div[2]/ytd-searchbox/button"
        fxpathSearch = "/html/body/ytd-app/div[1]/div/ytd-masthead/div[4]/div[2]/ytd-searchbox/button"

        searchButton = self.driver.find_element_by_xpath(fxpathSearch)
        searchButton.click()
        time.sleep(2)
        fxpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div[2]/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[1]/div/h3/a"
        fxpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[1]"
        fxpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[1]/div/h3/a"


        fxpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[%VIDEOINDEX]/div[1]/div/div[1]/div/h3/a"

        sV = False
        self.__print("Searching video",endl= "--> ")
        count = 0
        print(self.video["title"])
        while not sV and count <3:
            self.__print(".", level="debug", endl= " ")
            try:
                for i in range(1,10):
                    fxp_aux = fxpath.replace("%VIDEOINDEX", str(i))
                    videoElement = self.driver.find_element_by_xpath(fxp_aux)
                    #print(videoElement.text)
                    #s  time.sleep(1)
                    if videoElement.text == self.video["title"]:
                        sV = True
                        break

                if not sV:
                    return False
                #     fxp_aux = fxpath.replace("%VIDEOINDEX", str(1))
                #     videoElement = self.driver.find_element_by_xpath(fxp_aux)
                #     sV = True
            except:
                searchButton.click()
                time.sleep(1)
            finally:
                count +=1
                #traceback.print_exc()
                time.sleep(2)
        
        if count <7:
            videoElement.click()
            self.__print("Video has been found!")
            return True
        else:
            
            self.__print("Video not found")
            search.clear()
            

            return False
        

    def click_YoutubeLogo(self):
        try:
            self.__print("Clicking on Youtube Logo")
            xpath = "/html/body/ytd-app/div/div/ytd-masthead/div[3]/div[1]/ytd-topbar-logo-renderer/a"
            ytLogo = self.driver.find_element_by_xpath(xpath)
            #print("Getting youtube logo path:")
            #print(ytLogo)
            ytLogo.click()
        except:
            self.__print("Something went wrong when clicking on Youtube Logo")
        
    def __get_video_id(self, url):
        return url.split("=")[1].strip()
    
    def get_sec_from_time_str(self,time_str):
        
        try:
            timestr = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(time_str.split(":"))))
        except:
            if time_str == -1:
                timestr = -1
        return timestr

    def set_newVideo(self,video):
        self.video = video
        self.playback_seconds = self.get_sec_from_time_str(video['duration'])
    def load_video(self):
        self.__print("Loading url: " + self.video["url"])
        self.driver.get(self.video["url"])
        return True

    def set_keys(self):
        for div_id in DIVS:
            key = self.driver.find_element_by_css_selector(".html5-video-info-panel-content > div:nth-child(%d) > div:nth-child(1)"%div_id).text
            #print(div_id,key)
            #Populate DIV_TO_KEY dict
            DIV_TO_KEY[div_id] = key
            #DIV_TO_KEY_LIVE[div_id] = key
        # LIVE DIV KEY -- latency video (i.e., key index 12) and live mode (i.e., key index 13) are manually added
        #DIV_TO_KEY_LIVE[12] = "Live Latency"
        #DIV_TO_KEY_LIVE[13] = "Live Mode"
        DIV_TO_KEY[12] = "Live Latency"
        DIV_TO_KEY[13] = "Live Mode"

    def enable_stats(self):
        # Find player
        movie_player = self.driver.find_element_by_id('movie_player')
        self.hover = ActionChains(self.driver).move_to_element(movie_player)
        self.hover.perform()

        # Click on settings button
        ActionChains(self.driver).context_click(movie_player).perform()
        options = self.driver.find_elements_by_class_name('ytp-menuitem')

        # Among the different options, click on Stats for nerds
        for option in options:
            option_child = option.find_element_by_class_name('ytp-menuitem-label')
            if option_child.text == "Estadísticas para nerds" or option_child.text == "Stats for nerds":
                option_child.click()
                self.set_keys()
                return True
            self.__print(option_child.text, level = "debug")
        return False


    # Return in a dictionary both periodical and not periodical stats
    def get_all_stats(self):
        stats = dict()
        stats.update(self.get_notPeriodical_stats())
        stats.update(self.get_periodical_stats())
        return stats

    # Return in a dict the metrics which are changing along the time (Defined in DIVS_ARRAY)
    def get_periodical_stats(self):
        stat_dict = dict()
        for div_id in DIVS_ARRAY:
            elem = self.driver.find_element_by_css_selector(".html5-video-info-panel-content > div:nth-child(%d) > span:nth-child(2)"%div_id)
            stat_dict[DIV_TO_KEY[div_id]] = elem.text
        return self.formatingData(stat_dict)

    def get_periodical_liveStats(self):

        stat_dict = dict()
        for div_id in DIVS_ARRAY_LIVE:
            try:
                elem = self.driver.find_element_by_css_selector(".html5-video-info-panel-content > div:nth-child(%d) > span:nth-child(2)"%div_id)
                stat_dict[DIV_TO_KEY[div_id]] = elem.text
                #self.__print(str(div_id) + ":" +elem.text, level="debug")
                #self.__print(DIV_TO_KEY[div_id] + ":" + elem.text, level ="debug")
            except:
                self.__print(traceback.print_exc(),level="debug")
                self.__print("Something wrong getting periodical live stats", level = "info")
        return self.formatingData(stat_dict)

    # Return in a dict the metrics which don't change along the time (Defined in DIVS_NOT_ARRAY)
    def get_notPeriodical_stats(self):
        stat_dict = dict()
        for div_id in DIVS_NOT_ARRAY:
            elem = self.driver.find_element_by_css_selector(".html5-video-info-panel-content > div:nth-child(%d) > span:nth-child(2)"%div_id)
            stat_dict[DIV_TO_KEY[div_id]] = elem.text

        stat_dict = self.expandDict(stat_dict)
        stat_dict['samplesInterval'] = self.interval
        stat_dict['availableResolutions'] = self.availableResolutions
        return stat_dict


    # Expanding and formatting python dictionary given as input
    def formatingData(self,stat_dict):
        #self.__print(stat_dict, level = "debug")
        try:
            # Split double keys
            stat_dict = self.expandDict(stat_dict)
            stats = dict()
            # Formatting and renaming keys
            stats.update(self.getVideoValues(stat_dict)) # Video values (Resolution, Frames, Volume)
            stats.update(self.getStreamingValues(stat_dict)) # Streaming values (Network activity, Buffer health, play status, live latency)
            stats.update(self.getPlayerValues(stat_dict)) # Player values (Status, playback time, video stored)


        except:
            traceback.print_exc()
        return stats


    # This fuction returns all the information related with the played video
    def getVideoValues(self,stat_dict):
        stats = dict()

        # Viewport
        data = self.resolutionValues(stat_dict['Viewport'])
        stats['Resolution_player'] = data["Resolution"]
        # Current display
        data = self.resolutionValues(stat_dict['Current'])
        stats['Resolution_displayed'] = data["Resolution"]
        #stats['FPS_received'] = data["FPS"]

        # Optimal Resolution
        data = self.resolutionValues(stat_dict['Optimal Res'])
        stats['Resolution_optimal'] = data["Resolution"]
        stats['FPS_optimal'] = data["FPS"]

        # Frames
        data = stat_dict['Frames']
        try:
            stats['Frames_dropped'] = int(data[:data.find("dropped")]) # Dropped
            stats['Frames_total'] = int(data[data.find("of") + 2:]) # Total Frames
            stats['Frames_dropped_ratio'] = stats['Frames_dropped']/stats['Frames_total']
        except:
            stats['Frames_dropped'] = 0
            stats['Frames_total'] = 0 # Total Frames
            stats['Frames_dropped_ratio'] = 0
        # Volume
        stats['Volume'] = int(stat_dict['Volume'].split("%")[0])
        data = stat_dict["Normalized"].strip().split("%")
        
        try:
            stats['Volume_normalized'] = int(data[0])
            stats["Volume_content_loudness"] = float(data[1][data[1].find("loudness")+9:-3])
        except:
            stats['Volume_normalized'] = data[0]
            stats["Volume_content_loudness"] = data[1][data[1].find("loudness")+9:-3]

        return stats

    # This function returns information related with the video streaming
    def getStreamingValues(self,stat_dict):
        stats = dict()

        # Connection Speed
        data = stat_dict['Connection Speed'].split(" ")
        try:
            stats['Connection_speed'] = int(data[0])
        except:
            stats['Connection_speed'] = data[0]



        # Network activity
        data = stat_dict['Network Activity'].split(" ")
        try:
            stats['Network_activity'] = int(data[0])
        except:
            stats['Network_activity'] = data[0]


        # Buffer health
        data = stat_dict['Buffer Health'].split(" ")
        try:
            stats['Buffer_health'] = float(data[0])
        except:
            stats['Buffer_health'] = data[0]

        # Live latency
        try:
            data = stat_dict['Live Latency']
            try:
                stats['Live_latency'] = float(data[:-1])
            except:
                stats['Live_latency'] = data[0]
        except:
            # This exception means that there is not a Live latency field in the data, thus, it is not live streaming
            pass
        return stats

    # This function returns information related with the youtube player
    def getPlayerValues(self,stat_dict):
        try:
            stats = dict()
            data = stat_dict['Mystery Text'].split(" ")
            index = 0
            stats["Ad"] = False
            if (self.statsFromAD(stat_dict)):
                index += 1
                stats["Ad"] = True 
                
            # Status playback
            state = data[index].split(":")

            try:
                stats['Play_state'] = PLAY_STATUS[state[1]]
            except:
                
                stats['Play_state'] = "Unknown"
            
            # Play time
            index += 1
            time = data[index].split(":")
            try:
                stats['Play_time'] = float(time[1])
            except:
                try:
                    stats['Play_time'] = time[1]
                except:
                    stats['Play_time'] = -1
            # Video interval stored in buffer
            index += 1
            buf = data[index].split(":")
            bufInterval = buf[1].split("-")
            try:
                stats['Buffer_stored_init'] = float(bufInterval[0])
                stats['Buffer_stored_end'] = float(bufInterval[1])
            except:
                try:
                    stats['Buffer_stored_init'] = bufInterval[0]
                    stats['Buffer_stored_end'] = bufInterval[1]
                except:
                    stats['Buffer_stored_init'] = -1
                    stats['Buffer_stored_end'] = -1
        except:
            self.__print("Something wrong in getPlayerValues")
            traceback.print_exc()
            self.__print(data, level = "debug")


        return stats


    def expandDict(self, stat_dict):
        newDict = dict()
        for x in stat_dict:
            if (x.find("/") != -1):
                keys = x.split("/")
                val = stat_dict[x].split("/")
                for k in range(len(keys)):
                    newDict[keys[k].strip()] = val[k].strip()
            else:
                newDict[x] = stat_dict[x]
        return newDict
   
    def collect_stats(self):
        stat_dict = dict()
        try:

            # while(self.get_notPeriodical_stats()["Video ID"].strip() != self.video["videoID"].strip()):
            #     # It is not the video that we want to play
            #
            #     if (self.isADs()):
            #         self.__print("Ad detected")
            #         self.skipAd()
            #     else:
            #         self.__print("No ad detected")
            #         self.__print("Current videoID -->  " + self.get_notPeriodical_stats()["Video ID"], level = "debug")
            #         self.__print("Expected videoID --> " + self.video["videoID"], level = "debug")
            #
            #         self.__print("Same videoID? --> " + str(self.get_notPeriodical_stats()["Video ID"].strip() == self.video["videoID"].strip()) , level="debug")
            #         time.sleep(0.5)
            n = self.duration
            self.__print("duration -->" + str(n), level="debug")
            self.time_init = time.time()
            self.__print("Starting collecting stats (it'll take approximately %d seconds)" % (n))
            stat_dict["timestamp_sample"] = []
            with Bar("Collecting stats", fill="#", max=n) as bar:
                for i in range(n):
                    try:
                        start = time.time()
                        if i % 2 == 0:
                            self.hover.perform()
                        aux_dict = self.get_periodical_stats()
                        
                        stat_dict["timestamp_sample"].append(time.time())
                        for x in aux_dict:
                            # First time, dictionary field must be initialized
                            if (i == 0):
                                stat_dict[x] = [aux_dict[x]]
                            else:
                                # Sometimes, when the connection isn't quite good, some keys are missing, producing an error
                                # at the time of appending the value to the dictionary field.
                                try:
                                    stat_dict[x].append(aux_dict[x])
                                except:
                                    # When this error happens, adding values
                                    self.__errorLog("Error collecting stats")
                                    self.__print("Error collecting stats")
                                    error = sys.exc_info()
                                    msg = str(error[1])
                                    self.__print(msg, level = "debug")
                                    self.__errorLog(msg)
                                    ln = len(stat_dict[list(aux_dict.keys())[0]])
                                    auxList = ln * [aux_dict[x]]
                                    stat_dict[x] = auxList
                        

                    except:
                        # Sometimes when the connection isn't quite good, some keys are missing, creating an error.
                        # In that case, we avoid and fill the samples later.
                        self.__print("x",level="debug")
                    finally:
                        time_taken = time.time()-start
                        #print("Time taken",time_taken)
                        time.sleep(max(0,self.interval - time_taken))
                        bar.next()
        except:
            self.__errorLog("Error collecting stats (point 2)")
            self.__errorLog(traceback.print_exc())
            return self.create_new_stat_dict()
        print("\n")
        self.time_end = time.time()
        stat_dict.update(self.getStatsFromPeriodicalData(stat_dict))
        stat_dict.update(self.get_notPeriodical_stats())


        return stat_dict

    def collect_liveStats(self):
        stat_dict = dict()
        try:


            #while (self.get_notPeriodical_stats()["Video ID"].strip() != self.video["videoID"].strip()):
                # It is not the video that we want to play

            if (self.isADs()):
                self.__print("Ad detected")
                self.skipAd()

            n = self.duration

            self.time_init = time.time()
            self.__print("Starting collecting stats (it'll take approximately %d seconds)" % (n))
            stat_dict["timestamp_sample"] = []
            with Bar("Collecting stats", fill="#", max=n) as bar:
                for i in range(n):
                    try:
                        start = time.time()
                        if i % 2 == 0:
                            self.hover.perform()
                        aux_dict = self.get_periodical_liveStats()

                        stat_dict["timestamp_sample"].append(time.time())
                        for x in aux_dict:
                            # First time, dictionary field must be initialized
                            if (i == 0):
                                stat_dict[x] = [aux_dict[x]]
                            else:
                                # Sometimes, when the connection isn't quite good, some keys are missing, producing an error
                                # at the time of appending the value to the dictionary field.
                                try:
                                    stat_dict[x].append(aux_dict[x])
                                except:
                                    # When this error happens, adding values
                                    self.__errorLog("Error collecting stats")
                                    self.__print("Error collecting stats")
                                    error = sys.exc_info()
                                    msg = str(error[1])
                                    self.__print(msg, level="debug")
                                    self.__errorLog(msg)
                                    ln = len(stat_dict[list(aux_dict.keys())[0]])
                                    auxList = ln * [aux_dict[x]]
                                    stat_dict[x] = auxList


                    except:
                        # Sometimes when the connection isn't quite good, some keys are missing, creating an error.
                        # In that case, we avoid and fill the samples later.
                        self.__print("x", level="debug")
                    finally:
                        time_taken = time.time() - start
                        # print("Time taken",time_taken)
                        time.sleep(max(0, self.interval - time_taken))
                        bar.next()
        except:
            self.__errorLog("Error collecting stats (point 2)")
            self.__errorLog(traceback.print_exc())
            return self.create_new_stat_dict()
        print("\n")
        self.time_end = time.time()
        stat_dict.update(self.getStatsFromPeriodicalData(stat_dict))
        stat_dict.update(self.get_notPeriodical_stats())

        return stat_dict

    def getStatsFromPeriodicalData(self,data):
        d = dict()
        for x in ['Resolution_player', 'Resolution_displayed', 'Resolution_optimal']:
            aux = np.array(data[x])
            d[x+"_percentage"] = dict()
            d[x+"_time"] = dict()
            if x != "Resolution_player":
                for r in RES:
                    d[x + "_percentage"][RES[r]] = 0
                    d[x + "_time"][RES[r]] = 0
            unique, counts = np.unique(aux, return_counts=True)
            self.__print(x +" --> ", endl=" ")
            self.__print(unique)
            for r in range(len(unique)):
                d[x + "_percentage"][unique[r]] =  float(counts[r]/aux.size)*100
                d[x + "_time"][unique[r]] = int(counts[r]* self.interval)
        # Connection speed
        aux = np.array(data['Connection_speed'])
        d['avg_bitrate_connection'] = int(np.mean(aux))
        d['max_bitrate_connection'] = int(np.max(aux))
        d['min_bitrate_connection'] = int(np.min(aux))

        # Buffer health
        aux = np.array(data['Buffer_health'])
        d['avg_buffer_health'] = int(np.mean(aux))
        d['max_buffer_health'] = int(np.max(aux))
        d['min_buffer_health'] = int(np.min(aux))

        # Live latency (Only for the case of live streaming)
        try:
            aux = np.array(data['Live_latency'])
            d['avg_live_latency'] = int(np.mean(aux))
            d['max_live_latency'] = int(np.max(aux))
            d['min_live_latency'] = int(np.min(aux))
        except:
            pass

        # Network activity
        aux = np.array(data['Network_activity'])
        d['totalAmountNetworkData'] = int(np.sum(aux))

        # Initial time
        d.update(self.initialTime(data))
        # Time to fill buffer
        d.update(self.time2FillBuffer(data))

        # Freeze
        d.update(self.getStalls(data))

        d['TotalTime'] = int(aux.size * self.interval)
        return d


    def initialTime(self,data):
        playTime = np.array(data["Play_time"])



        # TODO: Check if they are consecutives

        #initialTime = len(np.where(playTime == 0)) *
        initialTime = float(np.count_nonzero(playTime == 0) * self.interval)


        return {"initialTime": initialTime}



    def time2FillBuffer(self,data):
        eb = np.array(data['Buffer_stored_end'], dtype = 'uint8')
        try:
            index = int(np.where(eb == self.playback_seconds)[0][0] * self.interval)
        except:
            # If an exception arises, it means that this value isn't in the array (so the whole video has not been stored in the buffer)
            index = -1

        return {"time2FillBuffer": index}

    def getStalls(self,data):
        res = dict()
        bH = np.array(data['Buffer_health'])

        hotPoints = bH[bH==0] # When buffer health is under 1s, freeze is supposed

        pt = np.array(data["Play_time"], dtype = 'uint8')


        # Number of freezes
        #res['freeze_number'] = len(hotPoints) * self.interval # Number of 0's in the buffer health
        res['freeze_number'] = (len(hotPoints) - len(pt[pt== self.playback_seconds]) )  # Number of 0's in the buffer health


        sTime = res['freeze_number'] * self.interval - self.initialTime(data)["initialTime"]

        # if (len(hotPoints) )> 0): # It means there are stalls
        #     for x in hotPoints:
        #         if (x >0): # Check if the buffer health is empty in a partial time of the previous interval
        #             pTime = max(self.interval - bH[x-1], 0) # Freeze in the previous interval where the stall have been initially detected
        #             sTime = sTime + (pTime + self.interval)  # stallTime will be the sum of the time in the previous interval + detection interval
        #         else:
        #             sTime = sTime + self.interval


        res['freeze_time'] = sTime

        return res

    def get_current_seek(self):
        elem = self.driver.find_element_by_css_selector(".ytp-time-current")
        return elem.text

    def loadVideo(self):
        self.__print("Loading video")
        while not self.searchVideo(self.video["title"]):
            self.__print("Trying to search video")
            self.click_YoutubeLogo()
            time.sleep(1)


        self.fullScreen()


    def checkTargetVideo(self):
        try:
            self.__print("Checking target video --> ", endl = " ")
            videoID = self.__get_video_id(self.video["url"])
            while (self.get_notPeriodical_stats()["Video ID"].strip() != videoID):
                # It is not the video that we want to play
                if (self.isADs()):
                    self.__print("Ad detected")
                    self.skipAd()
                else:
                    self.__print("No ad detected")
                    self.__print("Current videoID -->  " + self.get_notPeriodical_stats()["Video ID"], level="debug")
                    self.__print("Target videoID --> " + videoID, level="debug")

                    self.__print("Same videoID? --> " + str(
                        self.get_notPeriodical_stats()["Video ID"].strip() == videoID), level="debug")
                    time.sleep(0.5)
            self.__print("Target video is in the player")
        except:
            self.__print("Something wrong checking Target video", level="info")
            self.__print(traceback.print_exc(),level="debug")

    def __getMOS(self, kqi):


        Lti = kqi["initialTime"]  # initial Buffering time

        Lfr = kqi["freeze_number"] / kqi["TotalTime"]

        if kqi["freeze_number"] == 0:
            Ltr = 0
        else:
            Ltr = kqi["freeze_time"] / kqi["freeze_number"]  # avg stall duration


        MOS = 4.23 - 0.0672 * Lti - 0.742 * Lfr - 0.106 * Ltr

        if MOS < 1:
            MOS = 1

        return MOS
    def play(self, queue = None):
        try:
            self.loadVideo()
            if not self.select_resolution():
                # If resolution can't be set, load video again
                self.loadVideo()

            time.sleep(1)

            # Check if the video playing is the target
            self.checkTargetVideo()

            # Collect stats from Youtube player
            kqi = self.collect_stats()

            kqi["mos"] = "-1"
            if self.resolution != "Auto":
                kqi["mos"] = self.__getMOS(kqi)
                print("MOS: " + str(kqi["mos"]))
            kqi["videoPlayed"] = self.video
            kqi["availableResolutions"] = self.availableResolutions
            kqi["resolution"] = self.resolution
            kqi["time_init"] = self.time_init
            kqi["time_end"] = self.time_end
        except:
            self.__print("Something wrong playing the video")
            self.__print(traceback.print_exc(),level = "debug")
            kqi = {}

        if queue != None:
            queue.put(kqi)
        return kqi


    def create_new_stat_dict_array(self):
        stat = {}

        for div_id in DIVS_ARRAY:
            key = self.driver.find_element_by_css_selector(".html5-video-info-panel-content > div:nth-child(%d) > div:nth-child(1)"%div_id).text
            stat[key] = []
            
            #Populate DIV_TO_KEY dict
            DIV_TO_KEY[div_id] = key
        return stat
    def create_new_stat_dict(self):
        stat = {}

        for div_id in DIVS:
            key = self.driver.find_element_by_css_selector(".html5-video-info-panel-content > div:nth-child(%d) > div:nth-child(1)"%div_id).text
            #stat[key] = None
            stat[key] = None
            #print(div_id,key)
            #Populate DIV_TO_KEY dict
            DIV_TO_KEY[div_id] = key
        return stat





    # Get resolution and fps from a string given as an input
    def resolutionValues(self,values):
        if(values.find("@") != -1):
            data = values.split("@")
            try:
                fps = int(data[1])
            except:
                fps = data[1].strip()
        elif(values.find("*") != -1):
            data = values.split("*")
            fps = None
        else:
            data = [values]
            fps = None
        
        try:
            resolution = RES[data[0].split('x')[1]]
        except:
            resolution = data[0].split('x')[1]
        return {'Resolution':resolution, 'FPS': fps}


    def fullScreen(self):
        fullscreen = False
        while(not fullscreen):
            try:
                sb = self.driver.find_element_by_class_name('ytp-fullscreen-button')
                sb.click()
                fullscreen = True
            except:
                fullscreen = False
            

    def delete_cache(self):
        self.driver.execute_script("window.open('');")
        time.sleep(1)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(1)
        self.driver.get('chrome://settings/clearBrowserData')
        time.sleep(1)
        actions = ActionChains(self.driver) 
        actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3) # send right combination
        actions.perform()
        time.sleep(1)
        actions = ActionChains(self.driver) 
        actions.send_keys(Keys.TAB * 4 + Keys.ENTER) # confirm
        actions.perform()
        time.sleep(5) # wait some time to finish
        self.driver.close() # close this tab
        self.driver.switch_to.window(self.driver.window_handles[0]) # switch back
    


    def __dropDownQualityMenu(self, videoID):

        self.__print("Drop down quality menu", level="debug")
        while (self.get_notPeriodical_stats()["Video ID"] != videoID):
            # It is not the video that we want to play
            self.__print(self.get_notPeriodical_stats(), level="debug")

            if (self.isADs()):
                self.__print("Ad detected")
                self.skipAd()
            else:
                self.__print("No ad detected")
                time.sleep(1)

        clicked = False
        while (not clicked):
            try:
                sb = self.driver.find_element_by_css_selector('.ytp-button.ytp-settings-button')
                sb.click()
                clicked = True
            except:
                self.__print("Trying to click on player settings")
                time.sleep(1)
        self.__print("Click on settings button", level="debug",endl=" --> ")
        time.sleep(1)
        self.__print("Setting quality", level="debug",endl=" --> ")
        if self.isADs():
            self.skipAd()

        qMenu = False
        attempt = 0
        while not qMenu and attempt < 10:
            try:
                r = self.driver.find_element_by_xpath("//div[contains(text(), 'Calidad')]").click()
                qMenu = True
            except:
                try:
                    r = self.driver.find_element_by_xpath("//div[contains(text(), 'Quality')]").click()
                    qMenu = True
                except:
                    if self.isADs():
                        self.skipAd()
                    attempt += 1
                    self.__print("Cannot click on quality menu")
                    time.sleep(1)

        if attempt == 10 and not qMenu:
            self.__print("Setting quality --> False", level="debug")
            return False
        elif attempt > 0:
            self.__print("Setting quality --> True", level="debug")
        else:
            self.__print("True")
    def __getAvailableResolutions(self,resolution2set = "NO_SELECTED"):
        time.sleep(0.5)
        op = self.driver.find_elements_by_class_name("ytp-menuitem-label")
        fixRes = False

        self.__print("Resolution choose --> " + self.resolution)
        item2click = None
        availableRes = []
        self.__print("Available resolutions: ", level="info", endl=" ")
        for item in op:
            resol = item.text
            if resol != "":
                availableRes.append(self.__renameResolution(resol))
                self.__print(resol, level="info", endl=" ")
            if resol.find(resolution2set) != -1:
                item2click = item
                fixRes = True

        if fixRes:
            try:
                item2click.click()
                self.__print("Click on selected resolution: " + item2click.text)
            except:
                fixRes = self.select_resolution()

        self.__print(" ")
        return availableRes,fixRes

    def __renameResolution(self,res):
        renameRes = ["8K", "4K", "1440p", "1080p", "720p", "Auto"]
        for x in renameRes:
            if res.find(x) != -1:
                return x

        return res

    def select_resolution(self):
        if self.resolution != "Auto":
            self.__print("Choosing resolution")

            self.__dropDownQualityMenu(self.__get_video_id(self.video["url"]))

            self.availableResolutions, fixRes = self.__getAvailableResolutions(resolution2set=self.resolution)

            return fixRes

        else: # Auto
            return True

    def quit(self):
        self.driver.quit()
