import keyboard
import mouse
import time
import os
import json
from utils.utils import *
from pynput.mouse import Button, Controller
from videoCapturing.imageCapture import *
import multiprocessing
from cloudGaming.Moonlight.metricas_fich import LogMetrics
class MacroLoL:
    def __init__(self, game_name, moonlight_path,ip,port):
        self.name = game_name
        self.path = moonlight_path
        self.coord = {}
        self.timeConfig = 0
        self.sIP = ip
        self.sPort = port
        self.log_path = 'C:/Users/' + os.getlogin() + '/AppData/Local/Temp'  # Game path Host
        with open('cloudGaming/Moonlight/coordinates/actions.json') as file:
            self.actions = json.load(file)

        #with open('cloudGaming/Moonlight/coordinates/client_conf2.json') as file:
        with open('cloudGaming/Moonlight/coordinates/client_conf_labMSI4K.json') as file:
            self.configClient = json.load(file)




    def conf_service(self,config):
        print("Configuration:", config)
        if ("resolution" not in config):
            config['resolution'] = "1080p"

        if ("fps" not in config):
            config['fps'] = 30

        if ("bitrate" not in config):
            config['bitrate'] = "Automatic"

        if ("audio" not in config):
            config['audio'] = "Stereo"

        if ("decoder" not in config):
            config['decoder'] = "Software_decoding"

        if ("codec" not in config):
            config['codec'] = "H.264"

        self.conf_Moonlight(config['resolution'], config['fps'], config['bitrate'],
            config['audio'], config['decoder'], config['codec'])


    def conf_Moonlight(self, resValue='1080p', fpsValue=30, bitrateValue='20 mbps', audioValue='Stereo',
                       decoderValue='VideoDecoder_automatic', codecValue='VideoCodec_automatic'):
        print("Configuring Moonlight....")
        monitor = monitorInfo()
        # Start Moonlight process
        self.start_moonlight_process()
        # Open configuration
        self.open_settings()
        # Configure Video Resolution
        self.conf_resolution(resValue)
        self.resValue = resValue
        # Configure FPS
        self.conf_fps(fpsValue)
        self.fpsValue = fpsValue
        # Configure video bitrate
        if(bitrateValue != "Automatic"):
            self.conf_bitrate(bitrateValue)
        self.bitrateValue = bitrateValue
        # Configure Audio
        #self.conf_audio(audioValue)
        self.audioValue = audioValue
        # Configure Decoder
        #self.conf_decoder(decoderValue)
        self.decoderValue = decoderValue
        # Configure Codec
        #self.conf_codec(codecValue)
        self.codecValue = codecValue
        # Finish configuration
        self.finish_configuration()
        print('Client has been configured: ' + resValue + ', ' + str(fpsValue) + 'FPS , ' + bitrateValue + ', ' + audioValue +
              ', ' + decoderValue + ', ' + codecValue)

    def start_moonlight_process(self):
        print('Moonlight Client is starting...')
        os.startfile(self.path)
        time.sleep(6)

    def open_settings(self):
        print('Moonlight Client is being configured...')
        mouse.move(self.configClient['Setting']['X'], self.configClient['Setting']['Y'])
        print("Position setting: (",self.configClient['Setting']['X'],",",self.configClient['Setting']['Y'],")")
        print("Position mouse:",mouse.get_position())
        time.sleep(1)
        mouse.click()

    def finish_configuration(self):
        mouse.move(self.configClient['Return']['X'], self.configClient['Return']['Y'])
        time.sleep(1)
        mouse.click()
        time.sleep(1)
        #keyboard.send('alt+F4')  # Close Moonlight interface
        #self.closeMoonlightInterface()
        self.stop_moonlight()
        time.sleep(1)

    def closeMoonlightInterface(self):
        mouse.move(self.configClient['CloseMoonlight']['X'], self.configClient['CloseMoonlight']['Y'])
        time.sleep(1)
        mouse.click()

    def conf_resolution(self, resValue):
        # Click on resolution menu
        mouse.move(self.configClient['Resolution']['X'], self.configClient['Resolution']['Y'])
        time.sleep(1)
        mouse.click()
        # Choose resolution
        if resValue == '720p':
            mouse.move(self.configClient['720p']['X'], self.configClient['720p']['Y'])
            time.sleep(1)
            mouse.click()
            with open('cloudGaming/Moonlight/coordinates/coord_720p.json') as file:
                self.coord = json.load(file)
        elif resValue == '1080p':
            mouse.move(self.configClient['1080p']['X'], self.configClient['1080p']['Y'])
            time.sleep(1)
            mouse.click()
            with open('cloudGaming/Moonlight/coordinates/coord_1080p.json') as file:
                self.coord = json.load(file)
        elif resValue == '1440p':
            mouse.move(self.configClient['1440p']['X'], self.configClient['1440p']['Y'])
            time.sleep(1)
            mouse.click()
            with open('cloudGaming/Moonlight/coordinates/coord_1440p.json') as file:
                self.coord = json.load(file)
        elif resValue == '4k' or resValue == '4K':
            mouse.move(self.configClient['4K']['X'], self.configClient['4K']['Y'])
            time.sleep(1)
            mouse.click()
            print(os.getcwd())
            with open('cloudGaming/Moonlight/coordinates/coord_4k.json') as file:
                self.coord = json.load(file)
        else:
            mouse.move(self.configClient['1080p']['X'], self.configClient['1080p']['Y'])
            time.sleep(1)
            mouse.click()
            with open('cloudGaming/Moonlight/coordinates/coord_1080p.json') as file:
                self.coord = json.load(file)

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

    def conf_audio(self, audioValue):
        mouse.move(self.configClient['Audio']['X'], self.configClient['Audio']['Y'])
        time.sleep(1)
        mouse.click()
        mouse.move(self.configClient[audioValue]['X'], self.configClient[audioValue]['Y'])
        time.sleep(1)
        mouse.click()

    def conf_decoder(self, decoderValue):
        mouse.move(self.configClient['VideoDecoder']['X'], self.configClient['VideoDecoder']['Y'])
        time.sleep(1)
        mouse.click()
        mouse.move(self.configClient[decoderValue]['X'], self.configClient[decoderValue]['Y'])
        time.sleep(1)
        mouse.click()

    def conf_codec(self, codecValue):
        mouse.move(self.configClient['VideoCodec']['X'], self.configClient['VideoCodec']['Y'])
        time.sleep(1)
        mouse.click()
        mouse.move(self.configClient[codecValue]['X'], self.configClient[codecValue]['Y'])
        time.sleep(1)
        mouse.click()

    def start_moonlight(self):
        self.start_moonlight_process()
        # Choose server
        print("Starting Moonlight...")
        mouse.move(self.configClient['Sirio']['X'], self.configClient['Sirio']['Y'])
        print(self.configClient['Sirio']['X'], self.configClient['Sirio']['Y'])
        print(mouse.get_position())
        time.sleep(1)
        mouse.click()
        time.sleep(1)
        # Choose game
        mouse.move(self.configClient['LoL']['X'], self.configClient['LoL']['Y'])
        print(self.configClient['LoL']['X'], self.configClient['LoL']['Y'])
        print(mouse.get_position())
        time.sleep(1)
        mouse.click()
        print('Moonlight client is running...')
        time.sleep(10)


    def select_trainingMode(self):
        #time.sleep(60)
        #print("LoL Interface running")
        #if(checkREST(self.sIP,self.sPort)):
        b = True
        if(b):
            serverPrepareGame(self.sIP, self.sPort,"trainingTool")
        else: # If REST is not available, session will configure from client
            print("REST in the server is not available")
            # Play button action
            mouse.move(self.coord['Play']['X'], self.coord['Play']['Y'], absolute=True)
            #print(mouse.get_position())
            time.sleep(1)
            mouse.click()
            time.sleep(5)
            # Create custom game button action
            mouse.move(self.coord['Training']['X'], self.coord['Training']['Y'], absolute=True)
            time.sleep(1)
            #print(mouse.get_position())
            mouse.click()
            time.sleep(5)
            # Summoner's rift button action
            mouse.move(self.coord['ToolPractice']['X'], self.coord['ToolPractice']['Y'], absolute=True)
            #print(mouse.get_position())
            time.sleep(1)
            mouse.click()
            time.sleep(5)
            # Confirm button action
            mouse.move(self.coord['Confirm']['X'], self.coord['Confirm']['Y'], absolute=True)
            #print(mouse.get_position())
            time.sleep(1)
            mouse.click()
            time.sleep(5)
            # Start game button action
            mouse.move(self.coord['Start']['X'], self.coord['Start']['Y'], absolute=True)
            #print(mouse.get_position())
            time.sleep(1)
            mouse.click()
            time.sleep(5)
            # Random champion button action
            mouse.move(self.coord['Random']['X'], self.coord['Random']['Y'], absolute=True)
            #print(mouse.get_position())
            time.sleep(1)
            mouse.click()
            time.sleep(2)
            # Confirm champion button action
            mouse.move(self.coord['Select']['X'], self.coord['Select']['Y'], absolute=True)
            #print(mouse.get_position())
            time.sleep(1)
            mouse.click()
            time.sleep(2)
            # Wait time until selection is done
            time.sleep(10)
            # Wait time until game starts
            time.sleep(30)
            #keyboard.send('y')
            keyboard.send('control+shift+i')
            keyboard.send('shift+h')
            time.sleep(1)
            keyboard.send('y')
            time.sleep(2)

    def select_gameLoLPreloaded(self):
        time.sleep(60)
        print("LoL Interface running")
        # Play button action
        mouse.move(self.coord['Play']['X'], self.coord['Play']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Create custom game button action
        mouse.move(self.coord['Custom']['X'], self.coord['Custom']['Y'], absolute=True)
        time.sleep(0.5)
        print(mouse.get_position())
        mouse.click()
        time.sleep(1)
        # Summoner's rift button action
        mouse.move(self.coord['Rift']['X'], self.coord['Rift']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Confirm button action
        mouse.move(self.coord['Confirm']['X'], self.coord['Confirm']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Start game button action
        mouse.move(self.coord['Start']['X'], self.coord['Start']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Random champion button action
        mouse.move(self.coord['Random']['X'], self.coord['Random']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Confirm champion button action
        mouse.move(self.coord['Select']['X'], self.coord['Select']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Wait time until selection is done
        time.sleep(10)
        # Wait time until game starts
        time.sleep(30)

    def select_gameLoL(self):
        mouse.move(self.coord['Play']['X'], self.coord['Play']['Y'], absolute=True)
        time.sleep(0.5)
        mouse.click()
        time.sleep(60)
        print("LoL Interface running")
        # Play button action
        mouse.move(self.coord['Play']['X'], self.coord['Play']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Create custom game button action
        mouse.move(self.coord['Custom']['X'], self.coord['Custom']['Y'], absolute=True)
        time.sleep(0.5)
        print(mouse.get_position())
        mouse.click()
        time.sleep(1)
        # Summoner's rift button action
        mouse.move(self.coord['Rift']['X'], self.coord['Rift']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Confirm button action
        mouse.move(self.coord['Confirm']['X'], self.coord['Confirm']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Start game button action
        mouse.move(self.coord['Start']['X'], self.coord['Start']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Random champion button action
        mouse.move(self.coord['Random']['X'], self.coord['Random']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Confirm champion button action
        mouse.move(self.coord['Select']['X'], self.coord['Select']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.5)
        mouse.click()
        time.sleep(1)
        # Wait time until selection is done
        time.sleep(10)
        # Wait time until game starts
        time.sleep(30)

    def start_actions(self):
        # Initial move
        time.sleep(4)
        mouse.move(self.actions['A1']['X'], self.actions['A1']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.1)
        self.right_click()
        time.sleep(4)
        # Second move after init
        mouse.move(self.actions['A2']['X'], self.actions['A2']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.1)
        self.right_click()
        time.sleep(4)
        # Third move after init
        mouse.move(self.actions['A3']['X'], self.actions['A3']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.1)
        self.right_click()
        time.sleep(4)
        # Fourth move after init
        mouse.move(self.actions['A4']['X'], self.actions['A4']['Y'], absolute=True)
        print(mouse.get_position())
        time.sleep(0.1)
        self.right_click()
        time.sleep(4)

    def game_actions_time(self,timeV):
        print("game_actions")
        timeClicks = []
        for i in range(1,int(timeV/2)):
            print(i)
            self.move_camera_right()
            self.move_camera_up()
            #timeClicks.append(time.time())
            self.right_click()

            time.sleep(4)
            #self.use_Qability()
        #return timeClicks

    def game_go_base(self):
        keyboard.send('b')
        time.sleep(1)

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
        # self.stop_moonlight()
        # if(checkREST(self.sIP,self.sPort)):
        #     serverPrepare(self.sIP,self.sPort)
        # else:
        #     print("REST in the server is not available")
        return t

    def close_onlyGameClient(self):
        # keyboard.send('esc')
        # time.sleep(2)
        # mouse.move(self.coord['CloseLol1']['X'], self.coord['CloseLol1']['Y'], absolute=True)
        # time.sleep(0.1)
        # mouse.click()
        # time.sleep(1)
        # mouse.move(self.coord['CloseLol2']['X'], self.coord['CloseLol2']['Y'], absolute=True)
        # time.sleep(0.1)
        # mouse.click()
        # time.sleep(5)

        d = dict()
        base = "http://"+ self.sIP +":" +  str(self.sPort)
        url = "/action/endLoL"
        header =  {'content-type' : 'application/json'}
        r = requests.post(base + url,data = json.dumps(d), headers=header)

        if(r.status_code == 200):
            url = "/action/endProcess"
            d["process"] = "LeagueClient"
            r = requests.post(base + url,data = json.dumps(d), headers=header)
            if(r.status_code == 200):
                print("Client was closed successfully!")

        else:
            print("game cannot close")

    def quitGame(self):
        # self.start_moonlight_process()
        # # Choose server
        # mouse.move(self.configClient['Sirio']['X'], self.configClient['Sirio']['Y'])
        # print(self.configClient['Sirio']['X'], self.configClient['Sirio']['Y'])
        # print(mouse.get_position())
        # time.sleep(1)
        # mouse.click()
        # # Choose game
        # mouse.move(self.configClient['QuitGame']['X'], self.configClient['QuitGame']['Y'], absolute=True)
        # time.sleep(1)
        # mouse.click()

        # time.sleep(1)
        # mouse.move(self.configClient['ConfirmQuitGame']['X'], self.configClient['ConfirmQuitGame']['Y'], absolute=True)
        # time.sleep(1)
        # mouse.click()
        # time.sleep(5)
 
        self.close_onlyGameClient()



    def sendKeyAction(self, actions):
        base = "http://"+self.sIP+":"+ str(self.sPort)
        header =  {'content-type' : 'application/json'}
        url = "/action/keyboard"
        d = dict()
        d['action'] = actions
        r = requests.post(base+url, data = json.dumps([d]), headers = header)

    def sendMouseAction(self, posX,posY,action):
        base = "http://"+self.sIP+ ":" + str(self.sPort)
        header = {'content-type' : 'application/json'}
        url = "/action/mouse"
        d = dict()
        d['action'] = action
        d['pos'] = {'x':posX, 'y':posY}
        r = requests.post(base+url, data = json.dumps([d]), headers = header)

    def prepareExperiment(self,pos):

        name = str(int(time.time()))
        # Get monitor information from the server
        monitor = monitorInfo()[1]
        # Prepare user actions
        d = dict()
        d['repetitions'] = pos['repetitions']
        d['dMove'] = pos['dMove']
        dx = int(monitor['width']*pos['coordinates']['x'] + monitor['left'])
        dy = int(monitor['height']*pos['coordinates']['y'] + monitor['top'])
        #dx = 2651
        #dy = 691
        d['actions'] = [{'x':dx, 'y':dy}]
        data2send = [d]

        # Start Moonlight
        self.start_moonlight()
        time.sleep(10)
        self.sendMouseAction(dx,dy,"click")
        #time.sleep(2)
        #self.sendMouseAction(dx, dy, "click")
        # Show stats in Moonlight
        keyboard.send("Control + Shift + Alt + S") # This command is defined by Moonlight to do this
        mouse.move(dx,dy,absolute=True)
        mouse.click()

        # Estimation of the time which will be passed while actions are being doing
        t =pos['dMove']*d['repetitions'] +5

        return (name,data2send,t)

    def experiment(self,pos):
        try:
            q = multiprocessing.Queue()
            q2 = multiprocessing.Queue()
            # if (time.time() > self.timeConfig + 3600):
            #     self.quitGame()
            #     time.sleep(5)
            #     self.startConfiguration()
            name = str(int(time.time()))
            self.start_moonlight()
            time.sleep(10)
            keyboard.send("Control + Shift + Alt + S") # Show stats in Moonlight
            monitor = monitorInfo()[1]
            d = dict()
            d['repetitions'] = pos['repetitions']
            d['dMove'] = pos['dMove']

            dx = int(monitor['width']*pos['coordinates']['x'] + monitor['left'])
            dy = int(monitor['height']*pos['coordinates']['y'] + monitor['top'])
            d['actions'] = [{'x':dx, 'y':dy}]   
            data2send = [d]

            t =pos['dMove']*d['repetitions'] + 5

            # Get host latency
            dataFromServer = serverCapture2(pos)
            #res = np.asarray(dataFromServer['latency'])
            #res2 = np.asarray(dataFromServer['latency2'])
            #print(res)
            time.sleep(2)
            mouse.move(dx,dy,absolute=True)
            mouse.click()

            self.sendKeyAction(['b'])
            time.sleep(10)
            
            #name = "pruebas"
            #server = multiprocessing.Process(target= serverCapture, args=(t,q))
            client = multiprocessing.Process(target= gettingFrames , args=(t,name,))
            p = multiprocessing.Process(target=pingTest,args=("192.168.3.1","PING_Radio",80,20,q2))
            #p = multiprocessing.Process(target=pingTest,args=("185.40.67.150",'PING_RIOT',80,20,q2))
            
            p.start()
            #server.start()
            client.start()
            time.sleep(2)

            r = mouseMeasurement(data2send,name)
            p.join()
            client.join()
            #server.join()


        except:
            print("Something wrong")
            traceback.print_exc()
            #exc = True
        finally:
            self.stop_moonlight()
            self.sendKeyAction(['b'])
            #serverT = q.get()
            try:
                pingValues = q2.get()
                kqi = self.getKQIs(r,name)
                kqi.update(self.latencyFormatting("host",np.asarray(dataFromServer['latency'])))
                kqi.update(pingValues)
                kqi.update(dataFromServer['ping'])
            except:
                traceback.print_exc()
                kqi = dict()
                # try:
            finally:
                kqi['filename'] = name
                
        try:
            os.remove(name + "_images.npy")
            #os.remove(name + "_timestamp.npy")
            os.remove(name+":mouse.npy")
        except:
            print("Files can't be removed")

        return kqi

    def experiment2(self,pos):
        q3 = multiprocessing.Queue()
        qH =multiprocessing.Queue()
        # if (time.time() > self.timeConfig + 3600):
        #     self.quitGame()
        #     time.sleep(5)
        #     self.startConfiguration()
        name = str(int(time.time()))


                # Get monitor information from the server
        monitor = monitorInfo()[1]
        # Prepare user actions
        d = dict()
        d['repetitions'] = pos['repetitions']
        d['dMove'] = pos['dMove']

        dx = int(monitor['width']*pos['coordinates']['x'] + monitor['left'])
        dy = int(monitor['height']*pos['coordinates']['y'] + monitor['top'])
        d['actions'] = [{'x':dx, 'y':dy}]   
        data2send = [d]


        # Start Moonlight
        self.start_moonlight()
        time.sleep(10)
        self.sendMouseAction(dx,dy,"click")
        # Show stats in Moonlight
        keyboard.send("Control + Shift + Alt + S") # This command is defined by Moonlight to do this
        mouse.move(dx,dy,absolute=True)
        mouse.click()

        

        # Estimation of the time which will be passed while actions are being doing
        t =pos['dMove']*d['repetitions'] +5
        
        # Get client latency
        try: 
            # Activate flag to test in server
            serverTest = True

            # Measuring samples
            client = multiprocessing.Process(target= gettingFrames , args=(t,name,)) # Getting images process
            host = multiprocessing.Process(target = serverCapture, args = (d['repetitions'],qH))
            #mov = multiprocessing.Process(target=self.checkMoveHost, args = (10,q4,))
            #p = multiprocessing.Process(target=pingTest,args=("192.168.3.1","PING_Radio",80,20,q2)) # Ping process
            p2 = multiprocessing.Process(target= pingTest,args=(self.sIP, "PING_Host",80,10,q3))
            # Start process
            #p.start()
            p2.start()
            host.start()
            client.start()
            #mov.start()
            time.sleep(2)

            # User actions
            r = mouseMeasurement(data2send,name)
            
            # Wait until process have finished
            #p.join()
            p2.join()
            client.join()
            host.join()

            serverD = qH.get()
        except:
            #print("Fail in getting Frames from moonlight")
            traceback.print_exc()

        self.sendKeyAction(['b'])
        # Stop Moonlight
        self.stop_moonlight()
        # Reset character position (game)
        time.sleep(8)

        try:
            kqi = self.getKQIs(r,name)
            kqi.update(serverD)
            kqi.update(q3.get())
        except:
            traceback.print_exc()
            kqi = dict()
            kqi['filename'] = name

        # Remove files    
        try:
            os.remove(name + "_images.npy")
            os.remove(name + "_timestamp.npy")
            os.remove(name+"_mouse.npy")
        except:
            print("Files can't be removed")
            
        return kqi

    def experimentCrowd(self,pos,allMeasures=True):
        q = multiprocessing.Queue()
        q2 = multiprocessing.Queue()
        q3 = multiprocessing.Queue()
        q4 = multiprocessing.Queue()
        q5 = multiprocessing.Queue()
        q6 = multiprocessing.Queue()
        # if (time.time() > self.timeConfig + 3600):
        #     self.quitGame()
        #     time.sleep(5)
        #     self.startConfiguration()
        name = str(int(time.time()))
        kqi = dict()

        # Get monitor information from the server
        monitor = monitorInfo()[1]
        # Prepare user actions
        d = dict()
        d['repetitions'] = pos['repetitions']
        d['dMove'] = pos['dMove']

        dx = int(monitor['width']*pos['coordinates']['x'] + monitor['left'])
        dy = int(monitor['height']*pos['coordinates']['y'] + monitor['top'])
        d['actions'] = [{'x':dx, 'y':dy}]   
        data2send = [d]


        # Start Moonlight
        self.start_moonlight()
        time.sleep(10)
        self.sendMouseAction(dx,dy,"click")
        # Show stats in Moonlight
        keyboard.send("Control + Shift + Alt + S") # This command is defined by Moonlight to do this
        mouse.move(dx,dy,absolute=True)
        mouse.click()

        

        # Estimation of the time which will be passed while actions are being doing
        t =pos['dMove']*d['repetitions'] +5
        
        # Get client latency
        try: 
            # Activate flag to test in server
            serverTest = True

            # Measuring samples
            client = multiprocessing.Process(target= gettingFrames , args=(t,name,)) # Getting images process
            mov = multiprocessing.Process(target=self.checkMoveHost, args = (10,q4,))
            p = multiprocessing.Process(target=pingTest,args=("192.168.3.1","PING_Radio",80,20,q2)) # Ping process
            p2 = multiprocessing.Process(target= pingTest,args=(self.sIP, "PING_Host",80,20,q3))
            # Start process
            p.start()
            p2.start()
            if(allMeasures):
                client.start()
                mov.start()
                time.sleep(2)

            # User actions
            r = mouseMeasurement(data2send,name)
            
            # Wait until process have finished
            p.join()
            p2.join()
            if(allMeasures):
                client.join()
                print("waiting mov")
                mov.join()
                print("Let's get mov")
                #serverTest = q4.get()
        except:
            #print("Fail in getting Frames from moonlight")
            traceback.print_exc()
            
            # If something fails, desactivate server test procedures
            serverTest =False

        self.sendKeyAction(['b'])
        # Stop Moonlight
        self.stop_moonlight()

        p_a = multiprocessing.Process(target=pingTest, args=("192.168.3.1", "PING_Radio_", 80, 5, q5))  # Ping process
        p2_a = multiprocessing.Process(target=pingTest, args=(self.sIP, "PING_Host_", 80, 5, q6))
        # Reset character position (game)
        p_a.start()
        p2_a.start()

        #print("Server Test -->",serverTest)
        if(serverTest):
            #if(allMeasures):
                # Server test procedure
           #     server = multiprocessing.Process(target= self.serverExperiment , args=(pos,q,))
            #    server.start()
        
            # Get client measures
            try:
                pingValues = q2.get()
                kqi = self.getKQIs(r,name,allMeasures)
                kqi.update(pingValues)
                kqi.update(q3.get())
                p_a.join()
                p2_a.join()
                kqi.update(q5.get())
                kqi.update(q6.get())

            except:
                traceback.print_exc()
                kqi = dict()
                kqi['filename'] = name

        # Remove files    
        try:
            os.remove(name + "_images.npy")
            os.remove(name + "_timestamp.npy")
            os.remove(name+"_mouse.npy")
        except:
            print("Files can't be removed")
        hlatency = dict()
        prefix = "host"
        hl = 50
        hlatency[prefix + 'latencyAvg'] = hl
        hlatency[prefix + 'latencyMax'] = hl
        hlatency[prefix + 'latencyMin'] = hl
        hlatency[prefix + 'latency25Percent'] = hl
        hlatency[prefix + 'latency50Percent'] = hl
        hlatency[prefix + 'latency75Percent'] = hl
        hlatency[prefix + 'latency'] = [hl, hl, hl, hl, hl]
        kqi.update(hlatency)
        return kqi

    def experimentETH(self,pos,allMeasures):
        q = multiprocessing.Queue()
        q2 = multiprocessing.Queue()
        q3 = multiprocessing.Queue()
        qMov = multiprocessing.Queue()
        # if (time.time() > self.timeConfig + 3600):
        #     self.quitGame()
        #     time.sleep(5)
        #     self.startConfiguration()
        (name,data2send, t) = self.prepareExperiment(pos)

        # Get client latency
        try: 
            # Activate flag to test in server
            serverTest = True
            # Measuring samples
            client = multiprocessing.Process(target= gettingFrames , args=(t,name,)) # Getting images process
            mov = multiprocessing.Process(target=self.checkMoveHost, args = (10,qMov,))
            p2 = multiprocessing.Process(target= pingTest,args=(self.sIP, "PING_Host",80,20,q2))
            # Start process
            p2.start()
            if(allMeasures):
                client.start()
                mov.start()
                time.sleep(2)

            # User actions
            r = mouseMeasurement(data2send,name)
            
            # Wait until process have finished
            p2.join()
            if(allMeasures):
                client.join()
                mov.join()

                serverTest = qMov.get()
        except:
            #print("Fail in getting Frames from moonlight")
            traceback.print_exc()
            # If something fails, desactivate server test procedures
            serverTest =False

        self.sendKeyAction(['b'])
        # Stop Moonlight
        self.stop_moonlight()

        # Reset character position (game)
        
        time.sleep(2)


        try:
            pingValues = q2.get()
            p2 = multiprocessing.Process(target=pingTest, args=(self.sIP, "PING_Host_prev", 80, 10, q2))
            p2.start()
            kqi = self.getKQIs(r,name,allMeasures)
            kqi.update(pingValues)
            pingValues = q2.get()
            kqi.update(pingValues)
        except:
            traceback.print_exc()
            kqi = dict()
            kqi['filename'] = name

        # Remove files    
        try:
            os.remove(name + "_images.npy")
            os.remove(name + "_timestamp.npy")
            os.remove(name+"_mouse.npy")
        except:
            print("Files can't be removed")
        hlatency = dict()
        prefix = "host"
        hl = 50
        hlatency[prefix + 'latencyAvg'] = hl
        hlatency[prefix + 'latencyMax'] = hl
        hlatency[prefix + 'latencyMin'] = hl
        hlatency[prefix + 'latency25Percent'] = hl
        hlatency[prefix + 'latency50Percent'] = hl
        hlatency[prefix + 'latency75Percent'] = hl
        hlatency[prefix + 'latency'] = [hl, hl, hl, hl, hl]
        kqi.update(hlatency)

        return kqi

    def experiment3(self,pos,allMeasures,crowd):

        qRadio = multiprocessing.Queue()
        qHost = multiprocessing.Queue()
        qMov = multiprocessing.Queue()
        # if (time.time() > self.timeConfig + 3600):
        #     self.quitGame()
        #     time.sleep(5)
        #     self.startConfiguration()
        (name,data2send, t) = self.prepareExperiment(pos)
        
        # Get client latency
        try: 

            # Measuring samples
            client = multiprocessing.Process(target= gettingFrames , args=(t,name,)) # Getting images process
            mov = multiprocessing.Process(target=serverCapture, args = (data2send[0]['repetitions'],qMov,))
            if crowd:
                pRadio = multiprocessing.Process(target=pingTest,args=("192.168.3.1","PING_Radio",80,20,qRadio)) # Ping process
                pRadio.start()
            pHost = multiprocessing.Process(target= pingTest,args=(self.sIP, "PING_Host",80,20,qHost)) 

            # Start process
            pHost.start()
            if(allMeasures):
                client.start()
                mov.start()
                time.sleep(2)

            # User actions
            r = mouseMeasurement(data2send,name)
            
            if(allMeasures):
                # Wait until process have finished
                client.join()
                mov.join()

                #serverTest = qMov.get()
        except:
            #print("Fail in getting Frames from moonlight")
            traceback.print_exc()
            # If something fails, desactivate server test procedures
            serverTest =False

        self.sendKeyAction(['b'])
        # Stop Moonlight
        self.stop_moonlight()

        # Reset character position (game)
        
        


        # if(allMeasures):
        #     # Server test procedure
        #     server = multiprocessing.Process(target= self.serverExperiment , args=(pos,q,))    
        #     server.start()

            # Get client measures
        try:
           
            kqi = self.getKQIs(r,name,allMeasures)
            # Host values
            hostM = qMov.get()
            kqi.update(hostM)
             # Ping host values
            pHost.join()
            kqi.update(qHost.get())
            if(crowd): # If is an experiment through crowdcell, get Radio ping values
                pRadio.join()
                kqi.update(qRadio.get())
            
        except:
            traceback.print_exc()
            kqi = dict()
            kqi['filename'] = name

        # Remove files    
        try:
            os.remove(name + "_images.npy")
            os.remove(name + "_timestamp.npy")
            os.remove(name+"_mouse.npy")
        except:
            print("Files can't be removed")
        
        # if(allMeasures):
        #     # Get results from the server and adding to client measures
        #     server.join()
        #     self.sendKeyAction('b')
        #     try:
        #         dataFromServer= q.get()
        #         hLatency = self.latencyFormatting("host",np.asarray(dataFromServer['latency']))
        #         kqi.update(hLatency)
        #         kqi.update(dataFromServer['ping']) 
        #     except:
        #         traceback.print_exc()
        time.sleep(4)
        return kqi
    
    def experimentCrowd2(self,pos,allMeasures = True):
        q = multiprocessing.Queue()
        q2 = multiprocessing.Queue()
        q3 = multiprocessing.Queue()
        qMov = multiprocessing.Queue()
        # if (time.time() > self.timeConfig + 3600):
        #     self.quitGame()
        #     time.sleep(5)
        #     self.startConfiguration()
        (name,data2send, t) = self.prepareExperiment(pos)

        p = multiprocessing.Process(target=pingTest,args=("192.168.3.1","PING_Radio",80,20,q2)) # Ping process
        p2 = multiprocessing.Process(target= pingTest,args=(self.sIP, "PING_Host",80,20,q3))
    def serverExperiment(self,pos, q = None):
        # Get host latency
        try:
            dataFromServer = serverCapture2(pos)
            res = np.asarray(dataFromServer['latency'])
            time.sleep(2)

        except:
            print("Error in server Experient")
            traceback.print_exc()
            dataFromServer = dict()
        
        if (q != None):
            q.put(dataFromServer)
        return dataFromServer


    def checkMoveHost(self, time, q = None):
        try:
            print("base")
            base = "http://"+self.sIP+ ":" + str(self.sPort)
            url = "/frame/checkMovement?t="+str(time)
            r = requests.get(base+url)
            resp = r.json()
            if(resp["move"] == 1):
                resp = True
            else:
                resp = False
        except: 
            traceback.print_exc()
            resp = False
        
        
        if (q != None):
            q.put(resp)
        return resp
    def getKQIs(self,mouseTime,name,allMeas = True):
        # Get Measures from moonlight logs
        fileLoL = LogMetrics('LoL',self.log_path, self.resValue,self.fpsValue,self.audioValue,self.decoderValue,self.codecValue)
        latencyResults = fileLoL.get_dictionary()
        if (allMeas):
            # Measures from images
            q = multiprocessing.Queue()

            # Stalls calculation
            stalls = multiprocessing.Process(target= getStalls , args=(name,self.fpsValue,q,))
            stalls.start()

            # Latency calculation
            (img,imgt) = loadData(name)
            (cLD, efps) = getResponsivity4(mouseTime,img,imgt)
            del img
            del imgt
            
            latencyResults.update(self.latencyFormatting("client",cLD))
            latencyResults['efps'] = efps
            stalls.join()
            cFD = q.get()

            # Gathering kqi data
            latencyResults.update(cFD)

        return latencyResults

    def latencyFormatting(self,prefix, data):
        prefix = prefix + "_"
        hLatency = getSummaryLatency(data)
        latencyResults = dict()
         # Change of values to ms
        latencyResults[prefix + 'latencyAvg'] = hLatency['avg'] * 1000
        latencyResults[prefix + 'latencyMax'] = hLatency['max'] * 1000
        latencyResults[prefix + 'latencyMin'] = hLatency['min'] * 1000
        latencyResults[prefix + 'latency25Percent'] = hLatency['percent25']*1000
        latencyResults[prefix + 'latency50Percent'] = hLatency['percent50']*1000
        latencyResults[prefix + 'latency75Percent'] = hLatency['percent75']*1000
        latencyResults[prefix + 'latency'] = (data*1000).tolist()

        return latencyResults

    def emptyResults(self):
        latencyResults = dict()
        latencyResults['host_latencyAvg'] = 0
        latencyResults['host_latencyMax'] = 0
        latencyResults['host_latencyMin'] = 0
        latencyResults['client_latencyAvg'] = 0
        latencyResults['client_latencyMax'] = 0
        latencyResults['client_latencyMin'] = 0
        latencyResults['host_latency'] = [0]
        latencyResults['client_latency'] = [0]
        latencyResults['client_latency25Percent'] = 0
        latencyResults['client_latency50Percent'] = 0
        latencyResults['client_latency75Percent'] = 0
        latencyResults['host_latency25Percent'] = 0
        latencyResults['host_latency50Percent'] = 0
        latencyResults['host_latency75Percent'] = 0
        #latencyResults['clientMoveMeasurement'] = [0]
        return latencyResults
    # @staticmethod
    # def stop_moonlight():
    #     keyboard.send('alt+F4')
    #     print('Interrupting session!')
    #     time.sleep(2)
    #     keyboard.send('alt+F4')
    #     print('Closing Moonlight client...')
    #     time.sleep(5)


    # def stop_moonlight(self):
    #     keyboard.send('alt+F4')
    #     print('Interrupting session!')
    #     time.sleep(2)
    #     #keyboard.send('alt+F4')
    #     self.closeMoonlightInterface()
    #     print('Closing Moonlight client...')
    #     time.sleep(5)

    def stop_moonlight(self):
        keyboard.send('shift+alt+ctrl+q')

        time.sleep(5)

        getFromConsole("TASKKILL /F /IM Moonlight.exe")
        print("Interrupting session!")
        time.sleep(2)

    def close_lol(self):
        time.sleep(2)
        keyboard.send('alt+F4')
        print('Finalizing LoL simulation!')
        time.sleep(2)
        mouse.move(self.coord['CloseLol3']['X'], self.coord['CloseLol3']['Y'], absolute=True)
        time.sleep(1)
        mouse.click()
        mouse.move(self.coord['CloseLol4']['X'], self.coord['CloseLol4']['Y'], absolute=True)
        time.sleep(1)
        mouse.click()
        time.sleep(5)
        keyboard.send('alt+F4')
        print('Closing Moonlight client...')
        time.sleep(5)

    def move_camera_right(self):
        mouse.move(self.actions['RightSide']['X'], self.actions['RightSide']['Y'], absolute=True)
        time.sleep(0.25)
        mouse.move(self.actions['Center']['X'], self.actions['Center']['Y'], absolute=True)
        time.sleep(0.25)

    def move_camera_left(self):
        mouse.move(self.actions['LeftSide']['X'], self.actions['LeftSide']['Y'], absolute=True)
        time.sleep(0.25)
        mouse.move(self.actions['Center']['X'], self.actions['Center']['Y'], absolute=True)
        time.sleep(0.25)

    def move_camera_up(self):
        mouse.move(self.actions['UpSide']['X'], self.actions['UpSide']['Y'], absolute=True)
        time.sleep(0.25)
        mouse.move(self.actions['Center']['X'], self.actions['Center']['Y'], absolute=True)
        time.sleep(0.25)

    def move_camera_down(self):
        mouse.move(self.actions['DownSide']['X'], self.actions['DownSide']['Y'], absolute=True)
        time.sleep(0.25)
        mouse.move(self.actions['Center']['X'], self.actions['Center']['Y'], absolute=True)
        time.sleep(0.25)

    @staticmethod
    def right_click():
        mouse.right_click()

    @staticmethod
    def left_click():
        mouse.click()

    @staticmethod
    def select_Qability():
        keyboard.send('ctrl+q')
        time.sleep(2)

    @staticmethod
    def use_Qability():
        keyboard.send('q')
        time.sleep(7)
