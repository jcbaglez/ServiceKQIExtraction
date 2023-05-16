import sys
import json
import mouse
import keyboard
import time

with open('server.json') as file:
    coord = json.load(file)

keyboard.send('esc')
time.sleep(3)
mouse.move(coord['CloseLol1']['X'], coord['CloseLol1']['Y'], absolute=True)
time.sleep(1)
#print(mouse.get_position())
mouse.click()
time.sleep(1)
# Tool practice button action
mouse.move(coord['CloseLol2']['X'], coord['CloseLol2']['Y'], absolute=True)
#print(mouse.get_position())
time.sleep(1)
mouse.click()

time.sleep(1)
mouse.move(coord['CloseLol3']['X'], coord['CloseLol3']['Y'], absolute=True)
mouse.click()
time.sleep(1)

mouse.move(coord['CloseLol4']['X'], coord['CloseLol4']['Y'], absolute=True)
time.sleep(1)
mouse.click()
