from rp1controller import Target
from rp1controller.trajectory_planners import LocalVelocityControl, WorldVelocityControl
import rp1controller
import socket, pickle
import rp1controller
import time, threading


IP_laptop = "192.168.137.1"

def reset_target():
    global time_last
    while(True):
        delay = time.time()-time_last
        if ((delay)>2 and not first):
            print(f"Reset {delay} at {time.time()}")
            target = Target()
            HLC.set_target(target)
            time_last = time.time()


target = Target()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((socket.gethostname(), 1066))
s.connect((IP_laptop, 1066))
HLC = rp1controller.RP1Controller()

time_last = time.time()
watchdog = threading.Thread(target=reset_target)
watchdog.start()
first = True

while True:
    msg = s.recv(1024)
    time_last = time.time()
    try: 
        target = pickle.loads(msg)
    except:
        target = Target()
    
    if target == "local":
        planner = LocalVelocityControl(HLC)
        HLC.set_trajectory_planner(planner)
    elif target == "world":
        planner = WorldVelocityControl(HLC)
        HLC.set_trajectory_planner(planner)
    elif target == "reset":
        HLC.localisation.reset_localisation()
    else:
        first = False
        HLC.set_target(target)