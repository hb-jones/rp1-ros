from inputs import get_gamepad
from rp1controller import Target
import socket, pickle, threading
from time import sleep

IP_laptop = "192.168.137.1"

axis_FB = "ABS_Y"
axis_LR = "ABS_X"
axis_rot = "ABS_RX"
axis_deadzone = 0.2

button_UP = "BTN_TR"
button_DN = "BTN_TL"
button_STP = "BTN_EAST"
button_BRK = "BTN_SOUTH"
button_MODE = "BTN_WEST"
button_RSTODOM = "BTN_NORTH"

button_PRP = "ABS_HAT0Y"
state_PRP_UP = -1
state_PRP_DN = 1

button_INT = "ABS_HAT0X"
state_INT_UP = 1
state_INT_DN = -1

vel_gain = 0.004
vel_integrator_gain = 0.021


speed_limit_rot = 1
speed_limit_linear = 1
speed_limit_step = 0.2

target_FB = 0
target_LR = 0
target_rot = 0

mode = "local"

running_flag = True

#course = [(0,0),(2,0),(2,-0.5),(0,-0.5),(0,0),(1,-0.5)]
course = [(0,0),(4,0),(2,0),(1.5,-0.5),(1,0)]
course_index = 0

def curve(input):
    input = input/32000
    if input<0:
        sign = -1
    else:
        sign = 1
    input_unsigned = abs(input)
    if input_unsigned<axis_deadzone:
        output_unsigned = 0
    else:
        output_unsigned = input_unsigned*1/(1-axis_deadzone)-axis_deadzone
    #output_unsigned = ((0.1*20**(abs(input)-axis_deadzone))-0.1) Old buggy curve
    if output_unsigned >1: output_unsigned = 1
    output = output_unsigned*sign
    return output

def linear_FB(value: int):
    global target_LR, target_FB, target_rot
    target_FB = curve(value) * speed_limit_linear
    pass
def linear_LR(value: int):
    global target_LR, target_FB, target_rot
    target_LR = curve(-value) * speed_limit_linear
    pass
def rotation(value: int):
    global target_LR, target_FB, target_rot
    target_rot = curve(-value) * speed_limit_rot
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


def update_PID(parameter, increase):
    global vel_gain, vel_integrator_gain
    if parameter == "proportional":
        if increase:
            vel_gain = vel_gain * 1.1
        else:
            vel_gain = vel_gain * 0.9
    if parameter == "integrator":
        if increase:
            vel_integrator_gain = vel_integrator_gain * 1.1
        else:
            vel_integrator_gain = vel_integrator_gain * 0.9
    print(f"PID updated to:\nvel_gain: {vel_gain}\nvel_integrator_gain: {vel_integrator_gain}\n")
    pid_config = {"vel_gain": vel_gain, "vel_integrator_gain": vel_integrator_gain}
    data = pickle.dumps(pid_config)
    clientsocket.send(data)
    

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
                #reset_odometry()
                advance_course()
            if event.code == button_PRP:
                if event.state == state_PRP_UP:
                    update_PID("proportional", True) 
                elif event.state == state_PRP_DN:
                    update_PID("proportional", False) 
            if event.code == button_INT:
                if event.state == state_INT_UP:
                    update_PID("integrator", True) 
                elif event.state == state_INT_DN:
                    update_PID("integrator", False) 
            

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
    elif mode == "world":
        mode = "pose"
    else:
        mode = "local"
    print(f"Mode is currently: {mode}")

    data = pickle.dumps(mode) 
    clientsocket.send(data)
    return

def reset_odometry():
    data = pickle.dumps("reset")
    clientsocket.send(data)
    return

def advance_course():
    if mode != "pose":
        return
    global course_index, course
    course_index += 1
    if course_index >= len(course):
        course_index = 0
    print(f"Moving to position: {course_index} at: {course[course_index]}")
    target = Target()
    target.world_bearing = 0
    target.world_point = course[course_index]
    send_target(target)
    

def main():
    setup_socket()
    gp_listen = threading.Thread(target=listen_to_gamepad)
    gp_listen.start()
    while running_flag:
        sleep(0.05) #Needs to be at the start of loop so exit is handled gracefully 
        if mode != "pose":
            target = update_target()
            send_target(target)
        else:
            data = pickle.dumps("watchdog") 
            clientsocket.send(data)

        

if __name__ == "__main__":
    main()