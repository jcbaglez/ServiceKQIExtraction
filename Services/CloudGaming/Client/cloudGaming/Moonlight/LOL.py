import os
import json
import mouse
import keyboard
import requests
import time

class remoteLOL:

    def __init__(self, ip, port):
        self.coord = {}
        self.timeConfig = 0

        with open('cloudGaming/Moonlight/coordinates/actions.json') as file:
            self.coord = json.load(file)

        self.ip = ip
        self.port = port

        self.resolution = "1080p"
        self.framerate = 30
    def checkREST(self):
        base = "http://" + self.ip + ":" + str(self.port)
        header = {'content-type': 'application/json'}
        url = "/info"
        d = dict()
        print(base)
        try:
            r = requests.post(base + url, data=json.dumps([d]), timeout=5, headers=header)
            return True
        except:
            print("REST unavailable")
            return False



    # REMOTE
    def prepareGame(self, sessionType = "trainingTool"):
        # Configure LOL game in host through an HTTP request
        base = "http://" + self.ip + ":" + str(self.port)
        header = {'content-type': 'application/json'}
        url = "/action/configureClient"
        d = dict()
        d['type'] = sessionType
        # Start session
        r = requests.post(base + url, data=json.dumps(d), headers=header)

        # TODO: check requests' response


    def select_trainingMode(self):
        # TODO: Replace for prepareGame

        # if(checkREST(self.sIP,self.sPort)):
        b = True
        if (b):
            #self.serverPrepareGame()
            self.remotePrepareGame()
        else:  # If REST is not available, session will configure from client
            print("REST in the server is not available")


    def sendKeyAction(self, actions):
        base = "http://" + self.ip + ":" + str(self.port)
        header = {'content-type': 'application/json'}
        url = "/action/keyboard"
        d = dict()
        d['action'] = actions
        r = requests.post(base + url, data=json.dumps([d]), headers=header)


    def sendMouseAction(self, posX, posY, action):
        base = "http://" + self.ip + ":" + str(self.port)
        header = {'content-type': 'application/json'}
        url = "/action/mouse"
        d = dict()
        d['action'] = action
        d['pos'] = {'x': posX, 'y': posY}
        r = requests.post(base + url, data=json.dumps([d]), headers=header)



    #
    # def select_gameLoLPreloaded(self):
    #     # TODO: Remote (through API)
    #     time.sleep(60)
    #     print("LoL Interface running")
    #     # Play button action
    #     mouse.move(self.coord['Play']['X'], self.coord['Play']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Create custom game button action
    #     mouse.move(self.coord['Custom']['X'], self.coord['Custom']['Y'], absolute=True)
    #     time.sleep(0.5)
    #     print(mouse.get_position())
    #     mouse.click()
    #     time.sleep(1)
    #     # Summoner's rift button action
    #     mouse.move(self.coord['Rift']['X'], self.coord['Rift']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Confirm button action
    #     mouse.move(self.coord['Confirm']['X'], self.coord['Confirm']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Start game button action
    #     mouse.move(self.coord['Start']['X'], self.coord['Start']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Random champion button action
    #     mouse.move(self.coord['Random']['X'], self.coord['Random']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Confirm champion button action
    #     mouse.move(self.coord['Select']['X'], self.coord['Select']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Wait time until selection is done
    #     time.sleep(10)
    #     # Wait time until game starts
    #     time.sleep(30)
    #
    # def select_gameLoL(self):
    #     # TODO: remote
    #     mouse.move(self.coord['Play']['X'], self.coord['Play']['Y'], absolute=True)
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(60)
    #     print("LoL Interface running")
    #     # Play button action
    #     mouse.move(self.coord['Play']['X'], self.coord['Play']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Create custom game button action
    #     mouse.move(self.coord['Custom']['X'], self.coord['Custom']['Y'], absolute=True)
    #     time.sleep(0.5)
    #     print(mouse.get_position())
    #     mouse.click()
    #     time.sleep(1)
    #     # Summoner's rift button action
    #     mouse.move(self.coord['Rift']['X'], self.coord['Rift']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Confirm button action
    #     mouse.move(self.coord['Confirm']['X'], self.coord['Confirm']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Start game button action
    #     mouse.move(self.coord['Start']['X'], self.coord['Start']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Random champion button action
    #     mouse.move(self.coord['Random']['X'], self.coord['Random']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Confirm champion button action
    #     mouse.move(self.coord['Select']['X'], self.coord['Select']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.5)
    #     mouse.click()
    #     time.sleep(1)
    #     # Wait time until selection is done
    #     time.sleep(10)
    #     # Wait time until game starts
    #     time.sleep(30)
    #
    # def start_actions(self):
    #     # TODO: Consider to delete
    #     # Initial move
    #     time.sleep(4)
    #     mouse.move(self.actions['A1']['X'], self.actions['A1']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.1)
    #     self.right_click()
    #     time.sleep(4)
    #     # Second move after init
    #     mouse.move(self.actions['A2']['X'], self.actions['A2']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.1)
    #     self.right_click()
    #     time.sleep(4)
    #     # Third move after init
    #     mouse.move(self.actions['A3']['X'], self.actions['A3']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.1)
    #     self.right_click()
    #     time.sleep(4)
    #     # Fourth move after init
    #     mouse.move(self.actions['A4']['X'], self.actions['A4']['Y'], absolute=True)
    #     print(mouse.get_position())
    #     time.sleep(0.1)
    #     self.right_click()
    #     time.sleep(4)

    def game_actions_time(self, timeV):
        # TODO: consider to delete
        print("game_actions")
        timeClicks = []
        for i in range(1, int(timeV / 2)):
            print(i)
            self.move_camera_right()
            self.move_camera_up()
            # timeClicks.append(time.time())
            self.right_click()

            time.sleep(4)
            # self.use_Qability()
        # return timeClicks

    def game_restartCharacterPosition(self):
        self.sendKeyAction(['b'])


    def game_actions(self):
        self.move_camera_right()
        self.move_camera_up()
        self.right_click()
        time.sleep(4)

        for i in range(1, 6):
            self.move_camera_right()
            self.move_camera_up()
            self.right_click()
            time.sleep(5)

        self.move_camera_right()
        self.move_camera_right()
        self.move_camera_down()
        self.right_click()
        time.sleep(5)
        self.select_Qability()
        self.move_camera_right()
        self.move_camera_up()
        self.right_click()
        time.sleep(5)
        self.move_camera_right()
        self.move_camera_down()
        self.move_camera_down()
        self.right_click()
        time.sleep(5)
        self.use_Qability()
        self.use_Qability()
        self.use_Qability()

    def startConfiguration(self):
        # self.start_moonlight()
        self.select_trainingMode()
        self.timeConfig = time.time()
        t = time.time()
        return t

    def close_onlyGameClient(self):
        # Close LOL in host from CG client (through API)
        d = dict()
        base = "http://" + self.ip + ":" + str(self.port)
        url = "/action/endLoL"
        header = {'content-type': 'application/json'}
        r = requests.post(base + url, data=json.dumps(d), headers=header)

        if (r.status_code == 200):
            url = "/action/endProcess"
            d["process"] = "LeagueClient"
            r = requests.post(base + url, data=json.dumps(d), headers=header)
            if (r.status_code == 200):
                print("Client was closed successfully!")

        else:
            print("game cannot close")

    def quitGame(self):
        self.close_onlyGameClient()


