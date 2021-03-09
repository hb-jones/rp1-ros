from inputs import get_gamepad
from rp1controller import Target
import socket, pickle, threading
from time import sleep

IP_laptop = "192.168.137.1"

axis_FB = "ABS_Y"
axis_LR = "ABS_X"
axis_rot = "ABS_RX"
axis_deadzone = 5000

button_UP = "BTN_TR"
button_DN = "BTN_TL"
button_STP = "BTN_EAST"
button_BRK = "BTN_SOUTH"
button_MODE = "BTN_WEST"
button_RSTODOM = "BTN_NORTH"


speed_limit_rot = 1.2
speed_limit_linear = 1
speed_limit_step = 0.2

target_FB = 0
target_LR = 0
target_rot = 0

mode = "local"

running_flag = True

def curve(input):
    if input<0:
        sign = -1
    else:
        sign = 1
    output = ((0.05*20**abs(input))-0.05)*sign
    return output

def linear_FB(value: int):
    global target_LR, target_FB, target_rot
    if abs(value)<axis_deadzone: value = 0
    target_FB = curve(value/32000) * speed_limit_linear
    pass
def linear_LR(value: int):
    global target_LR, target_FB, target_rot
    if abs(value)<axis_deadzone: value = 0
    target_LR = curve(value/32000) * speed_limit_linear
    pass
def rotation(value: int):
    global target_LR, target_FB, target_rot
    if abs(value)<axis_deadzone: value = 0
    target_rot = curve(value/32000) * speed_limit_rot
    pass
def shift_speed_up():
    global speed_limit_linear
    speed_limit_linear = speed_limit_linear + speed_limit_step
    print(f"Speed limit is now {speed_limit_linear}m/s")
def shift_speed_dn():
    global speed_limit_linear
    if speed_limit_linear - speed_limit_step <0:
        speed_limit_linear = 0
    else:
        speed_limit_linear = speed_limit_linear - speed_limit_step
    print(f"Speed limit is now {speed_limit_linear}m/s")
def brake():
    global target_LR, target_FB, target_rot, speed_limit_linear
    target_FB = 0
    target_LR = 0
    target_rot = 0
    speed_limit_linear = speed_limit_step


def listen_to_gamepad():
    global running_flag
    while running_flag:
        events = get_gamepad()
        for event in events:
            if event.code == button_STP: #Emergency stop
                running_flag = False
                brake()
                return
            if event.code == axis_FB:
                linear_FB(event.state)
            if event.code == axis_LR:
                linear_LR(event.state)
            if event.code == axis_rot:
                rotation(event.state)
            if event.code == button_UP and event.state == 1:
                shift_speed_up()
            if event.code == button_DN and event.state == 1:
                shift_speed_dn()
            if event.code == button_BRK:
                brake()
            if event.code == button_MODE and event.state == 1:
                change_mode()
            if event.code == button_RSTODOM and event.state == 1:
                reset_odometry()

    return

def update_target()-> Target:
    target = Target((target_FB,target_LR),target_rot)
    target.world_velocity = (target_FB,target_LR)
    return target

def setup_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((IP_laptop, 1066))
    s.listen(5)
    global clientsocket
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established.")

def send_target(target: Target):
    data = pickle.dumps(target)
    clientsocket.send(data)

def change_mode():
    global mode
    if mode == "local": #TODO could be handled better
        mode = "world"
    else:
        mode = "local"
    data = pickle.dumps(mode) 
    clientsocket.send(data)
    return

def reset_odometry():
    data = pickle.dumps("reset")
    clientsocket.send(data)
    return

def main():
    setup_socket()
    gp_listen = threading.Thread(target=listen_to_gamepad)
    gp_listen.start()
    while running_flag:
        sleep(0.05) #Needs to be at the start of loop so exit is handled gracefully 
        target = update_target()
        send_target(target)

        

if __name__ == "__main__":
    main()