import os
import json
import mouse
import keyboard
import time
import mss
import numpy as np
from cloudGaming.Moonlight.metricas_fich import *
class Moonlight:

    def __init__(self,  **kwargs):

        if "moonlightPath" in kwargs:
            self.path = kwargs["moonlightPath"]
        else:
            self.path = "C:/Program Files/Moonlight Game Streaming/Moonlight.exe"

        if "coordinatesFile" in kwargs:
            coordFile = kwargs["coordinatesFile"]
        else:
            coordFile = "cloudGaming/Moonlight/coordinates/client_conf_labMSI4K.json"

        with open(coordFile) as file:
            # with open('cloudGaming/Moonlight/coordinates/client_conf_labMSI.json') as file:
            self.configClient = json.load(file)

        self.log_path = 'C:/Users/' + os.getlogin() + '/AppData/Local/Temp'  # Game path Host

        self.BITRATE_MOONLIGHT = self.__getDictBitrate()

    def __monitorInfo(self):
        return np.asarray(mss.mss().monitors)


    def __getDictBitrate(self):
        # Function to initialise dict with automatic bitrate according to Moonlight
        bitrate = dict()
        bitrate["720p"] = {"30": 5, "60": 10, "120": 20}
        bitrate["1080p"] = {"30": 10, "60": 20, "120": 40}
        bitrate["1440p"] = {"30": 20, "60": 40, "120": 80}
        bitrate["4K"] = {"30": 40, "60": 80, "120": 150}

        return bitrate



    def conf_Moonlight(self, resolution='1080p', framerate=30, bitrate = "Automatic"):
        print("Configuring Moonlight....")
        monitor = self.__monitorInfo() # To guarantee that actions will take place in the coordinates

        # Start Moonlight process
        self.start_moonlight_process()
        # Open configuration
        self.open_settings()

        # Configure Video Resolution
        self.conf_resolution(resolution)
        self.resolution = resolution

        # Configure FPS
        self.conf_fps(framerate)
        self.framerate = framerate

        # Bitrate
        if bitrate == "Automatic":
            bitrate = self.BITRATE_MOONLIGHT[resolution][str(framerate)]
        else:
            self.conf_bitrate(bitrate)

        # Finish configuration
        self.finish_configuration()


        print("Session has been configured:")
        print("Resolution --> " + resolution)
        print("Frame rate --> " + str(framerate) + " (FPS)")

        return {"resolution": resolution, "fps": framerate, "bitrate": bitrate}


    def start_moonlight_process(self):
        print('Moonlight Client is starting...')
        os.startfile(self.path)
        time.sleep(6)

    def open_settings(self):
        print('Moonlight Client is being configured...')
        mouse.move(self.configClient['Setting']['X'], self.configClient['Setting']['Y'])
        time.sleep(1)
        mouse.click()

    def finish_configuration(self):
        mouse.move(self.configClient['Return']['X'], self.configClient['Return']['Y'])
        time.sleep(0.5)
        mouse.click()
        time.sleep(0.5)
        self.stop_moonlight()


    def closeMoonlightInterface(self):
        mouse.move(self.configClient['CloseMoonlight']['X'], self.configClient['CloseMoonlight']['Y'])
        time.sleep(1)
        mouse.click()

    def conf_resolution(self, resValue):
        # Click on resolution menu
        mouse.move(self.configClient['Resolution']['X'], self.configClient['Resolution']['Y'])
        time.sleep(1)
        mouse.click()
        mouse.move(self.configClient[resValue]['X'], self.configClient[resValue]['Y'])
        time.sleep(1)
        mouse.click()

    def conf_fps(self, fpsValue):
        mouse.move(self.configClient['FPS']['X'], self.configClient['FPS']['Y'])
        time.sleep(1)
        mouse.click()
        mouse.move(self.configClient[str(fpsValue)+"FPS"]['X'], self.configClient[str(fpsValue)+"FPS"]['Y'])
        time.sleep(1)
        mouse.click()

    def conf_bitrate(self, bitrateValue):
        mouse.move(self.configClient[bitrateValue]['X'], self.configClient[bitrateValue]['Y'])
        time.sleep(1)
        mouse.click()

    def start_moonlight(self):
        self.start_moonlight_process()
        # Choose server
        print("Starting Moonlight...")
        mouse.move(self.configClient['Server']['X'], self.configClient['Server']['Y'])
        time.sleep(1)
        mouse.click()
        time.sleep(1)

        # Choose game
        mouse.move(self.configClient['Game']['X'], self.configClient['Game']['Y'])
        time.sleep(1)
        mouse.click()

        print('Moonlight client is running...')
        time.sleep(10)

    def stop_moonlight(self):
        keyboard.send('shift+alt+ctrl+q')

        #time.sleep(5)
        time.sleep(2)
        os.popen("TASKKILL /F /IM Moonlight.exe")
        print("Interrupting session!")
        #time.sleep(2)



    def show_stats(self):
        keyboard.send("Control + Shift + Alt + S")  # This command is defined by Moonlight to do this


    def get_metricsLog(self):
        fileLoL = LogMetrics('LoL',self.log_path, self.resolution,self.framerate)
        return fileLoL.get_dictionary()


