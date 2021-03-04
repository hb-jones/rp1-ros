import rp1controller
import keyboard
from time import sleep

HLC = rp1controller.RP1Controller()
Target = rp1controller.Target
speed_linear = 2
speed_radial = 0.8
loop = True
cont = False
def fwd():
    cont = True
    HLC.set_target(Target((speed_linear,0),0))
def bck():
    cont = True
    HLC.set_target(Target((-speed_linear,0),0))
def lft():
    cont = True
    HLC.set_target(Target((0,-speed_linear),0))
def rgt():
    cont = True
    HLC.set_target(Target((0,speed_linear),0))
def rot_left():
    cont = True
    HLC.set_target(Target((0,0),-speed_radial))
def rot_rgt():
    cont = True
    HLC.set_target(Target((0,0),speed_radial))
def stp():
    HLC.set_target(Target((0,0),0))
def shut_down():
    HLC.set_target(Target((0,0),0))
    HLC.low_level_interface.stop_loop()
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
    cont = False
    sleep(0.1)
    if not cont : HLC.set_target(Target((0,0),0))
    pass
