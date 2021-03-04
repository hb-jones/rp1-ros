import rp1controller
import keyboard
from time import sleep

HLC = rp1controller.RP1Controller()
Target = rp1controller.Target
speed_linear = 1
speed_radial = 0.8
loop = True
def fwd():
    HLC.set_target(Target(speed_linear,0),0)
    sleep(0.1)
    HLC.set_target(Target(0,0),0)
def bck():
    HLC.set_target(Target(-speed_linear,0),0)
    sleep(0.1)
    HLC.set_target(Target(0,0),0)
def lft():
    HLC.set_target(Target(0,-speed_linear),0)
    sleep(0.1)
    HLC.set_target(Target(0,0),0)
def rgt():
    HLC.set_target(Target(0,speed_linear),0)
    sleep(0.1)
    HLC.set_target(Target(0,0),0)
def rot_left():
    HLC.set_target(Target(0,0),-speed_radial)
    sleep(0.1)
    HLC.set_target(Target(0,0),0)
def rot_rgt():
    HLC.set_target(Target(0,0),speed_radial)
    sleep(0.1)
    HLC.set_target(Target(0,0),0)
def stp():
    HLC.set_target(Target(0,0),0)
def shut_down():
    loop = False
    

keyboard.add_hotkey('w', fwd)
keyboard.add_hotkey('s', bck)
keyboard.add_hotkey('a', lft)
keyboard.add_hotkey('d', rgt)
keyboard.add_hotkey('q', rot_left)
keyboard.add_hotkey('e', rot_rgt)
keyboard.add_hotkey(' ', stp)
keyboard.add_hotkey('r', stp)
keyboard.add_hotkey('t', shut_down)

while(loop):
    sleep(1)
    pass
