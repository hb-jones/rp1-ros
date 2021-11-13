from rp1controller import RP1Client
from rp1controller.trajectory_planners import Target, WorldPoseControl
import rp1controller, time
from rp1_full_client import update_terminal_target
from vision import monocular
ip = "192.168.137.1"
terminal_gain = 2 #TODO make sure to check command is within limit
delay = 0.1

max_dist = 1.4 #TODO this is the max distance the robot can move from origin during terminal phase
camera = None
coords = (0,0) #Normalised camera coords
updated = False

def update_camera_coords(cam):
    global coords, updated
    coords = cam.norm_coords
    updated = True

def main():
    print()

    print("Starting camera")
    global camera 
    camera = monocular.Monocular(update_camera_coords,"norm_coord")

    print("Sarting robot")
    HLC = rp1controller.RP1Controller()
    HLC.set_trajectory_planner(WorldPoseControl)
    while(True):
        update_terminal_target(HLC)
        time.sleep(1)

if __name__ == "__main__":
    main()