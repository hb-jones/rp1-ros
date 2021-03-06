from typing import no_type_check
from rp1controller import Target
import socket, pickle, threading
import keyboard
import time
from time import sleep


current_target = Target()

speed_linear = 0.5
speed_radial = 0.8
loop = True
cont = False

time_last = time.time()



def send_target(target: Target):
    data = pickle.dumps(target)
    clientsocket.send(data)
    time_last = time.time()

def reset_target():
    while(True):
        if ((time.time()-time_last)>0.2):
            target = Target()
            data = pickle.dumps(current_target)
            clientsocket.send(data)

def fwd():
    cont = True
    current_target = Target()
    current_target.local_velocity = (speed_linear,current_target.local_velocity[1])
    data = pickle.dumps(current_target)
    clientsocket.send(data)
def bck():
    cont = True
    current_target = Target()
    current_target.local_velocity = (-speed_linear,current_target.local_velocity[1])
    data = pickle.dumps(current_target)
    clientsocket.send(data)
def lft():
    cont = True
    current_target = Target()
    current_target.local_velocity = (current_target.local_velocity[0], -speed_linear)
    data = pickle.dumps(current_target)
    clientsocket.send(data)
def rgt():
    cont = True
    current_target = Target()
    current_target.local_velocity = (current_target.local_velocity[0], speed_linear)
    data = pickle.dumps(current_target)
    clientsocket.send(data)
def rot_left():
    cont = True
    current_target = Target()
    current_target.local_angular = -speed_radial
    data = pickle.dumps(current_target)
    clientsocket.send(data)
def rot_rgt():
    cont = True
    current_target = Target()
    current_target.local_angular = speed_radial
    data = pickle.dumps(current_target)
    clientsocket.send(data)
def stp():
    current_target = Target()
    data = pickle.dumps(current_target)
    clientsocket.send(data)
def shut_down():
    current_target = Target()
    data = pickle.dumps(current_target)
    clientsocket.send(data)
    loop = False

def speed_up():
    global speed_linear
    speed_linear = speed_linear+0.5
    print("Speed is {}".format(speed_linear))
def speed_dn():
    global speed_linear
    speed_linear = speed_linear-0.5
    print("Speed is {}".format(speed_linear))

    

keyboard.add_hotkey('w', fwd)
keyboard.add_hotkey('s', bck)
keyboard.add_hotkey('a', lft)
keyboard.add_hotkey('d', rgt)
keyboard.add_hotkey('q', rot_left)
keyboard.add_hotkey('e', rot_rgt)
keyboard.add_hotkey(' ', stp)
keyboard.add_hotkey('r', stp)
keyboard.add_hotkey('t', shut_down)
keyboard.add_hotkey(']', speed_up)
keyboard.add_hotkey('[', speed_dn)

IP_laptop = "192.168.137.1"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind((socket.gethostname(), 1066))
s.bind((IP_laptop, 1066))
s.listen(5)
clientsocket, address = s.accept()
print(f"Connection from {address} has been established.")
no_input_count = 0
while True:
    pass
while loop:
    pass
    cont = False
    if not cont: 
        no_input_count = no_input_count+1
        if no_input_count>200:
            current_target = Target()
    else:
        no_input_count = 0
    sleep(0.01)
    data = pickle.dumps(current_target)
    clientsocket.send(data)

