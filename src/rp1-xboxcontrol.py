from inputs import get_gamepad
from rp1controller import Target
import socket, pickle, threading
from time import sleep

IP_laptop = "192.168.137.1"

axis_FB = "ABS_Y"
axis_LR = "ABS_X"
axis_rot = "ABS_RX"

button_UP = "BTN_TR"
button_DN = "BTN_TL"
button_STP = "BTN_EAST"
button_BRK = "BTN_SOUTH"

speed_limit_rot = 1.2
speed_limit_linear = 1
speed_limit_step = 0.5

target_FB = 0
target_LR = 0
target_rot = 0

running_flag = True

def linear_FB(value: int):
    global target_LR, target_FB, target_rot
    target_FB = (value/32000) * speed_limit_linear
    pass
def linear_LR(value: int):
    global target_LR, target_FB, target_rot
    target_LR = (value/32000) * speed_limit_linear
    pass
def rotation(value: int):
    global target_LR, target_FB, target_rot
    target_rot = (value/32000) * speed_limit_rot
    pass
def shift_speed_up():
    global speed_limit_linear
    speed_limit_linear = speed_limit_linear + speed_limit_step
def shift_speed_dn():
    global speed_limit_linear
    if speed_limit_linear - speed_limit_step <0:
        speed_limit_linear = 0
    else:
        speed_limit_linear = speed_limit_linear - speed_limit_step
def brake():
    global target_LR, target_FB, target_rot, speed_limit_linear
    target_FB = 0
    target_LR = 0
    target_rot = 0
    speed_limit_linear = 0.5


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
    return

def update_target()-> Target:
    target = Target((target_FB,target_LR),target_rot)
    return target

def setup_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((IP_laptop, 1066))
    s.listen(5)
    global clientsocket
    clientsocket, address = s.accept()

def send_target(target: Target):
    data = pickle.dumps(target)
    clientsocket.send(data)



def main():
    setup_socket()
    gp_listen = threading.Thread(target=listen_to_gamepad)
    gp_listen.start()
    while running_flag:
        sleep(0.05) #Needs to be at the start of loop so exit is handled gracefully 
        target = update_target()
        send_target(target)

        





def main_old():
    while 1:
        events = get_gamepad()
        print("New Loop")
        for event in events:
            if event.ev_type == "Sync":
                continue
            print("Event Type:  {}".format(event.ev_type))
            print("Event Code:  {}".format(event.code))
            print("Event State: {}".format(event.state))
            print()


if __name__ == "__main__":
    main()