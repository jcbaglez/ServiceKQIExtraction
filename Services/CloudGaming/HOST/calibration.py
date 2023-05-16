import mouse
from pynput.mouse import Listener
import threading
import json
class calibration:

    def __init__(self):
        self.positions = dict()
        self.posArray = []


    def on_move(self,x,y):
        pass
    
    def on_click_recording(self,x,y,button,pressed):
        s = '{0}'.format(button)
        if pressed:
            if s == "Button.left":
                pos = mouse.get_position()
                print('Mouse clicked at ({0},{1})'.format(pos[0], pos[1]))
                self.posArray.append([pos[0],pos[1]])
            elif s == "Button.middle":
                self.listener.stop()

    def on_click(self, x,y,button,pressed):
        s = '{0}'.format(button)

        if pressed and (s == "Button.middle" or s == "Button.right"):
            #self.mousepos = [mouse.get_position()]
            pos = mouse.get_position()
            #self.mousepos = [pos[0],pos[1]]
            self.mousepos = [x,y]
            print("Hi")
            print("Mouse library position: ", str(pos))
            print("Position listener: (",x,",",y,")")
            print(pos)
            #self.mousepos = [x,y]
            #print('Mouse clicked at ({0}, {1}) with {2}'.format(x,y,button))
            self.listener.stop()
            


    def on_scroll(self,x,y,dx,dy):
        pass


    def getPositionsFromList(self, places, filename = ""):

        # For each place from the list
        for p in places:
            print("Press middle button over  ", p)

            with Listener(on_move = self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as self.listener:
                self.listener.join()
   
            
            self.positions[p] = {'X':self.mousepos[0], 'Y':self.mousepos[1]}

        if(filename != ""):
            with open(filename,"w") as outfile:
                json.dump(self.positions,outfile,indent = 6)

        return self.positions

    def getPositionsFromRecording(self,filename=""):
        print("To stop recording click middle button")
        print("Recording mouse actions...")
        # Empty the buffer
        self.posArray = []

        # Call Listener
        with Listener(on_move = self.on_move, on_click = self.on_click_recording, on_scroll = self.on_scroll) as self.listener:
            self.listener.join()
        
        if(filename != ""):
            with open(filename,"w") as outfile:
                json.dump(self.posArray,outfile,indent = 6)

        self.listener.stop()
        return self.posArray

