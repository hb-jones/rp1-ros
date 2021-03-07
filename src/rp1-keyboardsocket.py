from typing import no_type_check
from rp1controller import Target
import socket, pickle
import keyboard
from time import sleep


current_target = Target()
speed_linear = 2
speed_radial = 0.8
loop = True
cont = False

def fwd():
    cont = True
    current_target.local_velocity = (speed_linear,current_target.local_velocity[1])
def bck():
    cont = True
    current_target.local_velocity = (-speed_linear,current_target.local_velocity[1])
def lft():
    cont = True
    current_target.local_velocity = (current_target.local_velocity[0], -speed_linear)
def rgt():
    cont = True
    current_target.local_velocity = (current_target.local_velocity[0], speed_linear)
def rot_left():
    cont = True
    current_target.local_angular = -speed_radial
def rot_rgt():
    cont = True
    current_target.local_angular = speed_radial
def stp():
    current_target = Target()
def shut_down():
    current_target = Target()
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
IP_laptop = "192.168.137.1"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind((socket.gethostname(), 1066))
s.bind((IP_laptop, 1066))
s.listen(5)
clientsocket, address = s.accept()
print(f"Connection from {address} has been established.")
no_input_count = 0
while loop:
    
    cont = False
    if not cont: 
        no_input_count = no_input_count+1
        if no_input_count>20:
            current_target = Target()
    else:
        no_input_count = 0
    sleep(2)
    data = pickle.dumps(current_target)
    clientsocket.send(data)

