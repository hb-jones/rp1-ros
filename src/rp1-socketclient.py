from rp1controller.odometry_system import VelocityPose
from rp1controller import Target
from rp1controller.trajectory_planners import LocalVelocityControl, WorldVelocityControl, WorldPoseControl
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


data = Target()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((socket.gethostname(), 1066))
s.connect((IP_laptop, 1066))
HLC = rp1controller.RP1Controller()

time_last = time.time()
#watchdog = threading.Thread(target=reset_target)
#watchdog.start() #TODO reenable
first = True

while True:
    msg = s.recv(1024)
    time_last = time.time()
    try: 
        data = pickle.loads(msg)
    except:
        data = Target()
    if data == "watchdog":
        pass
    elif data == "local":
        planner = LocalVelocityControl(HLC)
        HLC.set_trajectory_planner(planner)
    elif data == "world":
        planner = WorldVelocityControl(HLC)
        HLC.set_trajectory_planner(planner)
    elif data == "pose":
        planner = WorldPoseControl(HLC)
        HLC.set_trajectory_planner(planner)
    elif data == "reset":
        HLC.localisation.reset_localisation()
    elif data == "odom_report":
        odom: VelocityPose = HLC.localisation.current_pose
        if odom == None:
            send_data = pickle.dumps("Bad Odom")
        else:
            send_data = pickle.dumps(odom)
        s.send(send_data)
    elif type(data) == dict:
        if data["vel_gain"] != None and data["vel_integrator_gain"] != None:
            HLC.config.vel_gain = data["vel_gain"]
            HLC.config.vel_integrator_gain = data["vel_integrator_gain"]
            HLC.low_level_interface.update_configuration()
        else:
            print("invalid confit dictionary")
    else:
        first = False
        HLC.set_target(data)