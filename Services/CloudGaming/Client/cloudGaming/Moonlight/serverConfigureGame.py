import sys
import json
import mouse
import keyboard
import time

from utils import *
def select_Mode(coord, mode):
    print("LoL Interface running")
    # Play button action
    mouse.move(coord['Play']['X'], coord['Play']['Y'], absolute=True)
    #print(mouse.get_position())
    time.sleep(1)
    mouse.click()
    time.sleep(2)

    if (mode == "trainingTool"):
        # Training game button action
        mouse.move(coord['Training']['X'], coord['Training']['Y'], absolute=True)
        time.sleep(1)
        #print(mouse.get_position())
        mouse.click()
        time.sleep(1)
        # Tool practice button action
        mouse.move(coord['ToolPractice']['X'], coord['ToolPractice']['Y'], absolute=True)
        #print(mouse.get_position())
        time.sleep(1)
        mouse.click()
        time.sleep(1)
    elif (mode == "customMatch"):
        # Create custom game button action
        mouse.move(coord['Custom']['X'], coord['Training']['Y'], absolute=True)
        time.sleep(1)
        #print(mouse.get_position())
        mouse.click()
        time.sleep(1)
        # Summoner's rift button action
        mouse.move(coord['Rift']['X'], coord['ToolPractice']['Y'], absolute=True)
        #print(mouse.get_position())
        time.sleep(1)
        mouse.click()
        time.sleep(1)
    # Confirm button action
    mouse.move(coord['Confirm']['X'], coord['Confirm']['Y'], absolute=True)
    #print(mouse.get_position())
    time.sleep(1)
    mouse.click()
    time.sleep(3)

def champSelect(coord):
    # Start game button action
    mouse.move(coord['Start']['X'], coord['Start']['Y'], absolute=True)
    #print(mouse.get_position())
    time.sleep(1)
    mouse.click()
    time.sleep(5)
    # Random champion button action
    mouse.move(coord['Random']['X'], coord['Random']['Y'], absolute=True)
    #print(mouse.get_position())
    time.sleep(1)
    mouse.click()
    time.sleep(2)
    # Confirm champion button action
    mouse.move(coord['Select']['X'], coord['Select']['Y'], absolute=True)
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
    keyboard.send('y')
    time.sleep(2)


if __name__ == '__main__':

    mon = monitorInfo(1)

    h = mon['height']

    if (h == 720): #720p
        filename = "720p"
    elif (h == 1080): #1080p
        filename = "1080p"
    
    with open('server_'+ filename + '.json') as file:
        coord = json.load(file)

    if (len(sys.argv)<2):
        mode = "trainingTool"
    else:
        mode = sys.argv[1]


    select_Mode(coord,sys.argv[1])
    champSelect(coord)
