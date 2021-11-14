from rp1controller import RP1Client
from rp1controller.trajectory_planners import Target, WorldPoseControl
import rp1controller, time
from rp1_full_client import update_terminal_target, update_camera_coords,coords, updated, terminal_gain_x, terminal_gain_y, max_dist, target_point
from vision import monocular

def main():
    print()

    print("Starting camera")
    global camera 
    camera = monocular.Monocular(update_camera_coords,"norm_coord")

    print("Sarting robot")
    HLC = rp1controller.RP1Controller()
    HLC.config.acceleration_max = 0.5
    HLC.config.linear_velocity_max = 0.5
    HLC.set_trajectory_planner(WorldPoseControl)
    while(True):
        update_terminal_target(HLC)
        time.sleep(0.1)

if __name__ == "__main__":
    main()